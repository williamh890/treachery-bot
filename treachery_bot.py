import discord
from discord.ext import commands
import pathlib

import treachery


class TreacheryGameState:
    def __init__(self):
        self.players = []
        self.role_deck = treachery.RoleDeck()
        self.current_roles = None

    def set_players(self, players):
        self.players = players

    def add_players(self, new_players):
        current_players = set(player.name for player in self.players)

        for new_player in new_players:
            if new_player.name in current_players:
                continue

            self.players.append(new_player)

    def remove_players(self, players_to_remove):
        to_remove = set(player.name for player in players_to_remove)
        self.players = [p for p in self.players if p.name not in to_remove]

    def deal(self):
        self.current_roles = self.deal([player.name for player in self.players])

        return self.current_roles

    def shuffle(self):
        self.role_deck.shuffle()

    @property
    def players_status_msg(self):
        if not self.players:
            msg = 'No treach gamers :('
        else:
            names = ", ".join(player.name for player in self.players)
            msg = f"Treachery Gamers: {names}"

        return msg


STATE = TreacheryGameState()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='_', intents=intents)


@bot.event
async def on_ready():
    print(f'bot online: {bot.user.name}')


@bot.command()
async def players(ctx):
    global STATE
    new_players = ctx.message.mentions

    if new_players:
        STATE.set_players(new_players)

    msg = STATE.players_status_msg
    await ctx.send(msg)


@bot.command()
async def add(ctx):
    global STATE
    new_players = ctx.message.mentions

    if not new_players:
        new_players = [ctx.author]

    STATE.add_players(new_players)

    msg = STATE.players_status_msg
    await ctx.send(msg)


@bot.command()
async def remove(ctx):
    global STATE
    players_to_remove = ctx.message.mentions

    if not players_to_remove:
        players_to_remove = [ctx.author]

    STATE.remove_players(players_to_remove)

    msg = STATE.players_status_msg
    await ctx.send(msg)


@bot.command()
async def deal(ctx):
    global STATE

    if not STATE.players:
        await ctx.send('Yo, you need players dude.')
        return

    player_roles = STATE.deal()

    for player in STATE.players:
        role = player_roles[player.name]
        image = treachery.card_image(role)

        await player.send(image)

    roles = [role['types']['subtype'] for role in player_roles.values()]
    msg = f'Dealt out {len(roles)} roles: {", ".join(roles)}'

    await ctx.send(msg)


@bot.command()
async def shuffle(ctx):
    global STATE
    STATE.shuffle()

    msg = 'Role deck has been reshuffled'
    await ctx.send(msg)


@bot.command()
async def deck(ctx):
    global STATE
    await ctx.send(str(STATE.role_deck))


@bot.command()
async def reset(ctx):
    global STATE

    STATE = TreacheryGameState()

    msg = 'Reset players and role deck'
    await ctx.send(msg)


def run():
    token = pathlib.Path('token.txt').read_text()
    bot.run(token)


if __name__ == '__main__':
    run()
