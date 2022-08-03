from Player import Player
from deck import Deck
from board import Board

class Game():
    #TODO: Impl rounds
    def __init__(self) -> None:
        self.board= Board()
        self.deck = Deck()
        self.players = [Player(0), Player(19), Player(38), Player(57)]
        self.stack = [] #TODO: IMPLEMENT STACK

    def init_game(self): #TODO: Rename
        self.deck.shuffle()
        hands = self.deck.deal()
        for idx, player in enumerate(self.players):
            player.update_hand(hands[idx])

    def process_hands(self):
        #TODO: Remove play turn from here
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
