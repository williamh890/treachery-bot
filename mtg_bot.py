import discord
import urllib
import requests
import json
from discord.ext import commands
import pathlib

DATA_PATH = pathlib.Path(__file__).parent / 'data'
PLAYERS = []

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='tre_', intents=intents)


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
        msg = 'No trech gamers :('
    else:
        names = ", ".join(player.name for player in PLAYERS)
        msg = f"Trechery Gamers: {names}"

    return msg


@bot.command()
async def deal(ctx):
    if not players:
        await ctx.send('Yo, you need players dude.')
        return

    for player in players:
        await player.send('ur playin')


@bot.command()
async def shuffle(ctx):
    pass


@bot.command()
async def reset(ctx):
    pass


def run():
    token = pathlib.Path('token.txt').read_text()
    bot.run(token)


def load_trechery_cards():
    with pathlib.Path('cards.json').open("r") as f:
        cards = json.load(f)

    for card in cards['cards']:
        download_image(card)

    return cards


def download_image(card):
    url_encoded = urllib.parse.quote(f'{card["id"]:03} - {card["types"]["subtype"]} - {card["name"]}.jpg')
    url = f'https://mtgtreachery.net/images/cards/en/trd/{url_encoded}'
    resp = requests.get(url)

    with (DATA_PATH / 'card-images' / f"{card['name']}.jpg").open('wb') as f:
        print(f'downloaded {card["name"]}')
        f.write(resp.content)


if __name__ == '__main__':
    run()
