import discord
import datetime
import asyncio
from discord.ext import commands
import pathlib
import os

import treachery
import game_state
import spreadsheet

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='_', intents=intents)


class PlayerEditSelect(discord.ui.UserSelect):
    def __init__(self, cog):
        super().__init__(
            placeholder='Select current players',
            min_values=0,
            max_values=10,
        )
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        self.cog.state.remove_players(self.cog.state.players.copy())

        added = []
        for member in self.values:
            if member.bot:
                continue
            self.cog.state.add_players([member])
            added.append(member.display_name)

        msg = self.cog.state.players_status_msg
        if added:
            msg += f'\nSelected: {", ".join(added)}'

        await interaction.response.send_message(content=msg, view=PlayerManagementView(self.cog), ephemeral=False)


class PlayerManagementView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)  # session-long view
        self.cog = cog

        # Pre-select current players in dropdown
        default_members = [p for p in cog.state.players if isinstance(p, discord.Member)]
        select = PlayerEditSelect(cog)
        select.default = default_members
        self.add_item(select)


class WearerOfMasksView(discord.ui.View):
    def __init__(self, cards, author: discord.User):
        super().__init__(timeout=None)
        self.value = None
        self.author = author

        for card in cards:
            role = card.role
            style = {
                'Traitor': discord.ButtonStyle.grey,
                'Assassin': discord.ButtonStyle.red,
                'Guardian': discord.ButtonStyle.primary,
            }[role]

            button = discord.ui.Button(label=card.name, style=style)
            button.callback = self.make_callback(button)

            self.add_item(button)

    def make_callback(self, button):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.author:
                await interaction.response.send_message('Not your buttons!', ephemeral=True)
                return

            self.value = button.label

            for btn in self.children:
                btn.disabled = True

            await interaction.message.edit(view=self)
            await interaction.response.send_message(f'You picked **{button.label}**!', ephemeral=True)
            self.stop()

        return callback


class TreacheryCog(commands.Cog, name='Treachery Bot'):
    """Game commands for Treachery"""

    def __init__(self, bot):
        self.bot = bot
        self.state = game_state.TreacheryGameState()
        self.game_start_time = None
        self.game_notes = {}

    @commands.group(invoke_without_command=True, help='Manage players via a dropdown')
    async def players(self, ctx):
        view = PlayerManagementView(self)

        await ctx.send(content=self.state.players_status_msg, view=view)

    @players.command(aliases=['list', 'l'], help='Set players or list all players')
    async def list_players(self, ctx):
        new_players = ctx.message.mentions

        if new_players:
            msg = self.state.set_players(new_players)
        else:
            msg = self.state.players_status_msg

        await ctx.send(msg)

        self.player_ui_message: discord.Message | None = None

    @commands.command(help='Add player(s) to the game')
    async def add(self, ctx):
        new_players = ctx.message.mentions or [ctx.author]
        msg = self.state.add_players(new_players)

        await ctx.send(msg)

    @commands.command(help='Remove player(s) from the game')
    async def remove(self, ctx):
        players_to_remove = ctx.message.mentions or [ctx.author]
        msg = self.state.remove_players(players_to_remove)

        await ctx.send(msg)

    @commands.command(help='Alias for remove')
    async def drop(self, ctx):
        players_to_remove = ctx.message.mentions or [ctx.author]
        msg = self.state.remove_players(players_to_remove)

        await ctx.send(msg)

    @commands.command(help='Deal out role cards to current players')
    async def deal(self, ctx):
        if not self.state.players:
            await ctx.send('Yo, you need players dude.')
            return

        leader = ctx.message.mentions
        if not leader:
            await ctx.send('Yo, you need to select a leader.')
            return

        if len(leader) > 2:
            await ctx.send('Yo, there can only be one leader.')
            return

        leader_player = leader.pop()

        player_msgs, game_msg = self.state.deal(leader_player)
        self.state.game_channel = ctx.channel
        self.state.deal_messages = set()

        for player in self.state.players:
            msg = player_msgs[player.name]

            if player.name == leader_player.name:
                await self.state.game_channel.send(msg)

            message = await player.send(msg)
            self.state.deal_messages.add(message.id)

        leader_msg = await self.state.game_channel.send(game_msg)
        await leader_msg.add_reaction('🎲')

        self.game_start_time = datetime.datetime.now()
        self.game_notes = {}

    @commands.command(aliases=['notes', 'n'], help='Make a note on the game before _winners and after _deal')
    async def note(self, ctx, *, arg: str = None):
        player_name = ctx.author.name
        if not arg:
            await ctx.send('No note passed...')
            return

        self.game_notes[player_name] = arg
        await ctx.send(f'Added to game notes for {ctx.author.name}: {arg}')

    @commands.command(
        help='Log game winners: either winning role [(a)ssassin, (l)eader, (t)raitor] or mention list of winners'
    )
    async def winners(self, ctx, *, arg: str = None):
        if self.state.current_roles is None:
            await ctx.send('You gotta deal before you can win...')
            return

        if ctx.message.mentions:
            winners = [user.name for user in ctx.message.mentions]

        elif arg:
            role_type = arg.strip().lower()
            print(role_type)

            if role_type in ('assassin', 'a'):
                winning_role = ('assassin',)
            elif role_type in ('traitor', 't'):
                winning_role = ('traitor',)
            elif role_type in ('leader', 'l', 'guardian', 'g'):
                winning_role = ('leader', 'guardian')
            else:
                await ctx.send(f"Can't determine winners for {role_type}")
                return

            winners = [player for player, role in self.state.current_roles.items() if role.role.lower() in winning_role]

        if winners:
            try:
                spreadsheet.log_game(winners, self.state.current_roles, self.game_start_time, self.game_notes)
                await ctx.send(f'Winners: {", ".join(winners)}')
            except Exception as e:
                await ctx.send(f'Error logging game: {e}')
            else:
                self.game_start_time = None

        else:
            await ctx.send('No winners found for that filter.')

    @commands.command(help='Reroll a delt out role card (only once per session)')
    async def reroll(self, ctx):
        try:
            await self._handle_reroll(ctx.author)
        except Exception as e:
            await ctx.send(f'Error rerolling: {e}')

    @commands.command(help='Shuffle the role deck')
    async def shuffle(self, ctx):
        msg = self.state.shuffle()
        await ctx.send(msg)

    @commands.command(help='Return the state of the role deck')
    async def deck(self, ctx):
        msg = str(self.state.role_deck)
        await ctx.send(msg)

    @commands.command(help='The Wearer of Masks card')
    async def masks(self, ctx, x: int = None):
        if x is None:
            await ctx.send('You need to specify a number for X.')
            return

        cards = self.state.wearer_of_masks(x)
        url_msg = ''

        for card in cards:
            url = treachery.card_image(card)
            if len(url_msg) + len(url) + 1 >= 2000:
                await ctx.send(url_msg)
                url_msg = ''
            url_msg += f'{url}\n'

        if url_msg:
            await ctx.send(url_msg)

        if len(cards) > 25:
            await ctx.send('Too many cards to use buttons.')
            return

        view = WearerOfMasksView(cards, ctx.author)
        await ctx.send('Pick a non-leader card to copy:', view=view)
        await view.wait()

    @commands.group(invoke_without_command=True, help='Reset treachery game state')
    async def reset(self, ctx):
        self.state = game_state.TreacheryGameState()

        failed_to_load = self.state.role_deck.custom_cards_failed
        if failed_to_load:
            await ctx.send('Failed to load custom cards: {failed_to_load}')

        await ctx.send('Reset players and role deck')

    @reset.command(aliases=['c', 'custom'], help='Reset rerolls')
    async def rerolls(self, ctx):
        msg = self.state.reset_rerolls()

        await ctx.send(msg)

    @commands.command(help='Link to google sheet with game stats')
    async def stats(self, ctx):
        await ctx.send(
            'https://docs.google.com/spreadsheets/d/1YxECCYDunuARaCrhFI5ooKukV-0pi4RqOpU_tadNHAA/edit?gid=1644267183#gid=1644267183'
        )

    async def _handle_reroll(self, user):
        if err_msg := self.state.can_player_reroll(user):
            await user.send(err_msg)
            return

        old_roll = self.state.current_roles[user.name]

        try:
            new_role_msg = self.state.reroll(user)
        except Exception as e:
            await user.send(f'ERROR REROLLING: {e}')
            return

        await user.send(new_role_msg)
        await self.state.game_channel.send(f'{user.name} just used their reroll for the night')

        spreadsheet.log_reroll(old_roll, user.name)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if str(reaction.emoji) != '🎲':
            return

        await self._handle_reroll(user)


@bot.event
async def on_ready():
    print(f'✅ Bot online: {bot.user.name}')


def run():
    async def main():
        await bot.add_cog(TreacheryCog(bot))
        TOKEN = os.getenv('DISCORD_TOKEN')
        if not TOKEN:
            TOKEN = pathlib.Path('token.txt').read_text().strip()
        await bot.start(TOKEN)

    asyncio.run(main())


if __name__ == '__main__':
    run()
