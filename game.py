from typing import List
from Player import Player
from deck import Deck
from board import Board
import numpy as np


class Game():
    def __init__(self) -> None:
        self.num_players: int = 4
        self.board = Board(self.num_players)
        self.deck = Deck()
        self.deck.shuffle()
        self.turn_order = np.array(
            list(range(self.num_players)), dtype=np.int8)
        self.players = self.create_players()
        self.stack = []
        self.skip_next = False

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
        # TODO: Add human player: In place of decide_action, print the legal actions and await selection input from player.
        print("=================================")
        for p in self.turn_order:
            print(
                f"Player Number: {self.players[p].number}", self.players[p].hand, sep='\n')
            if not self.skip_next:
                self.players[p].get_actions()
                self.players[p].check_legal_actions(self.board)
                self.players[p].decide_action()
                action = self.players[p].play_action(self.board)
                if action["verb"] == "BURN":
                    self.skip_next = True
            else:
                action = self.players[p].burn()
                self.skip_next = False

            print(action)
            self.stack.append(action)
            if self.players[p].check_win(self.board):
                raise Exception("GAME OVER!")
        self.board.print()
