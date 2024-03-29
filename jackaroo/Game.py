from __future__ import annotations
from typing import Any
from Player import Player
from Deck import Deck
from Board import Board
from collections import deque
from utils.logger import logger


class Game():
    def __init__(self, num_players: int, policies:list[str]) -> None:
        self.num_players = num_players
        self.num_teams = self.num_players//2
        self.board = Board(self.num_players)
        self.deck = Deck(self.num_players)
        self.deck.shuffle()
        self.turn_order = deque(list(range(self.num_players)))
        self.players = self.create_players()
        self.stack: list[dict[str, Any]] = []
        self.skip_next: bool = False
        self.is_over: bool = False
        self.rounds_played: int = 0
        self.policies = policies

    def create_players(self) -> list[Player]:
        """ Creates player instances

        Returns:
            list[Player]: list of Player instances
        """
        players = [Player(i*19, self.turn_order, i % self.num_teams)
                   for i in range(self.num_players)]
        for i in range(self.num_teams):
            players[i].set_teammate_balls(players[i+self.num_teams].balls)
            players[i+self.num_teams].set_teammate_balls(players[i].balls)
        return players

    def deal_cards(self) -> None:
        """ Updates hands for player instances """
        hands = self.deck.deal()
        for t, idx in enumerate(self.turn_order):
            self.players[t].update_hand(hands[idx])

    def roll_turn_order(self) -> None:
        """ Rotates turn_order property and updates it in player instances"""
        self.turn_order.rotate(-1)
        for p in self.players:
            p.set_turn_context(self.turn_order)

    def check_is_over(self) -> bool:
        """Checks if 2 players in a team have won

        Returns:
            bool: True if team has won via completing all win columns
        """
        player_wins = [player.check_win(self.board) for player in self.players]
        for t_num in range(self.num_teams):
            if player_wins[t_num] and player_wins[t_num+self.num_teams]:
                self.is_over = True
                return True
        return False

    def process_hands(self) -> None:
        # TODO: Add human player: In place of decide_action, print the legal actions and await selection input from player.
        for p in self.turn_order:
            if not self.skip_next:
                self.players[p].get_actions()
                self.players[p].check_legal_actions(self.board)
#                logger.info(self.players[p])
                self.players[p].decide_action(self.board, policy=self.policies[p])
                action = self.players[p].play_action(self.board)
                if action["verb"] == "BURN":
                    self.skip_next = True
            else:
#                logger.info(self.players[p])
                action = self.players[p].burn()
                self.skip_next = False

#            logger.info(action)
            self.stack.append(action)
            if self.check_is_over():
                break
#        logger.info(self.board)

    def run(self, step: bool = False) -> list[bool]:
        """ Executes full game with specified poilicy till completion

        Args:
            step (bool): await input at every hand cycle

        Returns:
            list[bool]: list of players, True if player has completed win column
        """
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
                    self.rounds_played += 1
#                    logger.info(
#                        f"rounds left: {self.deck.rounds_remaining}, exp_hand: {self.deck.expected_hand_length}, rounds_played: {self.rounds_played}")
                    if step:
                        input("Completed Hand Cycle\n")
        # Pass the deck, change the delaer
            self.roll_turn_order()
            self.deck.reset()
            self.deck.shuffle()
            if step:
                input("Completed Deck Cycle\n")
        return [player.check_win(self.board) for player in self.players]
