from enum import IntEnum
from logging import warning
from typing import List, Tuple
from typing_extensions import Self
import numpy as np
import numpy.typing as npt
import json

# from board import Board #TODO: FIX circular imports


class States(IntEnum):
    JAILED = -1
    PROTECTED = 0
    ACTIVE = 1
    COMPLETE = 2


class Ball:
    def __init__(self, base_idx, owner, team) -> None:
        self.position = -1  # Out of bounds
        self.state = States.JAILED
        self.base_idx = base_idx
        self.owner = owner
        self.team = team

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def upadate_position(self, idx) -> None:
        self.position = idx

    def set_complete(self):
        self.state = States.COMPLETE

    def update_state(self) -> None:
        if self.position == self.base_idx:
            self.state = States.PROTECTED
        elif self.position == -1:
            self.state = States.JAILED
        elif self.state == States.COMPLETE:
            pass  # Do nothing if ball is marked as complete
        else:
            self.state = States.ACTIVE

    def can_jailbreak(self) -> bool:
        if self.state == States.JAILED:
            return True
        else:
            return False

    def jailbreak(self, board) -> None:
        if board.is_occupied(self.base_idx):
            board.handle_collison(self.base_idx)

        self.upadate_position(self.base_idx)
        board.update(self.base_idx, self)
        self.update_state()

    def move(self, path: List[int], board) -> None:
        if board.is_occupied(path[-1]):
            board.handle_collison(path[-1])

        board.update(self.position, 0)
        self.upadate_position(path[-1])
        board.update(self.position, self)
        self.update_state()

    def is_legal_move(self, path: List[int], board) -> bool:
        obstacles: List[Ball] = []
        if self.state == States.JAILED or self.state == States.COMPLETE:
            return False

        if not path:
            # warning("no path provided")
            return False

        for i in path:
            if board.is_occupied(i):
                obstacles.append(board.query_ball_at_idx(i))

        if obstacles:
            problem_idx = 99  # NOTE: Just a default so static code checkers dont get mad
            for obstacle_idx, obstacle in enumerate(obstacles):
                if obstacle_idx == 0:
                    problem_idx = obstacle.position+1
                else:
                    if problem_idx > board.len:
                        problem_idx = 0
                    if obstacle.position == problem_idx:  # TODO: Handle king?
                        warning("\nIllegal MOVE\n")
                        return False

                if obstacle.position == obstacle.base_idx:
                    warning("This path is obstructed")
                    return False  # Illegal move. Obstacle in its base and you cannot overtake it

        return True

    def can_swap(self, board):
        if self.state == States.JAILED or self.position > board.len:  # Cant swap if jailed or in win column
            return False

        swapable: List[Ball] = []
        for i in range(board.len):
            if board.is_occupied(i):
                ball = board.query_ball_at_idx(i)
                if ball.state == States.ACTIVE and ball.owner != self.owner:
                    swapable.append(ball)
        return swapable

    def swap(self, target_ball: Self, board):
        tmp = self.position
        self.upadate_position(target_ball.position)
        target_ball.upadate_position(tmp)
        self.update_state()
        target_ball.update_state()
        board.update(self.position, self)
        board.update(target_ball.position, target_ball)
