from typing import List
from Player import Player
from deck import Deck
from board import Board
import numpy as np


class Game():
    def __init__(self) -> None:
        self.num_players: int = 4
        self.num_teams: int = self.num_players//2
        self.board = Board(self.num_players)
        self.deck = Deck()
        self.deck.shuffle()
        self.turn_order = np.array(
            list(range(self.num_players)), dtype=np.int8)
        self.players = [Player(i*19, self.turn_order, i%self.num_teams) for i in range(self.num_players)]
        self.stack = []
        self.skip_next = False
        self.is_over = False

    def deal_cards(self):
        hands = self.deck.deal()
        for t, idx in enumerate(self.turn_order):
            self.players[t].update_hand(hands[idx])

    def roll_turn_order(self):
        self.turn_order = np.roll(self.turn_order, -1)
        for p in self.players:
            p.set_turn_context(self.turn_order)

    def check_is_over(self):
        player_wins = [player.check_win(self.board) for player in self.players]
        for t_num in range(self.num_teams):
            if player_wins[t_num] and player_wins[t_num+self.num_teams]:
                self.is_over = True
                return True

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
            if self.check_is_over():
                break
        self.board.print()
