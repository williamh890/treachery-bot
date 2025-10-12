import requests
import random
import json
from collections import defaultdict
import pathlib
import urllib

DATA_PATH = pathlib.Path(__file__).parent / 'data'


def load_treachery_cards():
    with pathlib.Path('cards.json').open("r") as f:
        cards = json.load(f)

    return cards['cards']


def get_cards_by_role(cards):
    by_role = defaultdict(list)

    for card in cards:
        by_role[card['types']['subtype']].append(card)

    return by_role


ALL_CARDS = load_treachery_cards()
CARDS_BY_ROLE = get_cards_by_role(ALL_CARDS)


def card_image(card):
    url_encoded = urllib.parse.quote(f'{card["id"]:03} - {card["types"]["subtype"]} - {card["name"]}.jpg')
    url = f'https://mtgtreachery.net/images/cards/en/trd/{url_encoded}'

    return url


def download_image(card, url):
    resp = requests.get(url)

    with (DATA_PATH / 'card-images' / f"{card['name']}.jpg").open('wb') as f:
        print(f'downloaded {card["name"]}')
        f.write(resp.content)


def _deal_roles(players):
    num_players = len(players)
    # assert num_players > 3 and num_players < 9, f"Can't play treachery with {num_players} players"

    if num_players == 1:
        roles = [random.choice(['Traitor', 'Assassin', 'Assassin', 'Leader'])]
    if num_players == 4:
        roles = ['Traitor', 'Assassin', 'Assassin', 'Leader']
    elif num_players == 5:
        roles = ['Guardian', 'Traitor', 'Assassin', 'Assassin', 'Leader']
    elif num_players == 6:
        roles = ['Guardian', 'Traitor', 'Assassin', 'Assassin', 'Assassin', 'Leader']
    elif num_players == 7:
        roles = ['Guardian', 'Guardian', 'Traitor', 'Assassin', 'Assassin', 'Assassin', 'Leader']
    elif num_players == 8:
        roles = ['Guardian', 'Guardian', 'Traitor', 'Traitor', 'Assassin', 'Assassin', 'Assassin', 'Leader']

    random.shuffle(roles)

    return {player: role for player, role in zip(players, roles)}


def deal_role_cards(players):
    player_roles = _deal_roles(players)

    player_role_cards = {}

    for player, role in player_roles.items():
        player_role_cards[player] = random.choice(CARDS_BY_ROLE[role])

    return player_role_cards
