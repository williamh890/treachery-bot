import discord
import asyncio
from discord.ext import commands
import pathlib

import treachery
import game_state


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='_', intents=intents)


class WearerOfMasksView(discord.ui.View):
    def __init__(self, cards, author: discord.User):
        super().__init__(timeout=None)
        self.value = None
        self.author = author

        for card in cards:
            role = card['types']['subtype']
            style = {
                'Traitor': discord.ButtonStyle.grey,
                'Assassin': discord.ButtonStyle.red,
                'Guardian': discord.ButtonStyle.primary,
            }[role]

            button = discord.ui.Button(label=card['name'], style=style)
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


class TreacheryCog(commands.Cog, name='Treachery'):
    """Game commands for Treachery"""

    def __init__(self, bot):
        self.bot = bot
        self.state = game_state.TreacheryGameState()

    @commands.command(help='Set players or list all players')
    async def players(self, ctx):
        new_players = ctx.message.mentions

        if new_players:
            msg = self.state.set_players(new_players)
        else:
            msg = self.state.players_status_msg

        await ctx.send(msg)

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
            else:
                message = await player.send(msg)
                self.state.deal_messages.add(message.id)
                await message.add_reaction('game_dice')

        await self.state.game_channel.send(game_msg)

    @commands.command(help='Reroll a delt out role card')
    async def reroll(self, ctx):
        player = ctx.author

        await self._reroll_player(player)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id in self.state.deal_messages and reaction.emoji == 'game_dice':
            await self._reroll_player(user)

    async def _reroll_player(self, player):
        if (err_msg := self.state.can_player_reroll(player)):
            await player.send(err_msg)
            return

        new_role_msg = self.state.reroll(player)

        await self.state.game_channel.send(f'{player.name} just used their reroll for the night')
        await player.send(new_role_msg)


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

    @commands.command(help='The Puppet Master card')
    async def puppet(self, ctx, *, arg: str = None):
        if not arg:
            player_roles_msg = self.state.player_roles_msg(ctx.author.name)
            await ctx.author.send(player_roles_msg)
            return

        new_role_msgs = self.state.puppet_master(arg)
        for player in self.state.players:
            await player.send(new_role_msgs[player.name])

    @commands.command(help='Reset treachery game state')
    async def reset(self, ctx):
        self.state = game_state.TreacheryGameState()
        await ctx.send('Reset players and role deck')


@bot.event
async def on_ready():
    print(f'✅ Bot online: {bot.user.name}')


def run():
    async def main():
        await bot.add_cog(TreacheryCog(bot))
        token = pathlib.Path('token.txt').read_text().strip()
        await bot.start(token)

    asyncio.run(main())


if __name__ == '__main__':
    run()
