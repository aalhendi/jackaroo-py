from typing import List
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

    def handle_collison(self, idx:int) -> None:
        target_ball = self.query_ball_at_idx(idx)
        self.update(target_ball.position, 0) #NOTE: Not needed. There for completion
        target_ball.upadate_position(-1) #TODO: Merge upadate position and update state. Have a jailbreak method etc.
        target_ball.update_state()
    
    def calculate_move_path(self, ball:Ball, offset:int) -> List[int]:
        start = ball.position
        end = ball.position + offset

        #TODO: Handle victory paths & conditions

        # if offset == 5:
        #TODO: handle 5s and 7s
            # raise NotImplemented("Cant find 5 paths")

        if end > self.len - 1:
            one = list(range(start +1, self.len)) #left inclusive
            two = list(range(0, abs(offset) - len(one))) #loop around the board
            path = [*one, *two]
            # print(f"loop from {start} to {end} via {path}")
        elif ball.position + offset < 0:
            one = list(range(start-1, -1, -1)) #inclusive left exclusive right to 0
            two = list(range(self.len - 1, self.len - (abs(offset) - len(one)), -1)) #TODO: Check off by one error
            path = [*one, *two]
            # print(f"reverse loop from {start} to {end} via {path}")
        else:
            if offset > 0:
                path = list(range(start +1, end +1))
                # print(f"Standard forward from {start} to {end} via {path}")
            else:
                path = list(range(start-1, end, -1))
                # print(f"Standard backward from {start} to {end} via {path}")

        return path