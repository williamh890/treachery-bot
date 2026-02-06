import pytest

from log_games import log_game


def test_log_game(current_roles):
    result = log_game(['wbhorn'], current_roles)
    import json

    print(json.dumps(result, indent=2))
    assert len(result) == 2
    assert len(result) == 2


@pytest.fixture
def current_roles():
    return {
        'negative274': {
            'id': 46, 'name': 'The Sigil Mage', 'name_anchor': 'the-sigil-mage', 'uri': 'https://mtgtreachery.net/rules/oracle/?card=the-sigil-mage', 'cost': '', 'cmc': 0, 'color': 'red', 'type': 'Identity — Assassin', 'types': {'supertype': 'Identity', 'subtype': 'Assassin'}, 'rarity': 'U', 'text': '', 'flavor': '', 'artist': 'Peter Orullian', 'rulings': []},
        'wbhorn': {
            'id': 50, 'name': 'The Blood Empress', 'name_anchor': 'the-blood-empress', 'uri': 'https://mtgtreachery.net/rules/oracle/?card=the-blood-empress', 'cost': '', 'cmc': 0, 'color': 'multicolor', 'type': 'Identity — Leader', 'types': {'supertype': 'Identity', 'subtype': 'Leader'}, 'rarity': 'U', 'text': 'rules text', 'flavor': '', 'artist': 'rkpost', 'rulings': []
        }
    }
