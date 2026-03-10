import pytest
import datetime

from log_games import log_game, log_reroll


def test_log_game(current_roles):
    game_start_time = datetime.datetime.now() - datetime.timedelta(hours=2)
    notes = {'wbhorn': 'a note of the game', 'negative274': 'another note'}

    result = log_game(['wbhorn'], current_roles, game_start_time, notes)
    import json

    print(json.dumps(result, indent=2))
    assert len(result) == 2
    assert len(result) == 2

    notes = {}
    result = log_game(['negative274'], current_roles, game_start_time, notes)

    print(json.dumps(result, indent=2))
    assert len(result) == 2
    assert len(result) == 2


def test_log_reroll(reroll_event):
    role, user = reroll_event

    log_reroll(role, user)


@pytest.fixture
def current_roles():
    return {
        'negative274': {
            'id': 46, 'name': 'The Sigil Mage', 'name_anchor': 'the-sigil-mage', 'uri': 'https://mtgtreachery.net/rules/oracle/?card=the-sigil-mage', 'cost': '', 'cmc': 0, 'color': 'red', 'type': 'Identity — Assassin', 'types': {'supertype': 'Identity', 'subtype': 'Assassin'}, 'rarity': 'U', 'text': '', 'flavor': '', 'artist': 'Peter Orullian', 'rulings': []},
        'wbhorn': {
            'id': 50, 'name': 'The Blood Empress', 'name_anchor': 'the-blood-empress', 'uri': 'https://mtgtreachery.net/rules/oracle/?card=the-blood-empress', 'cost': '', 'cmc': 0, 'color': 'multicolor', 'type': 'Identity — Leader', 'types': {'supertype': 'Identity', 'subtype': 'Leader'}, 'rarity': 'U', 'text': 'rules text', 'flavor': '', 'artist': 'rkpost', 'rulings': []
        }
    }


@pytest.fixture
def reroll_event():
    return ({'id': 57, 'name': 'The King over the Scrapyard', 'name_anchor': 'the-king-over-the-scrapyard', 'uri': 'https://mtgtreachery.net/rules/oracle/?card=the-king-over-the-scrapyard', 'cost': '', 'cmc': 0, 'color': 'multicolor', 'type': 'Identity — Leader', 'types': {'supertype': 'Identity', 'subtype': 'Leader'}, 'rarity': 'R', 'text': 'Whenever a creature you control dies, if it was attacking or blocking, create a Junk token or a Treasure token. (A Junk token is an artifact with “{T}, Sacrifice this token: Exile the top card of your library. You may play that card this turn. Activate only as a sorcery.”)|Whenever a spell or ability an opponent controls causes a nontoken permanent you control to leave the battlefield, create a Junk token and a Treasure token.', 'flavor': '', 'artist': 'Ralph Horsley @ DeviantArt', 'rulings': ['The King over the Scrapyard’s first ability triggers for each attacking or blocking creature you control that dies. For each of them, you can choose to either create a Junk token or a Treasure token on resolution, but not both tokens.', 'The King over the Scrapyard’s second ability triggers only on spells and abilities that directly causes a nontoken permanent to leave the battlefield. The following won’t cause The King over the Scrapyard’s second ability to trigger: If a spell or ability an opponent controls deals lethal damage to a creature you control, removes all loyalty counters from a planeswalker you control, or causes an ability you control to trigger (and then that ability destroys or exiles a permanent you control).']}, 'wbhorn')
