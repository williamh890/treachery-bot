import discord
from discord.ext import commands
import pathlib

import treachery

PLAYERS = []

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
        return

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
        return

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
    global PLAYERS

    if not players:
        await ctx.send('Yo, you need players dude.')
        return

    player_roles = treachery.deal_role_cards([player.name for player in PLAYERS])
    for player in PLAYERS:
        role = player_roles[player.name]
        image = treachery.card_image(role)

        await player.send(image)


@bot.command()
async def shuffle(ctx):
    pass


@bot.command()
async def reset(ctx):
    pass


def run():
    token = pathlib.Path('token.txt').read_text()
    bot.run(token)


if __name__ == '__main__':
    run()
