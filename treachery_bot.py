import discord
from discord.ext import commands
import pathlib

import treachery
import game_state


STATE = game_state.TreacheryGameState()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='_', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot online: {bot.user.name}')


@bot.command()
async def players(ctx):
    global STATE
    new_players = ctx.message.mentions

    if new_players:
        msg = STATE.set_players(new_players)
    else:
        msg = STATE.players_status_msg

    await ctx.send(msg)


@bot.command()
async def add(ctx):
    global STATE
    new_players = ctx.message.mentions

    if not new_players:
        new_players = [ctx.author]

    msg = STATE.add_players(new_players)

    await ctx.send(msg)


@bot.command()
async def remove(ctx):
    global STATE
    players_to_remove = ctx.message.mentions

    if not players_to_remove:
        players_to_remove = [ctx.author]

    msg = STATE.remove_players(players_to_remove)

    await ctx.send(msg)


@bot.command()
async def deal(ctx):
    global STATE

    if not STATE.players:
        await ctx.send('Yo, you need players dude.')
        return

    player_msgs, game_msg = STATE.deal()

    for player in STATE.players:
        player_msg = player_msgs[player.name]
        await player.send(player_msg)

    await ctx.send(game_msg)


@bot.command()
async def shuffle(ctx):
    global STATE
    msg = STATE.shuffle()

    await ctx.send(msg)


@bot.command()
async def deck(ctx):
    global STATE
    await ctx.send(str(STATE.role_deck))


class WearerOfMasksView(discord.ui.View):
    def __init__(self, cards, author: discord.User):
        super().__init__()  # stop after 30s if no click
        self.value = None  # store chosen option
        self.author = author

        for card in cards:
            style = {
                'Traitor': discord.ButtonStyle.grey,
                'Assassin': discord.ButtonStyle.red,
                'Guardian': discord.ButtonStyle.primary
            }[card['types']['subtype']]

            button = discord.ui.Button(label=card['name'], style=style)
            button.callback = self.make_callback(button)
            self.add_item(button)

    def make_callback(self, button):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.author:
                await interaction.response.send_message("Not your buttons!", ephemeral=True)
                return

            self.value = button.label

            for btn in self.children:
                btn.disabled = True
            await interaction.message.edit(view=self)

            await interaction.response.send_message(f"You picked **{button.label}**!", ephemeral=True)
            self.stop()

        return callback


@bot.command()
async def masks(ctx):
    global STATE

    command_msg = ctx.message.content.strip('_masks')
    try:
        x = int(command_msg)
    except ValueError:
        await ctx.send('No value for X found in command.')
        return

    cards = STATE.wearer_of_masks(x)

    url_msg = ''
    for card in cards:
        url = treachery.card_image(card)

        if len(url_msg) + len(url) + 1 >= 2000:
            await ctx.send(f'{url_msg}')
            url_msg = ''

        url_msg += f'{url}\n'

    if len(cards) > 25:
        await ctx.send('Too many cards to use buttons.')
        return

    view = WearerOfMasksView(cards, ctx.author)
    await ctx.send('Pick a non-leader card to copy:', view=view)

    await view.wait()


@bot.command()
async def puppet(ctx):
    global STATE
    msg_command = ctx.message.content.strip('_puppet')

    if not msg_command:
        player_roles_msg = STATE.player_roles_msg(ctx.author.name)

        await ctx.author.send(player_roles_msg)
        return

    new_role_msgs = STATE.puppet_master(msg_command)

    for player in STATE.players:
        player_msg = new_role_msgs[player.name]
        await player.send(player_msg)


@bot.command()
async def reset(ctx):
    global STATE

    STATE = game_state.TreacheryGameState()

    msg = 'Reset players and role deck'
    await ctx.send(msg)


def run():
    token = pathlib.Path('token.txt').read_text()
    bot.run(token)


if __name__ == '__main__':
    run()
