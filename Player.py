from copy import deepcopy
import json
import random
from typing import List
from ball import Ball, States
import numpy as np
from board import Board
from utils.actions import action_map
from pprint import pformat


class Player():
    def __init__(self, base_idx, turn_order, team_number) -> None:
        self.base_idx = base_idx
        self.number: int = (self.base_idx // 19)+1
        self.team_number = team_number
        self.balls: List[Ball] = [
            Ball(self.base_idx, self.number, self.team_number) for _ in range(4)]
        self.hand = np.array([], dtype=np.int8)
        self.current_action = dict()
        self.actions = []
        self.turn_order = turn_order

    def __repr__(self) -> str:
        p_dict = deepcopy(self.__dict__)
        balls = [pformat(json.loads(ball.__repr__())) for ball in self.balls]
        p_dict.update({'balls': balls, 'hand': self.hand.tolist(),
                      'turn_order': self.turn_order.tolist()})
        return pformat(p_dict)

    def set_turn_context(self, turn_order):
        self.turn_order = turn_order

    def update_hand(self, new_hand):
        self.hand = new_hand

    def burn(self):
        np.random.shuffle(self.hand)
        card_value = self.hand[0]
        self.hand = self.hand[1:]
        action = {"card_value": card_value, "verb": "DISCARD", "is_burn": True}
        return action

    def remove_card(self, card_value: int) -> int:
        hand: List = self.hand.tolist()
        hand.pop(hand.index(card_value))
        self.hand = np.array(hand, dtype=np.int8)
        return

    def decide_action(self):
        # TODO: Impl basic set of rules?
        # Check if theres at least one card to be played
        if len(self.actions) == 0:
            card_idx = random.randrange(len(self.hand))
            card_value = self.hand[card_idx]
            action = {"card_value": card_value,
                      "verb": "DISCARD", "is_burn": False}
            self.current_action = action
            return

        action = random.choice(self.actions)
        self.current_action = action

    def clear_actions(self) -> None:
        self.current_action = dict()
        self.actions = []

    def play_action(self, board: Board):
        action = self.current_action
        verb = action['verb']

        if verb == "MOVE":
            ball_pos = self.current_action["ball_pos"]
            ball = board.query_ball_at_idx(ball_pos)
            path = self.current_action["path"]
            ball.move(path, board)

        elif 'JAILBREAK' == verb:
            ball_idx = self.current_action["ball_idx"]
            self.balls[ball_idx].jailbreak(board)

        elif 'BURN' == verb:
            # Do nothing. Burn is handled by game
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

        self.remove_card(self.current_action["card_value"])
        self.clear_actions()
        return action

    def get_actions(self):
        actions = []
        for card_value in self.hand:
            card_actions = action_map[str(card_value)]
            actions += card_actions
        self.actions = actions

    def check_legal_actions(self, board: Board):
        legal_actions = []
        moveable = self.get_moveable_balls()
        for action in self.actions:
            if action["verb"] == "MOVE":
                if len(moveable) > 0:
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        offset = action["offset"]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            action.update(
                                {"path": path, "ball_pos": ball.position})
                            legal_actions.append(action)

            elif action['verb'] == "FLEXMOVE":
                if len(moveable) == 2:
                    pairs = [[0, 1]]
                elif len(moveable) == 3:
                    pairs = [[0, 1], [0, 2], [1, 2]]
                elif len(moveable) == 4:
                    pairs = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
                else:
                    pass

                if len(moveable) > 1:
                    for i, k in pairs:
                        ball_idx1 = moveable[i]
                        ball_idx2 = moveable[k]
                        ball1 = self.balls[ball_idx1]
                        ball2 = self.balls[ball_idx2]
                        new_action = self.check_flexmove_pair(
                            board, action, ball1, ball2, ball1.position, ball2.position)
                        if new_action:
                            legal_actions.append(new_action)

            elif action['verb'] == "JAILBREAK":
                for ball_idx, ball in enumerate(self.balls):
                    if ball.can_jailbreak():
                        action.update({"ball_idx": ball_idx})
                        legal_actions.append(action)

            elif action['verb'] == 'BURN':
                can_burn = self.can_burn()
                if can_burn:
                    legal_actions.append(action)

            elif action['verb'] == "MOVEANY":
                offset = action['offset']
                balls = board.get_balls()
                for ball in balls:
                    if ball.state == States.ACTIVE or ball.owner == self.number:
                        path = board.calculate_move_path(
                            ball, offset, team_number=self.team_number, is_five=True)
                        if ball.is_legal_move(path, board):
                            details = {"ball_pos": ball.position,
                                       "verb": "MOVE", "path": path}
                            action.update(details)
                            legal_actions.append(action)

            elif action['verb'] == "SWAP":
                for ball_idx, ball in enumerate(self.balls):
                    swappable = ball.get_swapable(board)
                    if swappable:
                        for b in swappable:
                            action.update(
                                {"ball_pos": ball.position, "target_ball_pos": b.position})
                            legal_actions.append(action)
            else:
                raise TypeError(f"Unkown verb in action {action}")
        self.actions = legal_actions
        return

    def get_moveable_balls(self):
        moveable = []
        for ball_idx, ball in enumerate(self.balls):
            if ball.state != States.JAILED and ball.state != States.COMPLETE:
                moveable.append(ball_idx)
        return moveable

    def can_burn(self):
        # Cant burn if last to play turn with one card left.
        if len(self.hand) == 1 and self.turn_order[-1]+1 == self.number:
            return False
        else:
            return True

    def check_flexmove_pair(self, board: Board, action, ball1: Ball, ball2: Ball, ball_pos1: int, ball_pos2: int):
        path1 = board.calculate_move_path(ball1, action["offset1"])
        is_legal1 = ball1.is_legal_move(path1, board)
        path2 = board.calculate_move_path(ball2, action["offset2"])
        is_legal2 = ball2.is_legal_move(path2, board)
        if is_legal1 and is_legal2:
            action.update(
                {"ball_pos1": ball_pos1, "ball_pos2": ball_pos2, "path1": path1, "path2": path2})
            return action
        else:
            return False

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
