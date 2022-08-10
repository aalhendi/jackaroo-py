from typing import List
from Player import Player
from deck import Deck
from board import Board


class Game():
    # TODO: Impl rounds
    def __init__(self) -> None:
        self.num_players = 4
        self.board = Board(self.num_players)
        self.deck = Deck()
        self.players = self.create_players()
        self.stack = []  # TODO: IMPLEMENT STACK

    def create_players(self) -> List[Player]:
        players: List[Player] = []
        for i in range(self.num_players):
            players.append(Player(i*19))
        return players

    def init_game(self):  # TODO: Rename
        self.deck.shuffle()
        hands = self.deck.deal()
        for idx, player in enumerate(self.players):
            player.update_hand(hands[idx])

    def process_hands(self):
        # TODO: Remove play turn from here
        print("=================================")
        for p in self.players:
            p.get_actions()
            p.check_legal_actions(self.board)
            p.decide_action()
            print(p.hand, p.current_action, sep='\n')
            card = p.play_action(self.board)
            self.stack.append(card)
            if p.check_win(self.board):
                raise Exception("GAME OVER!")
        self.board.print()
