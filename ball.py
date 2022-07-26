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

class Ball:
    def __init__(self, base_idx) -> None:
        self.position = -1 #Out of bounds
        self.state = States.JAILED
        self.base_idx = base_idx
        self.owner = self.base_idx_to_player_number(base_idx)

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)

    def base_idx_to_player_number(self, base_idx):
        if base_idx == 0:
            return 1
        elif base_idx == 19:
            return 2
        elif base_idx == 38:
            return 3
        elif base_idx == 57:
            return 4

    def upadate_position(self, idx)->None:
        self.position = idx

    def update_state(self) -> None:
        if self.position ==  self.base_idx:
            self.state = States.PROTECTED
        elif self.position ==  -1:
            self.state = States.JAILED
        else:
            self.state = States.ACTIVE

    def can_jailbreak(self)->bool:
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
    
    def move(self, path:List[int], board) -> None:
        if board.is_occupied(path[-1]):
            board.handle_collison(path[-1])

        board.update(self.position, 0)
        self.upadate_position(path[-1])
        board.update(self.position, self)
        self.update_state()

    
    def is_legal_move(self, path:List[int], board)-> bool:
            obstacles:List[Ball] = []
            if self.state == States.JAILED:
                return False

            if not path:
                raise LookupError("No path to traverse")

            #TODO: Handle victory legal moves

            for i in path:
                if board.is_occupied(i):
                    obstacles.append(board.query_ball_at_idx(i))

            if obstacles:
                problem_idx = 99 #NOTE: Just a default so static code checkers dont get mad
                for obstacle_idx, obstacle in enumerate(obstacles):
                    if obstacle_idx == 0:
                        problem_idx = obstacle.position+1
                    else:
                        if problem_idx > board.len:
                            problem_idx = 0
                        if obstacle.position == problem_idx: #TODO: Handle king?
                            warning("\nIllegal MOVE\n")
                            return False

                    if obstacle.position == obstacle.base_idx:
                        warning("This path is obstructed")
                        return False #Illegal move. Obstacle in its base and you cannot overtake it

            return True
    
    def can_swap(self, board):
        swapable:List[Ball] = []
        for i in range(board.len):
            if board.is_occupied(i):
                ball = board.query_ball_at_idx(i)
                if ball.state != States.PROTECTED and ball.base_idx != self.base_idx:
                    swapable.append(ball)
        return swapable

    def swap(self, target_ball:Self, board):
        tmp = self.position
        self.upadate_position(target_ball.position)
        target_ball.upadate_position(tmp)
        self.update_state()
        target_ball.update_state()
        board.update(self.position, self)
        board.update(target_ball.position, target_ball)
