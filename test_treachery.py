import treachery


def test_loading_cards():
    role_deck = treachery.RoleDeck()
    assert role_deck.all_cards
    assert set(role_deck.cards_by_role.keys()) == {'Guardian', 'Traitor', 'Assassin', 'Leader'}


def test__get_roles():
    players = {'p1', 'p2', 'p3', 'p4'}
    roles = treachery._deal_roles(players)

    assert roles.keys() == players
    assert set(roles.values()) == {'Traitor', 'Assassin', 'Leader'}


def test_get_role_cards():
    players = {'p1', 'p2', 'p3', 'p4'}
    role_cards = treachery.RoleDeck().deal(players)

    assert role_cards.keys() == players
    assert set(card['types']['subtype'] for card in role_cards.values()) == {'Traitor', 'Assassin', 'Leader'}


def test_multiple_deals():
    players = {'p1', 'p2', 'p3', 'p4'}
    role_deck = treachery.RoleDeck()
    seen_roles = set()

    for _ in range(9):
        role_cards = role_deck.deal(players)
        dealt = [role['name'] for role in role_cards.values()]

        assert all(role not in seen_roles for role in dealt)
        seen_roles.update(dealt)

    role_cards = role_deck.deal(players)
    dealt = [role['name'] for role in role_cards.values()]
    assert any(role in seen_roles for role in dealt)


def test_shuffle():
    players = {'p1', 'p2', 'p3', 'p4'}
    role_deck = treachery.RoleDeck()

    for _ in range(9):
        role_deck.deal(players)

    assert len(role_deck.cards_by_role['Assassin']) == 0

    role_deck.shuffle()

    assert len(role_deck.cards_by_role['Assassin']) == 18
    assert len(role_deck.cards_by_role['Leader']) == 13
    assert len(role_deck.cards_by_role['Guardian']) == 18
    assert len(role_deck.cards_by_role['Traitor']) == 13
