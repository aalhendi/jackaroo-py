import numpy as np
from enum import Enum
class Color(Enum):
     RED = 0
     GREEN = 19
     BLUE = 38
     BLACK = 57

class Game:
    def __init__(self, players):
        self.board = np.linspace(0, 75, 76).astype('int32')
        self.deck = np.repeat(np.linspace(0, 12, 13), 4).astype('int32')
        self.round = 0
        self.players = players
        self.dealer = self.players[0]
    
    def shuffle_deck(self):
        np.random.shuffle(self.deck)

    def check_round(self):
        match len(self.deck):
            case 52:
                return 1
            case 36:
                return 2
            case 20:
                return 3

            # If an exact match is not confirmed, this last case will be used if provided
            case _:
                return "Something's wrong with nature"

    def deal_cards(self):
        for p in self.players:
            self.deck = p.draw(self.deck)


class Player:
    def __init__(self, Color):
        self.color = Color # The point which is the home base start point of player
        self.cards = []
        self.balls = np.full((4,4), -1) #NOTE: Everyone starts in jail

    def draw(self, deck):
        if len(deck) <= 20: #last round
            amount = 5
        else:
            amount = 4
        self.cards = deck[ len(deck)-amount : ]
        deck = deck[ : -amount]
        return deck