from __future__ import annotations
from typing import Literal
from Ball import Ball


class Board():
    # TODO: Impl logger / visualizer
    def __init__(self, num_players: int) -> None:
        self.num_players = num_players
        self.ROW_LEN: Literal[19] = 19
        self.WIN_COL_LEN: Literal[4] = 4
        self.len: int = num_players * self.ROW_LEN  # Fixed length per player
        self.win_len: int = num_players * self.WIN_COL_LEN  # Fixed length per player
        # 4-player Board is a 76 element mask + 16 tiles for win columns
        self.tiles: list[int | Ball] = [0]*(self.len + self.win_len)

    def is_occupied(self, idx: int) -> bool:
        """Checks if given tile index is occupied

        Args:
            idx (int): tile index

        Returns:
            bool: True if occupied
        """
        # Returns true if non-zero - aka ball present
        return bool(self.tiles[idx])

    def query_ball_at_idx(self, idx: int) -> Ball | int:
        """ Returns value of tile at index=idx

        Args:
            idx (int): tile index

        Returns:
            Ball|int: Ball instance if value is ball else tile int value
        """
        return self.tiles[idx]

    def print(self) -> None:
        winners = self.tiles[-self.win_len:]
        tiles = self.tiles[:-self.win_len]
        for idx, tile in enumerate(tiles):
            if isinstance(tile, Ball):
                tiles[idx] = tile.owner
        for idx, tile in enumerate(winners):
            if isinstance(tile, Ball):
                winners[idx] = tile.owner
        [print(tiles[i*self.ROW_LEN:(i+1)*self.ROW_LEN], '\t', winners[i *
               self.WIN_COL_LEN:(i+1)*self.WIN_COL_LEN]) for i in range(self.num_players)]

    def update(self, idx: int, value: Ball | int) -> None:
        """ Updates tile value at index=idx

        Args:
            idx (int): tile index
            value (Ball|int): value
        """
        self.tiles[idx] = value

    def get_balls(self) -> list[Ball]:
        """Returns all ball instances on board tiles (exculdes win columns)

        Returns:
            list[[Ball]: list of ball instances
        """
        balls: list[Ball] = []
        for tile in range(self.len):
            if self.is_occupied(tile):
                ball = self.query_ball_at_idx(tile)
                if not isinstance(ball, Ball):
                    raise TypeError("Expected Ball type")
                balls.append(ball)
        return balls

    def handle_collison(self, idx: int) -> None:
        """ Jails ball at tile index=idx updating position and state

        Args:
            idx (int): tile index
        """
        target_ball = self.query_ball_at_idx(idx)
        if not isinstance(target_ball, Ball):
            raise TypeError("Expected Ball type")
        # NOTE: Not needed. There for completion
        self.update(target_ball.position, 0)
        # TODO: Merge upadate position and update state. Have a jailbreak method etc.
        target_ball.upadate_position(-1)
        target_ball.update_state()

    def calculate_move_path(self, ball: Ball, offset: int, team_number:int|None=None, is_five:bool=False) -> list[int]:
        """ Calculates move path for a given ball for a given offset

        Args:
            team_number (int?): optional team number
            is_five (bool): optional if card_value was 5
            ball (Ball): ball instance
            offset (int): offset to move ball by

        Returns:
            list[int]: list of tile indicies
        """
        can_enter_win = True  # By default all can enter winner col
        if is_five and team_number != ball.team_number:
            can_enter_win = False  # If 5 & not same team then cant enter

        start = ball.position
        end = ball.position + offset
        # Starting tile for that win player's win column
        col_start = self.len + (self.WIN_COL_LEN*(ball.owner-1))
        col_end = col_start + self.WIN_COL_LEN
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
