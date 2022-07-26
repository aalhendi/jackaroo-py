import numpy.typing as npt
from logging import warning
from typing import List, Dict, Tuple
from Player import Player
from deck import Deck
from ball import Ball, States
from board import Board

class Game():
    def __init__(self) -> None:
        self.board = Board()
        self.deck = Deck()
        self.players = [Player(0), Player(19), Player(38), Player(57)]
        self.stack = [] #TODO: IMPLEMENT STACK

    def init_game(self): #TODO: Rename
        self.deck.shuffle()
        hands = self.deck.deal()
        for idx, player in enumerate(self.players):
            player.update_hand(hands[idx])

    def process_hands(self):
        for p in self.players:
            p.get_intents()
            p.check_legal_intents(self.board)
            p.map_intents()
            p.decide_intent()
            #play_turn()
