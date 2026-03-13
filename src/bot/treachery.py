import requests
import random
import json
from collections import defaultdict, Counter
import pathlib

from cards import RoleCard, card_image_url
import spreadsheet


ASSET_PATH = pathlib.Path(__file__).parent / 'assets'


class RoleDeck:
    def __init__(self):
        self.all_cards: list[RoleCard] = self._load_treachery_cards()
        self.cards_by_role: dict[str, list[RoleCard]] = get_cards_by_role(self.all_cards)

    def __str__(self):
        return 'Current Role Deck: \n' + '\n'.join(
            [f'    {name}: {len(roles)}' for name, roles in self.cards_by_role.items()]
        )

    def deal(self, leader, players, spice_pct=0.03):
        player_roles = _deal_non_leader_roles(players, spice_pct)
        player_roles[leader] = 'Leader'

        player_role_cards = {}

        for role, count in Counter(player_roles.values()).items():
            if len(self.cards_by_role[role]) < count:
                self.cards_by_role[role] = self._get_all_cards_for(role)

        for player, role in player_roles.items():
            player_role_cards[player] = self.cards_by_role[role].pop()

        return player_role_cards

    def reroll(self, dealt_roles):
        count = len(dealt_roles)
        role_type = dealt_roles[0].role

        if len(self.cards_by_role[role_type]) < count:
            dealt_card_names = set(r.name for r in dealt_roles)

            self.cards_by_role[role_type] = [
                r for r in self._get_all_cards_for(role_type) if r.name not in dealt_card_names
            ]

        random.shuffle(self.cards_by_role[role_type])
        new_role = self.cards_by_role[role_type].pop()

        return new_role

    def shuffle(self):
        self.cards_by_role = get_cards_by_role(self.all_cards)

    def _get_all_cards_for(self, role):
        return [card for card in self.all_cards if card.role == role]

    def _load_treachery_cards(self) -> list[RoleCard]:
        cards_path = ASSET_PATH / 'cards.json'

        if not cards_path.exists():
            _download_cards(cards_path)

        with cards_path.open('r') as f:
            cards = json.load(f)

        try:
            loaded_cards = spreadsheet.load_custom_roles()
            print(f'Loaded cards from spreadsheet: {len(loaded_cards)}')
        except Exception as e:
            self.custom_cards_failed = str(e)
            loaded_cards = [
                RoleCard(
                    id=card['id'],
                    name=card['name'],
                    role=card['types']['subtype'],
                    text=card['text'],
                    author='Default Treachery',
                    image=card_image_url(card),
                )
                for card in cards['cards']
            ]
        else:
            self.custom_cards_failed = None

        return loaded_cards


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


def wearer_of_masks(role_deck, x):
    def is_maskable_card(card):
        return card.role != 'Leader' and card.name != 'The Wearer of Masks'

    non_leader_cards = [card for card in role_deck.all_cards if is_maskable_card(card)]

    if x > len(non_leader_cards):
        x = len(non_leader_cards)

    return random.sample(non_leader_cards, x)


def _download_cards(cards_path):
    cards_url = 'https://mtgtreachery.net/rules/oracle/treachery-cards.json'
    resp = requests.get(cards_url)

    with cards_path.open('wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def get_cards_by_role(cards: list[RoleCard]) -> dict[str, RoleCard]:
    by_role = defaultdict(list)

    for card in cards:
        by_role[card.role].append(card)

    for role in by_role:
        random.shuffle(by_role[role])

    return by_role


def download_image(card, url):
    resp = requests.get(url)

    with (ASSET_PATH / 'card-images' / f'{card["name"]}.jpg').open('wb') as f:
        print(f'downloaded {card["name"]}')
        f.write(resp.content)
