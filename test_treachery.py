import treachery


def test_loading_cards():
    role_deck = treachery.RoleDeck()
    assert role_deck.all_cards
    assert set(role_deck.cards_by_role.keys()) == {
        'Guardian',
        'Traitor',
        'Assassin',
        'Leader',
    }


def test_deal_roles():
    players = {'p1', 'p2', 'p3'}
    roles = treachery._deal_non_leader_roles(players, spice_pct=-1)

    assert roles.keys() == players
    assert set(roles.values()) == {'Traitor', 'Assassin'}

    for num_players in range(1, 8):
        players = {f'p{player_num + 1}' for player_num in range(num_players)}
        roles = treachery._deal_non_leader_roles(players, spice_pct=-1)

        assert roles.keys() == players
        assert len(roles.values()) == len(players)


def test_get_role_cards():
    players = {'p1', 'p2', 'p4'}
    role_cards = treachery.RoleDeck().deal('p3', players, spice_pct=-1)

    assert role_cards.keys() == players | {'p3'}
    assert set(card['types']['subtype'] for card in role_cards.values()) == {
        'Traitor',
        'Assassin',
        'Leader',
    }
    assert role_cards['p3']['types']['subtype'] == 'Leader'


def test_multiple_deals():
    players = {'p1', 'p2', 'p3'}
    role_deck = treachery.RoleDeck()
    seen_roles = set()

    for _ in range(9):
        role_cards = role_deck.deal('p4', players, spice_pct=-1)
        dealt = [role['name'] for role in role_cards.values()]

        assert all(role not in seen_roles for role in dealt)
        seen_roles.update(dealt)

    role_cards = role_deck.deal('p4', players, spice_pct=-1)
    dealt = [role['name'] for role in role_cards.values()]
    assert any(role in seen_roles for role in dealt)


def test_shuffle():
    players = {'p2', 'p3', 'p4'}
    role_deck = treachery.RoleDeck()

    for _ in range(9):
        role_deck.deal('p1', players, spice_pct=-1)

    assert len(role_deck.cards_by_role['Assassin']) == 0

    role_deck.shuffle()

    assert len(role_deck.cards_by_role['Assassin']) == 18
    assert len(role_deck.cards_by_role['Leader']) == 13
    assert len(role_deck.cards_by_role['Guardian']) == 18
    assert len(role_deck.cards_by_role['Traitor']) == 13


def test_wearer_of_masks():
    cards = treachery.RoleDeck()

    assert len(treachery.wearer_of_masks(cards, 0)) == 0
    assert len(treachery.wearer_of_masks(cards, 1)) == 1
    assert len(treachery.wearer_of_masks(cards, 100)) == 18 + 18 + 12


def test_puppet_master():
    cards = treachery.RoleDeck()
    assert cards


def test_all_traitor_spice():
    assert treachery._add_all_traitor_spice(['Assassin']) == ['Traitor']
    assert treachery._add_all_traitor_spice(
        [
            'Guardian',
            'Guardian',
            'Traitor',
            'Assassin',
            'Assassin',
            'Assassin',
        ]
    ) == ['Traitor', 'Traitor', 'Traitor', 'Traitor', 'Traitor', 'Traitor']

    assert treachery._add_all_traitor_spice(
        [
            'Guardian',
            'Traitor',
            'Assassin',
            'Assassin',
        ]
    ) == ['Traitor', 'Traitor', 'Traitor', 'Traitor']


def test_role_chaos():
    assert 'RngRole' not in treachery._role_chaos(['RngRole'])
