from typing import List
from Player import Player
from deck import Deck
from board import Board
from collections import deque


class Game():
    def __init__(self, num_players=4) -> None:
        self.num_players: int = num_players
        self.num_teams: int = self.num_players//2
        self.board = Board(self.num_players)
        self.deck = Deck(self.num_players)
        self.deck.shuffle()
        self.turn_order = deque(list(range(self.num_players)))
        self.players = self.create_players()
        self.stack = []
        self.skip_next = False
        self.is_over = False

    def create_players(self):
        players = [Player(i*19, self.turn_order, i % self.num_teams)
                   for i in range(self.num_players)]
        for i in range(self.num_teams):
            players[i].set_teammate_balls(players[i+self.num_teams].balls)
            players[i+self.num_teams].set_teammate_balls(players[i].balls)
        return players

    def deal_cards(self):
        hands = self.deck.deal()
        for t, idx in enumerate(self.turn_order):
            self.players[t].update_hand(hands[idx])

    def roll_turn_order(self):
        self.turn_order.rotate(-1)
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
                self.players[p].decide_action(policy="random")
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

    def run(self, step=False):
        # Play till winner
        while not self.is_over:
            # Play a whole deck, 4-4-5
            while self.deck.rounds_remaining > 0 and not self.is_over:
                self.deal_cards()
                self.deck.decrement_rounds()
            # Play whole hand

                while self.deck.expected_hand_length > 0 and not self.is_over:
                    # Every player plays card
                    self.process_hands()
                    self.deck.decrement_hand_length()
                    print(
                        f"rounds left: {self.deck.rounds_remaining}, exp_hand: {self.deck.expected_hand_length}, turn_order {self.turn_order}")
                    if step:
                        input("Completed Hand Cycle\n")
        # Pass the deck, change the delaer
            self.roll_turn_order()
            self.deck.reset()
            self.deck.shuffle()
            if step:
                input("Completed Deck Cycle\n")
        return [player.check_win(self.board) for player in self.players]
