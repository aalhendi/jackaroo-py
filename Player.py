from copy import deepcopy
from logging import warning
import random
from typing import List
from ball import Ball, States
import numpy as np

from board import Board


class Player():
    def __init__(self, base_idx) -> None:
        self.base_idx = base_idx
        self.number: int = self.base_idx_to_player_number(self.base_idx)
        # NOTE: Hacky implementation works for 4 players but not more
        self.team: int = self.number % 2
        self.balls = [Ball(self.base_idx, self.number, self.team), Ball(self.base_idx, self.number, self.team), Ball(
            self.base_idx, self.number, self.team), Ball(self.base_idx, self.number, self.team)]
        self.hand = np.array([], dtype=np.int8)
        self.current_action = dict()
        self.actions = []

    # def __repr__(self) -> str:
    #     p_dict = self.__dict__
    #     myballs =  [ball.__repr__ for ball in self.balls]
    #     p_dict['balls'] = myballs
    #     return json.dumps(p_dict)

    def create_balls(self) -> List[Ball]:
        balls: List[Ball] = []
        for _ in range(4):
            balls.append(Ball(self.base_idx, self.number, self.team))
        return balls

    def base_idx_to_player_number(self, base_idx) -> int:
        if base_idx == 0:
            return 1
        elif base_idx == 19:
            return 2
        elif base_idx == 38:
            return 3
        elif base_idx == 57:
            return 4
        else:
            return -1

    def update_hand(self, new_hand):
        self.hand = new_hand

    def burn(self) -> int:
        # TODO: skip next guys turn. Could be a game method that checks hand lengths in can_play_turn()
        np.random.shuffle(self.hand)
        burned = self.hand[0]
        self.hand = self.hand[1:]
        return burned

    def remove_card(self, idx: int) -> int:
        hand: List = self.hand.tolist()
        removed = hand.pop(idx)
        self.hand = np.array(hand, dtype=np.int8)
        return removed

    def decide_action(self):
        # TODO: Impl basic set of rules?
        # Check if theres at least one card to be played
        if len(self.actions) == 0:
            card_idx = random.randrange(len(self.hand))
            card_value = self.hand[card_idx]
            action = self.create_action(card_idx, card_value, "DISCARD")
            self.current_action = action
            return

        action = random.choice(self.actions)
        self.current_action = action

    def clear_actions(self) -> None:
        self.current_action = dict()
        self.actions = []

    def play_action(self, board: Board):
        verb = self.current_action['verb']
        if verb == "MOVE":
            ball_pos = self.current_action["ball_pos"]
            ball = board.query_ball_at_idx(ball_pos)
            path = self.current_action["path"]
            ball.move(path, board)

        elif 'JAILBREAK' == verb:
            ball_idx = self.current_action["ball_idx"]
            self.balls[ball_idx].jailbreak(board)

        elif 'BURN' == verb:
            warning("Not implemented BURN Processing")
            # burn(next_player_hand)
            pass

        elif verb == "FLEXMOVE":
            ball_pos1 = self.current_action["ball_pos1"]
            ball_pos2 = self.current_action["ball_pos2"]
            path1 = self.current_action["path1"]
            path2 = self.current_action["path2"]
            ball1 = board.query_ball_at_idx(ball_pos1)
            ball2 = board.query_ball_at_idx(ball_pos2)
            ball1.move(path1, board)
            ball2.move(path2, board)

        elif 'SWAP' == verb:
            ball_pos = self.current_action["ball_pos"]
            target_ball_pos = self.current_action["target_ball_pos"]
            b1 = board.query_ball_at_idx(ball_pos)
            b2 = board.query_ball_at_idx(target_ball_pos)
            b1.swap(b2, board)

        elif verb == 'DISCARD':
            pass  # Nothing to do for a discard.

        else:
            raise TypeError(f"Unkown action {self.current_action}")

        card_idx = self.current_action['card_idx']
        card = self.remove_card(card_idx)
        self.clear_actions()
        return card

    def create_action(self, card_idx, card_value, verb, **kwargs):
        base_action = dict(
            {"card_idx": card_idx, "card_value": card_value, "verb": verb})
        return base_action | kwargs

    def get_actions(self):
        actions = []
        for card_idx, card_value in enumerate(self.hand):
            verb = "MOVE"  # default verb
            offset = card_value  # default offset
            if card_value == 1:
                card = self.create_action(
                    card_idx, card_value, verb, offset=offset)
                actions += [
                    self.create_action(card_idx, card_value, verb, offset=11),
                    self.create_action(card_idx, card_value, verb="JAILBREAK")
                ]
            elif card_value == 4:
                card = self.create_action(
                    card_idx, card_value, verb, offset=-offset)
            elif card_value == 5:
                card = self.create_action(
                    card_idx, card_value, "MOVEANY", offset=offset)
            elif card_value == 7:
                card = self.create_action(card_idx, card_value, "FLEXMOVE")
            elif card_value == 10:
                card = self.create_action(card_idx, card_value, "BURN")
            elif card_value == 11:
                card = self.create_action(card_idx, card_value, "SWAP")
            elif card_value == 13:
                card = self.create_action(
                    card_idx, card_value, verb="JAILBREAK")  # Jailbreak
            else:
                card = self.create_action(
                    card_idx, card_value, verb, offset=offset)

            actions.append(card)
        self.actions = actions
        return

    def check_legal_actions(self, board: Board):
        legal_actions = []
        for action in self.actions:
            if action["verb"] == "MOVE":
                for ball_idx, ball in enumerate(self.balls):
                    if ball.state == States.JAILED or ball.state == States.COMPLETE:
                        pass  # Do nothing
                    else:
                        offset = action["offset"]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['path'] = path
                            new_action['ball_pos'] = ball.position
                            legal_actions.append(new_action)

            elif action['verb'] == "FLEXMOVE":
                moveable = self.count_moveable_balls()
                if len(moveable) == 1:
                    offset = 7
                    ball_idx = moveable[0]
                    ball = self.balls[ball_idx]
                    path = board.calculate_move_path(ball, offset)
                    is_legal = ball.is_legal_move(path, board)
                    if is_legal:
                        new_action = deepcopy(action)
                        new_action['verb'] = "MOVE"
                        new_action['path'] = path
                        new_action['ball_pos'] = ball.position
                        legal_actions.append(new_action)

                elif len(moveable) == 2:
                    ball_idx1 = moveable[0]
                    ball_idx2 = moveable[1]
                    ball1 = self.balls[ball_idx1]
                    ball2 = self.balls[ball_idx2]

                    # Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_pos'] = ball.position
                            legal_actions.append(new_action)

                    # Handle pairs
                    pair_actions = self.process_flexmove_pairs(
                        board, action, ball1, ball2, ball1.position, ball2.position)
                    legal_actions += pair_actions

                elif len(moveable) == 3:
                    # Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_pos'] = ball.position
                            legal_actions.append(new_action)

                    # Handle pairs
                    for i, k in [[0, 1], [0, 2], [1, 2]]:
                        ball_idx1 = moveable[i]
                        ball_idx2 = moveable[k]
                        ball1 = self.balls[ball_idx1]
                        ball2 = self.balls[ball_idx2]
                        pair_actions = self.process_flexmove_pairs(
                            board, action, ball1, ball2, ball1.position, ball2.position)
                        legal_actions += pair_actions

                elif len(moveable) == 4:
                    # Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_pos'] = ball.position
                            legal_actions.append(new_action)

                    # Handle pairs
                    for i, k in [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]:
                        ball_idx1 = moveable[i]
                        ball_idx2 = moveable[k]
                        ball1 = self.balls[ball_idx1]
                        ball2 = self.balls[ball_idx2]
                        pair_actions = self.process_flexmove_pairs(
                            board, action, ball1, ball2, ball1.position, ball2.position)
                        legal_actions += pair_actions

            elif action['verb'] == "JAILBREAK":
                for ball_idx, ball in enumerate(self.balls):
                    if ball.can_jailbreak():
                        new_action = deepcopy(action)
                        new_action['ball_idx'] = ball_idx
                        legal_actions.append(new_action)

            elif action['verb'] == 'BURN':
                # TODO: Check if last player in with 1 card in round
                legal_actions.append(action)

            elif action['verb'] == "MOVEANY":
                offset = action['offset']
                for tile in range(board.len):
                    if board.is_occupied(tile):
                        ball = board.query_ball_at_idx(tile)
                        if ball.state == States.ACTIVE or ball.owner == self.number:
                            path = board.calculate_move_path(
                                ball, offset, team=self.team, is_five=True)
                            if ball.is_legal_move(path, board):
                                new_action = deepcopy(action)
                                new_action['ball_pos'] = ball.position
                                new_action["verb"] = "MOVE"
                                new_action["path"] = path
                                legal_actions.append(new_action)

            elif action['verb'] == "SWAP":
                for ball_idx, ball in enumerate(self.balls):
                    swappable = ball.can_swap(board)
                    if swappable:
                        for b in swappable:
                            new_action = deepcopy(action)
                            new_action['ball_pos'] = ball.position
                            new_action['target_ball_pos'] = b.position
                            legal_actions.append(new_action)
            else:
                raise TypeError(f"Unkown verb in action {action}")
        self.actions = legal_actions
        return

    def count_moveable_balls(self):
        moveable = []
        for ball_idx, ball in enumerate(self.balls):
            if ball.state != States.JAILED and ball.state != States.COMPLETE:
                moveable.append(ball_idx)
        return moveable

    def process_flexmove_pairs(self, board: Board, action, ball1: Ball, ball2: Ball, ball_pos1: int, ball_pos2: int):
        actions = []
        for offset1, offset2 in [[6, 1], [5, 2], [4, 3], [3, 4], [2, 5], [1, 6]]:
            path1 = board.calculate_move_path(ball1, offset1)
            is_legal1 = ball1.is_legal_move(path1, board)
            path2 = board.calculate_move_path(ball2, offset2)
            is_legal2 = ball2.is_legal_move(path2, board)
            if is_legal1 and is_legal2:
                new_action = deepcopy(action)
                new_action['ball_pos1'] = ball_pos1
                new_action['ball_pos2'] = ball_pos2
                new_action["offset1"] = offset1
                new_action["offset2"] = offset2
                new_action['path1'] = path1
                new_action['path2'] = path2
                actions.append(new_action)
        return actions

    def check_win(self, board: Board) -> bool:
        win_tiles = board.tiles[-16:]
        my_win_tiles = win_tiles[(self.number-1)*4: (self.number - 1)*4 + 4]
        if bool(my_win_tiles[-1]):
            my_win_tiles[-1].set_complete()
            if bool(my_win_tiles[-2]):
                my_win_tiles[-2].set_complete()
                if bool(my_win_tiles[-3]):
                    my_win_tiles[-3].set_complete()
                    if bool(my_win_tiles[-4]):
                        my_win_tiles[-4].set_complete()
        return bool(my_win_tiles.all())
