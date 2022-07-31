from ast import literal_eval
from logging import warning
import random
from typing import List
from ball import Ball
import numpy as np

from board import Board

class Player():
    def __init__(self, base_idx) -> None:
        self.base_idx = base_idx
        self.balls = [Ball(self.base_idx), Ball(self.base_idx), Ball(self.base_idx), Ball(self.base_idx)]
        self.hand = np.array([], dtype=np.int8)
        self.current_action = dict()
        self.actions = []

    # def __repr__(self) -> str:
    #     p_dict = self.__dict__
    #     myballs =  [ball.__repr__ for ball in self.balls]
    #     p_dict['balls'] = myballs
    #     return json.dumps(p_dict)

    def update_hand(self, new_hand):
        self.hand = new_hand

    def burn(self) -> int:
        #TODO: skip next guys turn. Could be a game method that checks hand lengths in can_play_turn()
        np.random.shuffle(self.hand)
        burned = self.hand[0]
        self.hand = self.hand[1:]
        return burned
    
    def remove_card(self, idx:int) -> int:
        hand:List = self.hand.tolist()
        removed = hand.pop(idx)
        self.hand = np.array(hand, dtype=np.int8)
        return removed
    
    def decide_action(self):
        #TODO: Impl basic set of rules?
        #Check if theres at least one card to be played
        if len(self.actions) == 0:
            card_idx = random.randrange(len(self.hand))
            card_value = self.hand[card_idx]
            action = self.create_action(card_idx, card_value, "DISCARD")
            self.current_action = action
            return

        action = random.choice(self.actions)
        self.current_action = action

    def clear_actions(self)->None:
        self.current_action = dict()
        self.actions= []

    def play_action(self, board:Board):
        verb = self.current_action['verb']
        if verb == "MOVE":
            ball_idx = self.current_action["ball_idx"]
            path = self.current_action["path"]
            self.balls[ball_idx].move(path, board)
        
        elif 'JAILBREAK' == verb:
            ball_idx = self.current_action["ball_idx"]
            self.balls[ball_idx].jailbreak(board)

        elif 'BURN' == verb:
            warning("Not implemented BURN Processing")
            # burn(next_player_hand)
            pass

        elif 'SWAP' == verb:
            ball_idx = self.current_action["ball_idx"]
            target_ball_pos = self.current_action["target_ball_pos"]
            b1 = self.balls[ball_idx]
            b2 = board.query_ball_at_idx(target_ball_pos)
            b1.swap(b2, board)

        elif verb == 'DISCARD':
            pass #Nothing to do for a discard.

        else:
            raise TypeError(f"Unkown action {self.current_action}")

        card_idx = self.current_action['card_idx']
        card = self.remove_card(card_idx)
        self.clear_actions()
        return card
    
    def create_action(self, card_idx, card_value, verb, offset=None, target=None):
        #TODO: Use kwargs or clean up conditionals 
        if offset:
            return dict({"card_idx":card_idx, "card_value":card_value, "verb": verb, "offset":offset})
        elif target:
            return dict({"card_idx":card_idx, "card_value":card_value, "verb": verb, "target":target})
        else:
            return dict({"card_idx":card_idx, "card_value":card_value, "verb": verb})

    def get_actions(self):
        actions = []
        for card_idx, card_value in enumerate(self.hand):
            verb = "MOVE"
            offset = card_value
            if card_value not in [1, 4, 10, 11, 13]:
                card = self.create_action(card_idx, card_value, verb, offset)
                actions.append(card)
            else:
                if card_value == 1:
                    card = self.create_action(card_idx, card_value, verb, offset)
                    actions.append(card)
                    card = self.create_action(card_idx, card_value, verb, offset=11) #Create 2nd one for Ace
                    actions.append(card)
                    card = self.create_action(card_idx, card_value, verb="JAILBREAK") #Jailbreak
                    actions.append(card)
                elif card_value == 4:
                    offset = -card_value
                    card = self.create_action(card_idx, card_value, verb, offset)
                    actions.append(card)
                elif card_value == 10:
                    card = self.create_action(card_idx, card_value, "BURN")
                    actions.append(card)
                elif card_value == 11:
                    card = self.create_action(card_idx, card_value, "SWAP")
                    actions.append(card)
                elif card_value == 13:
                    card = self.create_action(card_idx, card_value, verb="JAILBREAK") #Jailbreak
                    actions.append(card)
        self.actions = actions
        return

    def check_legal_actions(self, board):
        legal_actions = []
        for action in self.actions:
            if action["verb"] == "MOVE":
                for ball_idx, ball in enumerate(self.balls):
                    offset = action["offset"]
                    path = board.calculate_move_path(ball, offset)
                    is_legal = ball.is_legal_move(path, board)
                    if is_legal:
                        new_action = action
                        new_action['path'] = path
                        new_action['ball_idx'] = ball_idx
                        legal_actions.append(new_action)
            elif action['verb'] == "JAILBREAK":
                for ball_idx, ball in enumerate(self.balls):
                            if ball.can_jailbreak():
                                new_action = action
                                new_action['ball_idx'] = ball_idx
                                legal_actions.append(new_action)
            elif action['verb'] == 'BURN':
                #TODO: Check if last player in with 1 card in round
                legal_actions.append(action)
            elif action['verb'] == "SWAP":
                for ball_idx, ball in enumerate(self.balls):
                            swappable = ball.can_swap(board)
                            if swappable:
                                for b in swappable:
                                    new_action = action
                                    new_action['ball_idx'] = ball_idx
                                    new_action['target_ball_pos'] = b.position
                                    legal_actions.append(new_action)
            else:
                raise TypeError(f"Unkown verb in action {action}")
        self.actions = legal_actions
        return 
        