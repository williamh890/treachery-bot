import treachery


class TreacheryGameState:
    def __init__(self):
        self.players = []
        self.role_deck = treachery.RoleDeck()
        self.current_roles = None
        self.game_number = 0

    def set_players(self, players):
        self.players = players

        return self.players_status_msg

    def add_players(self, new_players):
        current_players = set(player.name for player in self.players)

        for new_player in new_players:
            if new_player.name in current_players:
                continue

            self.players.append(new_player)

        return self.players_status_msg

    def remove_players(self, players_to_remove):
        to_remove = set(player.name for player in players_to_remove)
        self.players = [p for p in self.players if p.name not in to_remove]

        return self.players_status_msg

    def deal(self, leader_player):
        self.game_number += 1
        non_leader_players = [player.name for player in self.players if player.name != leader_player.name]
        self.current_roles = self.role_deck.deal(leader_player.name, non_leader_players)

        player_msgs = {}
        for player in self.players:
            role = self.current_roles[player.name]
            image = treachery.card_image(role)

            player_msgs[player.name] = f'Game {self.game_number}\n{image}'

        roles = [role['types']['subtype'] for role in self.current_roles.values()]

        game_msg = f'Game {self.game_number}:\n'
        game_msg += f'    Dealt out {len(roles)}'

        return player_msgs, game_msg

    def shuffle(self):
        self.role_deck.shuffle()

        return 'Role deck has been reshuffled'

    def wearer_of_masks(self, x):
        return treachery.wearer_of_masks(self.role_deck, x)

    def puppet(self):
        return treachery.puppet_master(self.current_roles)

    @property
    def players_status_msg(self):
        if not self.players:
            msg = 'No treach gamers :('
        else:
            names = ', '.join(player.name for player in self.players)
            msg = f'Treachery Gamers: {names}'

        return msg

    def player_roles_msg(self, filter_player):
        if not self.current_roles:
            return 'No roles are dealt'

        msg, idx = 'Other Player Roles: \n', 1

        for name, role in self.current_roles.items():
            if name == filter_player:
                continue

            msg += f'    {idx}.) {name}: {role["name"]} [{role["types"]["subtype"]}]\n'
            idx += 1

        return msg
