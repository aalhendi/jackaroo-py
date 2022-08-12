from typing import List
from Player import Player
from deck import Deck
from board import Board
import numpy as np


class Game():
    # TODO: Impl rounds
    def __init__(self) -> None:
        self.num_players: int = 4
        self.board = Board(self.num_players)
        self.deck = Deck()
        self.turn_order = np.array(
            list(range(self.num_players)), dtype=np.int8)
        self.players = self.create_players()
        self.stack = []  # TODO: IMPLEMENT STACK

    def create_players(self) -> List[Player]:
        players: List[Player] = []
        for i in range(self.num_players):
            players.append(Player(i*19, self.turn_order))
        return players

    def init_game(self):  # TODO: Rename
        self.deck.shuffle()

    def deal_cards(self):
        hands = self.deck.deal()
        for t, idx in enumerate(self.turn_order):
            self.players[t].update_hand(hands[idx])

    def roll_turn_order(self):
        self.turn_order = np.roll(self.turn_order, -1)
        for p in self.players:
            p.set_turn_context(self.turn_order)

    def process_hands(self):
        # TODO: Remove play turn from here
        print("=================================")
        for p in self.turn_order:
            if len(self.players[p].hand) == self.deck.expected_hand_length:
                self.players[p].get_actions()
                self.players[p].check_legal_actions(self.board)
                self.players[p].decide_action()
                print(self.players[p].hand,
                      self.players[p].current_action, sep='\n')
                card = self.players[p].play_action(self.board)
                self.stack.append(card)
            else:
                pass  # Do Nothing if wrong hand_len (burn happened)
            if self.players[p].check_win(self.board):
                raise Exception("GAME OVER!")
        self.board.print()
