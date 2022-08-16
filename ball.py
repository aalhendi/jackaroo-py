from enum import IntEnum
from logging import warning
from typing import List, Tuple
from typing_extensions import Self
import json

# from board import Board #TODO: FIX circular imports


class States(IntEnum):
    JAILED = -1
    PROTECTED = 0
    ACTIVE = 1
    COMPLETE = 2


class Ball:
    def __init__(self, base_idx, owner, team_number) -> None:
        self.position = -1  # Out of bounds
        self.state = States.JAILED
        self.base_idx = base_idx
        self.owner = owner
        self.team_number = team_number

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
        if self.state == States.JAILED or self.state == States.COMPLETE:
            return False

        if not path:
            return False

        if len(path) > 1:
            slow_tile = path[0]
            slow_o = False
            if board.is_occupied(slow_tile):
                slow_o = board.query_ball_at_idx(slow_tile)
                if slow_o.state == States.PROTECTED and slow_o.owner != self.owner:
                    return False  # Path blocked by someone else's ball in base
            else:
                # Check rest of path
                for tile in path[1:]:
                    if board.is_occupied(slow_tile):
                        slow_o = board.query_ball_at_idx(slow_tile)
                    else:
                        slow_o = False
                    if board.is_occupied(tile):
                        o = board.query_ball_at_idx(tile)
                        if slow_o:
                            if path[-1] == o.position or path[-1] == slow_o.position:
                                return True  # Can land on one of the double obstacles if its the last step in path
                            else:
                                return False  # Path blocked by 2 consecutive balls and path not ending on one of them
                    else:
                        slow_tile = tile
        else:
            if board.is_occupied(path[0]):
                o = board.query_ball_at_idx(path[0])
                if o.state == States.PROTECTED and o.owner != self.owner:
                    return False

        return True

    def get_swapable(self, board):
        if self.state == States.JAILED or self.position >= board.len:  # Cant swap if jailed or in win column
            return False

        swapable: List[Ball] = []
        balls = board.get_balls()
        for ball in balls:
            if ball.state == States.ACTIVE and ball.owner != self.owner and ball.position < board.len:
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
