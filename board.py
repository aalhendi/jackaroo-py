from copy import deepcopy
from typing import List
import numpy as np
import numpy.typing as npt
from ball import Ball


class Board():
    # TODO: Impl logger / visualizer
    def __init__(self, num_players: int) -> None:
        self.len = num_players * 19  # Fixed length per player
        # 4-player Board is a 76 element mask + 16 tiles for win columns
        self.tiles = np.zeros(self.len + 4*num_players, dtype=np.object_)

    def is_occupied(self, idx: int) -> bool:
        # Returns true if non-zero - aka ball present
        return bool(self.tiles[idx])

    def query_ball_at_idx(self, idx: int) -> Ball:
        return self.tiles[idx]

    def print(self) -> None:
        tiles = deepcopy(self.tiles)
        winners = tiles[-16:]
        tiles = tiles[:-16]
        for idx, tile in enumerate(tiles):
            if isinstance(tile, Ball):
                tiles[idx] = tile.owner
        for idx, tile in enumerate(winners):
            if isinstance(tile, Ball):
                winners[idx] = tile.owner
        print(*tiles.reshape(4, 19), sep='\n')
        print(*winners.reshape(4, 4), sep='\n')

    def update(self, idx, ball: Ball) -> None:
        self.tiles[idx] = ball

    def get_balls(self):
        balls = []
        for tile in range(self.len):
            if self.is_occupied(tile):
                ball = self.query_ball_at_idx(tile)
                balls.append(ball)
        return balls

    def handle_collison(self, idx: int) -> None:
        target_ball = self.query_ball_at_idx(idx)
        # NOTE: Not needed. There for completion
        self.update(target_ball.position, 0)
        # TODO: Merge upadate position and update state. Have a jailbreak method etc.
        target_ball.upadate_position(-1)
        target_ball.update_state()

    def calculate_move_path(self, ball: Ball, offset: int, team=None, is_five=False) -> List[int]:
        can_enter_win = True  # By default all can enter winner col
        if is_five and team != ball.team:
            can_enter_win = False  # If 5 & not same team then cant enter

        start = ball.position
        end = ball.position + offset
        # Starting tile for that win player's win column
        col_start = self.len + (4*(ball.owner-1))
        col_end = col_start + 4
        if (ball.base_idx - 2) > 0:
            entry = ball.base_idx - 2
        else:
            entry = self.len - 2  # For base_idx 0

        # Ball is somewhere in winners columns
        if start >= self.len:
            # is it moveable?
            max_move = 0
            for i in range(start+1, col_end):  # Check path
                if not bool(self.tiles[i]):  # if empty, can move there
                    max_move += 1
                else:
                    break
            if offset > max_move:
                return []  # Cant move more than empty spaces ahead
            path = list(range(start+1, start+offset+1))

        # Potential entry into win column
        # Must start before the entrypoint with offset ending after entry
        elif start <= entry and end > entry and can_enter_win:
            # From start to entry
            one = list(range(start + 1, entry + 1))
            remainder = offset - len(one)
            # Check if the offset remaining can get into winner tiles. Is there room?
            max_move = 0
            for i in range(col_start, col_end):  # Check path
                if not bool(self.tiles[i]):  # if empty, can move there
                    max_move += 1
                else:
                    break
            if remainder > max_move:
                return []  # Cant move more than available slots
            two = list(range(col_start, col_start + remainder))
            path = [*one, *two]

        elif end > self.len - 1:
            one = list(range(start + 1, self.len))  # left inclusive
            # loop around the board
            two = list(range(0, abs(offset) - len(one)))
            path = [*one, *two]

        elif end < 0:
            # inclusive left exclusive right to 0
            one = list(range(start-1, -1, -1))
            two = list(range(self.len-1, self.len-1 -
                       (abs(offset) - len(one)), -1))
            path = [*one, *two]

        elif offset > 0:
            path = list(range(start + 1, end + 1))

        else:
            path = list(range(start-1, end - 1, -1))

        return path
