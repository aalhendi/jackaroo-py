from logging import warning
from typing import List
from Player import Player
from deck import Deck
import utils.utils as utils
from ball import Ball
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
            p.intents = self.check_legal_intents(p.balls, p.intents)
            p.map_intents()

    def process_intent(self,intent:str, player_balls:List[Ball]):
        all_balls = [p.balls for p in self.players]
        if 'MOVE' in intent:
            #HANDLE MOVE
            offset = int(intent.split(" ")[0].split("=")[-1])
            ball_idx = int(intent.split(" ")[-1].split("=")[-1])
            path = utils.calculate_move_path(player_balls[ball_idx], self.board, offset) #TODO: Check if encoding path at check_legal_intents and calling eval() is cheaper compute
            utils.move(self.board, player_balls[ball_idx], all_balls, path)

        elif 'DISCARD' in intent:
            #HANDLE discard 
            warning("Not implemented DISCARD Processing")
            pass

        elif 'JAILBREAK' in intent:
            ball_idx = int(intent.split(" ")[-1].split("=")[-1])
            utils.jailbreak(self.board, player_balls[ball_idx], all_balls)

        elif 'BURN' in intent:
            warning("Not implemented BURN Processing")
            # burn(next_player_hand)
            pass

        elif 'SWAP' in intent:
            #HANDLE SWAP
            warning("Not implemented SWAP Processing")
            pass
        else:
            raise TypeError(f"Unkown intent {intent}")
    
    #TOOD: trim inputs
    def check_legal_intents(self, player_balls:List[Ball], intents:List[List[str]]) -> List[List[str]]:
        all_balls = [p.balls for p in self.players]

        legal_intents:List[List[str]] = []
        for intent_list in intents:
            legal_intent_list:List[str] = []
            for i in intent_list:
                if 'MOVE' in i:
                    for ball_idx, ball in enumerate(player_balls):
                        offset = int(i.split(' ')[0].split("=")[-1])
                        path = utils.calculate_move_path(ball, self.board, offset)
                        is_legal = utils.is_legal_move(self.board, ball, all_balls, path)
                        if is_legal:
                            legal_intent_list.append(i+ f" ball_idx={ball_idx}")

                elif 'JAILBREAK' in i:
                    for ball_idx, ball in enumerate(player_balls):
                        if ball.can_jailbreak():
                            legal_intent_list.append(i+ f" ball_idx={ball_idx}")

                elif 'BURN' in i:
                        #TODO: Check if last player in with 1 card in round
                        legal_intent_list.append(i)
                
                elif 'SWAP' in i:
                    #HANDLE SWAP
                    pass

                else:
                    raise TypeError(f"Unkown intent {i}")
            legal_intents.append(legal_intent_list)
        return legal_intents