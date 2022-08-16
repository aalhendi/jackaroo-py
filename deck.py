import random
from typing import List
# NOTE: Can deal cards in more realistic scenarios *observed dealing patterns (two's -> one's -> four's)


class Deck:
    def __init__(self, num_players: int) -> None:
        self.num_players = num_players
        self.cards = list(range(1, 14))*num_players
        self.rounds_remaining = 3
        self.expected_hand_length = 4  # 4 card hands by default

    def shuffle(self) -> None:
        # NOTE: Can use much more advanced shuffles
        random.shuffle(self.cards)

    def deal(self) -> List[List[int]]:
        if self.rounds_remaining == 1:
            self.expected_hand_length = 5
            cards_remaining = []
        else:
            self.expected_hand_length = 4
            cards_remaining = self.cards[self.expected_hand_length *
                                         self.num_players:]

        hands = [self.cards[self.expected_hand_length *
                            i: self.expected_hand_length * (i+1)] for i in range(self.num_players)]
        self.cards = cards_remaining
        return hands

    def reset(self):
        self.cards = list(range(1, 14))*self.num_players
        self.rounds_remaining = 3
        self.expected_hand_length = 4  # 4 card hands by default

    def decrement_hand_length(self):
        self.expected_hand_length -= 1

    def decrement_rounds(self):
        self.rounds_remaining -= 1
