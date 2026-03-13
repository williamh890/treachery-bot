import pytest
import datetime

from spreadsheet import log_game, log_reroll, load_custom_roles
import cards


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


def test_load_custom_roles():
    custom_roles = load_custom_roles()

    assert len(custom_roles) > 10
    assert all([r.id >= 1000 for r in custom_roles])
    assert all([r.role in cards.role_types for r in custom_roles])


@pytest.fixture
def current_roles() -> dict[str, cards.RoleCard]:
    return {
        'negative274': cards.RoleCard(
            id=46,
            name='The Sigil Mage',
            role='Assassin',
            text='',
            author='Default Treachery',
            image='https://mtgtreachery.net/rules/oracle/?card=the-sigil-mage',
        ),
        'wbhorn': cards.RoleCard(
            id=50,
            name='The Blood Empress',
            role='Leader',
            text='rules text',
            author='Default Treachery',
            image='https://mtgtreachery.net/rules/oracle/?card=the-blood-empress',
        ),
    }


@pytest.fixture
def reroll_event():
    return (
        cards.RoleCard(
            id=57,
            name='The King over the Scrapyard',
            role='Leader',
            text='Whenever a creature you control dies, if it was attacking or blocking, create a Junk token or a Treasure token. (A Junk token is an artifact with “{T}, Sacrifice this token: Exile the top card of your library. You may play that card this turn. Activate only as a sorcery.”)|Whenever a spell or ability an opponent controls causes a nontoken permanent you control to leave the battlefield, create a Junk token and a Treasure token.',
            author='Default Treachery',
            image='https://mtgtreachery.net/rules/oracle/?card=the-king-over-the-scrapyard',
        ),
        'wbhorn',
    )
