import requests
import random
import json
from collections import defaultdict, Counter
import pathlib
import urllib

DATA_PATH = pathlib.Path(__file__).parent / 'data'


class RoleDeck:
    def __init__(self):
        self.all_cards = _load_treachery_cards()
        self.cards_by_role = get_cards_by_role(self.all_cards)

    def __str__(self):
        return 'Current Role Deck: \n' + '\n'.join(
            [f'    {name}: {len(roles)}' for name, roles in self.cards_by_role.items()]
        )

    def deal(self, leader, players, spice_pct=0.02):
        player_roles = _deal_non_leader_roles(players, spice_pct)
        player_roles[leader] = 'Leader'

        player_role_cards = {}

        for role, count in Counter(player_roles.values()).items():
            if len(self.cards_by_role[role]) < count:
                self.cards_by_role[role] = self._get_all_cards_for(role)

        for player, role in player_roles.items():
            player_role_cards[player] = self.cards_by_role[role].pop()

        return player_role_cards

    def shuffle(self):
        self.cards_by_role = get_cards_by_role(self.all_cards)

    def _get_all_cards_for(self, role):
        return [card for card in self.all_cards if card['types']['subtype'] == role]


def _deal_non_leader_roles(players, spice_pct=0.02):
    num_players = len(players)

    if num_players < 3:
        roles = [random.choice(['Traitor', 'Assassin', 'Guardian']) for _ in range(num_players)]
    elif num_players == 3:
        roles = ['Traitor', 'Assassin', 'Assassin']
    elif num_players == 4:
        roles = ['Guardian', 'Traitor', 'Assassin', 'Assassin']
    elif num_players == 5:
        roles = ['Guardian', 'Traitor', 'Assassin', 'Assassin', 'Assassin']
    elif num_players == 6:
        roles = [
            'Guardian',
            'Guardian',
            'Traitor',
            'Assassin',
            'Assassin',
            'Assassin',
        ]
    elif num_players == 7:
        roles = [
            'Guardian',
            'Guardian',
            'Traitor',
            'Traitor',
            'Assassin',
            'Assassin',
            'Assassin',
        ]

    random.shuffle(roles)

    if random.random() < spice_pct:
        roles = _add_all_traitor_spice(roles)

    if random.random() < spice_pct:
        roles = _role_chaos(roles)

    return {player: role for player, role in zip(players, roles)}


def _add_all_traitor_spice(roles):
    return ['Traitor'] * len(roles)


def _role_chaos(roles):
    rng_role = random.choice(['Traitor', 'Traitor', 'Assassin', 'Guardian'])
    roles.pop()

    return roles + [rng_role]


def puppet_master(player_roles, message):
    print(player_roles, message)

    return {}


def wearer_of_masks(role_deck, x):
    def is_maskable_card(card):
        return card['types']['subtype'] != 'Leader' and card['name'] != 'The Wearer of Masks'

    non_leader_cards = [card for card in role_deck.all_cards if is_maskable_card(card)]

    if x > len(non_leader_cards):
        x = len(non_leader_cards)

    return random.sample(non_leader_cards, x)


def _load_treachery_cards():
    cards_path = pathlib.Path('cards.json')

    if not cards_path.exists():
        _download_cards(cards_path)

    with cards_path.open('r') as f:
        cards = json.load(f)

    return cards['cards']


def _download_cards(cards_path):
    cards_url = 'https://mtgtreachery.net/rules/oracle/treachery-cards.json'
    resp = requests.get(cards_url)

    with cards_path.open('wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def get_cards_by_role(cards):
    by_role = defaultdict(list)

    for card in cards:
        by_role[card['types']['subtype']].append(card)

    for role in by_role:
        random.shuffle(by_role[role])

    return by_role


def card_image(card):
    url_encoded = urllib.parse.quote(f'{card["id"]:03} - {card["types"]["subtype"]} - {card["name"]}.jpg')
    url = f'https://mtgtreachery.net/images/cards/en/trd/{url_encoded}'

    return url


def download_image(card, url):
    resp = requests.get(url)

    with (DATA_PATH / 'card-images' / f'{card["name"]}.jpg').open('wb') as f:
        print(f'downloaded {card["name"]}')
        f.write(resp.content)
