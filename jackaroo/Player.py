from __future__ import annotations
from copy import deepcopy
import json
import random
from typing import Any, Deque, Literal
from Ball import Ball, States
from Board import Board
from policies import jailbrak_pacifict, random_policy
from utils.actions import action_map
from pprint import pformat


class Player():
    def __init__(self, base_idx: int, turn_order: Deque[int], team_number: int) -> None:
        self.base_idx = base_idx
        self.number: int = (self.base_idx // 19)+1
        self.team_number = team_number
        self.balls: list[Ball] = [
            Ball(self.base_idx, self.number, self.team_number) for _ in range(4)]
        self.hand: list[int] = []
        self.current_action: dict[str, Any] = dict()
        self.actions: list[dict[str, Any]] = []
        self.turn_order = turn_order
        self.is_finished: bool = False
        self.teammate_balls: list[Ball] = []

    def __repr__(self) -> str:
        p_dict = deepcopy(vars(self))
        balls = [pformat(json.loads(ball.__repr__())) for ball in self.balls]
        p_dict.update({'balls': balls})
        return pformat(p_dict)

    def set_turn_context(self, turn_order: Deque[int]) -> None:
        """Sets the turn_order property

        Args:
            turn_order (Deque[int]): new turn order
        """
        self.turn_order = turn_order

    def set_teammate_balls(self, balls: list[Ball]) -> None:
        """Sets the teammate_balls property

        Args:
            balls (List[Ball]): list of teammate balls
        """
        self.teammate_balls = balls

    def update_hand(self, new_hand: list[int]) -> None:
        """Updates the hand property

        Args:
            new_hand (List[int]): list of card values
        """
        self.hand = new_hand

    def burn(self) -> dict[str, Any]:
        """Burns a random card from a player instance's hand

        Returns:
            action (Dict[str, int|str|bool]): player discard action
        """
        random.shuffle(self.hand)
        card_value = self.hand[0]
        self.hand = self.hand[1:]
        action: dict[str, Any] = {
            "card_value": card_value, "verb": "DISCARD", "is_burn": True}
        return action

    def remove_card(self, card_value: int) -> None:
        """Removes first occurance of card_value from player instance's hand

        Args:
            card_value (int): value of card to be removed
        """
        self.hand.pop(self.hand.index(card_value))
        return

    def decide_action(self, board:Board, policy: str) -> None:
        """Decides action from actions property

        Args:
            policy (str): decision policy to be used
        """
        action: dict[str, Any]
        if policy == "random":
            action = random_policy(self)
        elif policy == "jailbreak_pacifist":
            action = jailbrak_pacifict(self, board)
        else:
            raise NotImplementedError("Policy not implemented:", policy)
        self.current_action = action

    def clear_actions(self) -> None:
        """ Clears player instance's current action and actions list """
        self.current_action = dict()
        self.actions = []

    def play_action(self, board: Board) -> dict[str, Any]:
        """Excecutes action for a player's instance

        Args:
            board (Board): board instance

        Returns:
            action (dict[str, Any]): action executed
        """
        action = self.current_action
        verb: str = action['verb']

        if verb == "MOVE":
            ball = board.query_ball_at_idx(self.current_action["ball_pos"])

            if not isinstance(ball, Ball):
                raise TypeError("Expected Ball type")

            path = self.current_action["path"]
            ball.move(path, board)

        elif 'JAILBREAK' == verb:
            ball_idx: int = self.current_action["ball_idx"]
            if self.is_finished:
                balls = self.teammate_balls
            else:
                balls = self.balls
            balls[ball_idx].jailbreak(board)

        elif 'BURN' == verb:
            # Do nothing. Burn is handled by game
            pass

        elif verb == "FLEXMOVE":
            path1: list[int] = self.current_action["path1"]
            path2: list[int] = self.current_action["path2"]
            ball1 = board.query_ball_at_idx(self.current_action["ball_pos1"])
            ball2 = board.query_ball_at_idx(self.current_action["ball_pos2"])

            if not isinstance(ball1, Ball) or not isinstance(ball2, Ball):
                raise TypeError("Expected Ball type")

            ball1.move(path1, board)
            ball2.move(path2, board)

        elif verb == 'SWAP':
            ball_pos: int = self.current_action["ball_pos"]
            target_ball_pos: int = self.current_action["target_ball_pos"]
            b1 = board.query_ball_at_idx(ball_pos)
            b2 = board.query_ball_at_idx(target_ball_pos)
            if not isinstance(b1, Ball) or not isinstance(b2, Ball):
                raise TypeError("Expected Ball type")
            b1.swap(b2, board)

        elif verb == 'DISCARD':
            pass  # Nothing to do for a discard.

        else:
            raise TypeError(f"Unkown action {self.current_action}")

        self.remove_card(self.current_action["card_value"])
        self.clear_actions()
        return action

    def get_actions(self) -> None:
        """  Sets actions property based on player's hand"""
        actions: list[dict[str, Any]] = []
        for card_value in self.hand:
            card_actions = action_map[str(card_value)]
            actions += card_actions
        self.actions = actions

    def check_legal_actions(self, board: Board) -> None:
        """ Filters actions property to legal actions only

        Args:
            board (Board): board instance
        """
        legal_actions: list[dict[str, Any]] = []
        if self.is_finished:
            balls = self.teammate_balls
        else:
            balls = self.balls
        moveable = self.get_moveable_balls(balls)
        for action in self.actions:
            verb: str = action["verb"]
            if verb == "MOVE":
                if len(moveable) > 0:
                    for ball in moveable:
                        offset = action["offset"]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            action.update(
                                {"path": path, "ball_pos": ball.position})
                            legal_actions.append(action)

            elif verb == "FLEXMOVE":
                pairs: list[list[int]] = []
                if len(moveable) == 2:
                    pairs = [[0, 1]]
                elif len(moveable) == 3:
                    pairs = [[0, 1], [0, 2], [1, 2]]
                elif len(moveable) == 4:
                    pairs = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
                else:
                    pass

                for i, k in pairs:
                    ball1 = moveable[i]
                    ball2 = moveable[k]
                    new_action = self.check_flexmove_pair(
                        board, action, ball1, ball2)
                    if not new_action == False:
                        legal_actions.append(new_action)

            elif verb == "JAILBREAK":
                for ball_idx, ball in enumerate(balls):
                    if ball.can_jailbreak():
                        new_action = deepcopy(action)
                        new_action.update({"ball_idx": ball_idx})
                        legal_actions.append(new_action)

            elif verb == 'BURN':
                can_burn = self.can_burn()
                if can_burn:
                    legal_actions.append(action)

            elif verb == "MOVEANY":
                offset = action['offset']
                balls = board.get_balls()
                for ball in balls:
                    if self.is_finished:
                        can_move = ball.team_number == self.team_number
                    else:
                        can_move = ball.owner == self.number
                    if ball.state == States.ACTIVE or can_move:
                        path = board.calculate_move_path(
                            ball, offset, team_number=self.team_number, is_five=True)
                        if ball.is_legal_move(path, board):
                            details = {"ball_pos": ball.position,
                                       "verb": "MOVE", "path": path}
                            action.update(details)
                            legal_actions.append(action)

            elif verb == "SWAP":
                for ball in balls:
                    swappable = ball.get_swapable(board)
                    for b in swappable:
                        action.update(
                            {"ball_pos": ball.position, "target_ball_pos": b.position})
                        legal_actions.append(action)
            else:
                raise TypeError(f"Unkown verb in action {action}")
        self.actions = legal_actions
        return

    def get_moveable_balls(self, balls: list[Ball]) -> list[Ball]:
        moveable: list[Ball] = []
        for ball in balls:
            if ball.state != States.JAILED and ball.state != States.COMPLETE:
                moveable.append(ball)
        return moveable

    def can_burn(self) -> bool:
        """Checks if can burn from next player in turn order

        Returns:
            bool: True if can burn
        """
        # Cant burn if last to play turn with one card left.
        if len(self.hand) == 1 and self.turn_order[-1]+1 == self.number:
            return False
        else:
            return True

    def check_flexmove_pair(self, board: Board, action: dict[str, Any], ball1: Ball, ball2: Ball) -> dict[str, Any] | Literal[False]:
        """ Checks if pair of paths is legal

        Args:
            board (Board): board instance
            action (dict[str,Any]): FLEXMOVE action
            ball1 (Ball): first ball instance
            ball2 (Ball): second ball instance

        Returns:
            action (dict[str,Any]) | Literal[False]: updated action if legal flexmove else False
        """
        path1 = board.calculate_move_path(ball1, action["offset1"])
        is_legal1 = ball1.is_legal_move(path1, board)
        path2 = board.calculate_move_path(ball2, action["offset2"])
        is_legal2 = ball2.is_legal_move(path2, board)
        if is_legal1 and is_legal2:
            action.update(
                {"ball_pos1": ball1.position, "ball_pos2": ball2.position, "path1": path1, "path2": path2})
            return action
        else:
            return False

    def check_win(self, board: Board) -> bool:
        """ Checks if win column is complete for self

        Args:
            board (Board): board instance

        Returns:
            bool: True if complete
        """
        if self.is_finished:
            return self.is_finished
        win_tiles = board.tiles[-16:]
        my_win_tiles = win_tiles[(self.number-1)*4: (self.number - 1)*4 + 4]
        if isinstance(my_win_tiles[-1], Ball):
            my_win_tiles[-1].set_complete()
            if isinstance(my_win_tiles[-2], Ball):
                my_win_tiles[-2].set_complete()
                if isinstance(my_win_tiles[-3], Ball):
                    my_win_tiles[-3].set_complete()
                    if isinstance(my_win_tiles[-4], Ball):
                        my_win_tiles[-4].set_complete()
        is_finished = all(my_win_tiles)
        self.is_finished = is_finished
        return is_finished
