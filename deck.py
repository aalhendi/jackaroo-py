from copy import deepcopy
from typing import List
import numpy as np
import numpy.typing as npt

# NOTE: Can deal cards in more realistic scenarios *observed dealing patterns (two's -> one's -> four's)


class Deck:
    def __init__(self) -> None:
        self.cards: npt.NDArray[np.int8] = np.repeat(
            np.linspace(1, 13, 13, dtype=np.int8), 4)
        self.rounds_remaining = 3
        self.expected_hand_length = 4  # 4 card hands by default

    # NOTE: Couldn't seem to get implementation with __repr__ or __str__
    def print(self) -> None:
        cards = deepcopy(self.cards)
        print(*cards.reshape(4, (4*self.rounds_remaining)+1), sep='\n')

    def shuffle(self) -> None:
        # NOTE: Can use much more advanced shuffles
        np.random.shuffle(self.cards)

    def deal(self) -> List[npt.NDArray[np.int8]]:
        if self.rounds_remaining == 1:
            self.expected_hand_length = 5
            hands = np.split(self.cards[:20], 4)
            self.cards = self.cards[:]
        else:
            self.expected_hand_length = 4
            hands = np.split(self.cards[:16], 4)
            self.cards = self.cards[16:]
        return hands
    
    def reset(self):
        self.cards: npt.NDArray[np.int8] = np.repeat(
            np.linspace(1, 13, 13, dtype=np.int8), 4)
        self.rounds_remaining = 3
        self.expected_hand_length = 4  # 4 card hands by default 

    def decrement_hand_length(self):
        self.expected_hand_length -= 1

    def decrement_rounds(self):
        self.rounds_remaining -= 1
