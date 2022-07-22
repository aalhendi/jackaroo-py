from enum import Enum
from typing import List, Tuple
import numpy as np
import numpy.typing as npt
from board import Board

class Game():
    def __init__(self) -> None:
        self.board = Board()