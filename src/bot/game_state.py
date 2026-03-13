import treachery


class TreacheryGameState:
    def __init__(self):
        self.players = []
        self.role_deck = treachery.RoleDeck()
        self.current_roles = None
        self.game_number = 0
        self.has_rerolled = set()
        self.game_channel = None
        self.deal_messages = set()

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

            player_msgs[player.name] = self._role_card_message(role)

        roles = [role.role for role in self.current_roles.values()]

        game_msg = f'    Dealt out {len(roles)} roles (dice to reroll)'

        return player_msgs, game_msg

    def can_player_reroll(self, player):
        if not self.current_roles or player.name not in self.current_roles.keys():
            return "You haven't been dealt out a role."

        return None

    def reroll(self, player):
        role_type = self.current_roles[player.name].role
        dealt_roles = [role for role in self.current_roles.values() if role.role == role_type]

        role = self.role_deck.reroll(dealt_roles)

        self.has_rerolled.add(player.name)

        player_msg = 'Rerolled!\n\n'
        player_msg += self._role_card_message(role)

        return player_msg

    def _role_card_message(self, role):
        image = role.image or 'NO IMAGE'
        role_info = f'{role.role} - {role.name}'

        msg = f'|\n|\nGame {self.game_number}:\n'
        msg += f'    {role_info}'
        msg += f'    {role.author}\n\n'
        msg += f'    {role.text}\n\n'
        msg += f'{image}\n'

        return msg

    def shuffle(self):
        self.role_deck.shuffle()

        return 'Role deck has been reshuffled'

    def reset_rerolls(self):
        self.has_rerolled = set()

        return 'Player rerolls have been reset'

    def wearer_of_masks(self, x):
        return treachery.wearer_of_masks(self.role_deck, x)

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

            msg += f'    {idx}.) {name}: {role.name} [{role.role}]\n'
            idx += 1

        return msg
