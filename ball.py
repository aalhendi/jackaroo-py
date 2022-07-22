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
        match base_idx:
            case 0:
                return 1
            case 19:
                return 2
            case 38:
                return 3
            case 57:
                return 4
    
    def update_state(self) -> None:
        match self.position:
            case self.base_idx:
                self.state = States.PROTECTED
            case -1:
                self.state = States.JAILED
            case _:
                self.state = States.ACTIVE