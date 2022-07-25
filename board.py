import numpy as np
import numpy.typing as npt

from ball import Ball

class Board():
    def __init__(self) -> None:
        self.tiles = np.zeros(76, dtype=np.object_) # Board is a 76 element mask with player balls as non-zero ints.
        self.len = len(self.tiles)
        self.win_tiles = np.repeat(np.zeros(4, dtype=np.object_), 4)

    def is_occupied(self, idx:int) -> bool:
            # Returns true if non-zero - aka ball present
            return bool(self.tiles[idx])

    def query_ball_at_idx(self, idx:int) -> Ball:
            return self.tiles[idx]

    def print(self) -> None:
        tiles = self.tiles
        for idx, tile in enumerate(tiles):
            if isinstance(tile, Ball):
                tiles[idx] = tile.owner
        print(*tiles.reshape(4,19), sep='\n')

    def update(self, idx, value) -> None:
        self.tiles[idx] = value
