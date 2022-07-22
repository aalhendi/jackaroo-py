from enum import Enum
from typing import List, Tuple
import numpy as np
import numpy.typing as npt

class Board():
    def __init__(self) -> None:
        self.tiles = np.zeros(76, dtype=np.int8) # Board is a 76 element mask with player balls as non-zero ints.
        self.len = len(self.tiles)

    def print(self) -> None:
        print(*self.tiles.reshape(4,19), sep='\n')
    
    def update(self, idx, value) -> None:
        self.tiles[idx] = value