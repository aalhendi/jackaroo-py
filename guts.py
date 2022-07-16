from typing import List, Literal
import numpy as np
from enum import Enum
import numpy.typing as npt

JAILMOVES = [1, 5, 10, 13] # Ace and King can jailbreak ball, 10 to burn and 5 move all
class Color(Enum):
     RED = 0
     GREEN = 19
     BLUE = 38
     BLACK = 57

class Player:
    def __init__(self, color: Color) -> None:
        self.color: Color = color # The point which is the home base start point of player
        self.cards: List[int] = []
        self.balls: npt.NDArray[np.int8] = np.full(4, -1, dtype=np.int8) #NOTE: Everyone starts in jail

    def draw(self, deck: npt.NDArray[np.int8], round_number: int) -> npt.NDArray[np.int8]:
        if round_number == 3: #last round
            self.cards = deck[ len(deck)-5: ].tolist()
            deck = deck[ : -5]
        else:
            self.cards = deck[ len(deck)-4: ].tolist()
            deck = deck[ : -4]
        
        return deck
    
    def check_legal_moves(self) -> npt.NDArray[np.int8]:
        # TODO: handle victory locs
        jailed: int = (self.balls < 0).sum() # Number of balls in jail
        legal_idx: npt.NDArray[np.int8] = np.array([])
        if jailed == 4: # Can ONLY play jail moves:
            legal_idx = np.array([idx for idx, val in enumerate(self.cards) if val in JAILMOVES]) # return idx of all jail moves
        elif jailed < 4 and jailed > 0: # Can play jail & movement
            # TODO: Check ball pos and blocks
            pass
        else: # Nothing in jail. Can play everything
            # TODO: Check ball pos and blocks
            pass
        
        return legal_idx

    def play_card(self, idx: int) -> int:
        if idx <= len(self.cards): # Checks if card index is within 4 or 5 cards in hand
            return self.cards.pop(idx) # Deletes card at index AND returns it to be played
        else:
            raise ValueError("Invalid card index")

class Game:
    def __init__(self, players:List[Player]) -> None:
        self.board: npt.NDArray[np.int8] = np.linspace(0, 75, 76, dtype=np.int8)
        self.deck: npt.NDArray[np.int8] = np.repeat(np.linspace(0, 12, 13, dtype=np.int8), 4)
        self.round: int = 0
        self.players = np.array(players)
        self.stack:List[int] = [] # Stack of played cards
        self.balls:dict[Player, npt.NDArray[np.int8]] = {
            players[0] : players[0].balls,
            players[1] : players[1].balls
        }
    
    def shuffle_deck(self) -> None:
        np.random.shuffle(self.deck)

    def check_round(self) -> int:
        deck_rounds_dict: dict[int, int] = {
            52 : 1,
            36 : 2,
            20 : 3,
        }
        return deck_rounds_dict[len(self.deck)]
                

    def deal_cards(self) -> None:
        round_number = self.check_round()
        for p in self.players:
            self.deck = p.draw(self.deck, round_number)
    
    def prep_dealer(self) -> None:
        self.players = np.roll(self.players, 1) # Player on the right now deals
        self.deck = np.repeat(np.linspace(0, 12, 13, dtype=np.int8), 4) # Cards are recollected by dealer
        self.shuffle_deck() # Deck is reshuffled

    


