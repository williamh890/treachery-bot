import treachery


def test_loading_cards():
    assert treachery.ALL_CARDS
    assert set(treachery.CARDS_BY_ROLE.keys()) == {'Guardian', 'Traitor', 'Assassin', 'Leader'}


def test__get_roles():
    players = {'p1', 'p2', 'p3', 'p4'}
    roles = treachery._deal_roles(players)

    assert roles.keys() == players
    assert set(roles.values()) == {'Traitor', 'Assassin', 'Leader'}


def test_get_role_cards():
    players = {'p1', 'p2', 'p3', 'p4'}
    role_cards = treachery.deal_role_cards(players)

    assert role_cards.keys() == players

    assert set(card['types']['subtype'] for card in role_cards.values()) == {'Traitor', 'Assassin', 'Leader'}
