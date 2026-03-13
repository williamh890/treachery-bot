from typing import NamedTuple
import urllib

role_types = set(['Traitor', 'Assassin', 'Guardian', 'Leader'])


class RoleCard(NamedTuple):
    id: int
    name: str
    role: str
    text: str
    author: str
    image: str | None


def card_image_url(card: dict) -> str:
    url_encoded = urllib.parse.quote(f'{card["id"]:03} - {card["types"]["subtype"]} - {card["name"]}.jpg')
    url = f'https://mtgtreachery.net/images/cards/en/trd/{url_encoded}'

    return url
