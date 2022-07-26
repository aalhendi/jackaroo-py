from enum import IntEnum
from typing import List, Tuple
import numpy as np
import numpy.typing as npt
import json


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
        board.update(self.base_idx, self.owner)
        self.update_state()
    
    def move(self, path:List[int], board) -> None:
        if board.is_occupied(path[-1]):
            board.handle_collison(path[-1])

        board.update(self.position, 0)
        self.upadate_position(path[-1])
        board.update(self.position, self.owner)
        self.update_state()

    
