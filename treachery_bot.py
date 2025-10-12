import discord
from discord.ext import commands
import pathlib

import treachery

PLAYERS = []
ROLE_DECK = treachery.RoleDeck()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='_', intents=intents)


@bot.event
async def on_ready():
    print(f'bot online: {bot.user.name}')


@bot.command()
async def players(ctx):
    global PLAYERS
    new_players = ctx.message.mentions

    if new_players:
        PLAYERS = new_players

    msg = _players_status_msg(PLAYERS)
    await ctx.send(msg)


@bot.command()
async def add(ctx):
    global PLAYERS
    new_players = ctx.message.mentions

    if not new_players:
        new_players = [ctx.author]

    current_players = set(player.name for player in PLAYERS)

    for new_player in new_players:
        if new_player.name in current_players:
            continue

        PLAYERS.append(new_player)

    msg = _players_status_msg(PLAYERS)
    await ctx.send(msg)


@bot.command()
async def remove(ctx):
    global PLAYERS
    players_to_remove = ctx.message.mentions

    if not players_to_remove:
        players_to_remove = [ctx.author]

    to_remove = set(player.name for player in players_to_remove)
    PLAYERS = [p for p in PLAYERS if p.name not in to_remove]

    msg = _players_status_msg(PLAYERS)
    await ctx.send(msg)


def _players_status_msg(players):
    if not PLAYERS:
        msg = 'No treach gamers :('
    else:
        names = ", ".join(player.name for player in PLAYERS)
        msg = f"Treachery Gamers: {names}"

    return msg


@bot.command()
async def deal(ctx):
    global PLAYERS, ROLE_DECK

    if not players:
        await ctx.send('Yo, you need players dude.')
        return

    player_roles = ROLE_DECK.deal([player.name for player in PLAYERS])

    for player in PLAYERS:
        role = player_roles[player.name]
        image = treachery.card_image(role)

        await player.send(image)

    roles = [role['types']['subtype'] for role in player_roles.values()]
    msg = f'Dealt out {len(roles)} roles: {", ".join(roles)}'

    await ctx.send(msg)


@bot.command()
async def shuffle(ctx):
    global ROLE_DECK
    ROLE_DECK.shuffle()

    msg = 'Role deck has been reshuffled'
    await ctx.send(msg)


@bot.command()
async def deck(ctx):
    global ROLE_DECK

    await ctx.send(str(ROLE_DECK))


@bot.command()
async def reset(ctx):
    global PLAYERS, ROLE_DECK

    PLAYERS = []
    ROLE_DECK = treachery.RoleDeck()

    msg = 'Reset players and role deck'
    await ctx.send(msg)


def run():
    token = pathlib.Path('token.txt').read_text()
    bot.run(token)


if __name__ == '__main__':
    run()
