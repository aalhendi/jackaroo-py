from ast import literal_eval
from copy import deepcopy
from logging import warning
import random
from typing import List
from ball import Ball, States
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
        
        elif verb == "FLEXMOVE":
            ball_idx1 = self.current_action["ball_idx1"]
            ball_idx2 = self.current_action["ball_idx2"]
            path1 = self.current_action["path1"]
            path2 = self.current_action["path2"]
            self.balls[ball_idx1].move(path1, board)
            self.balls[ball_idx2].move(path2, board)

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
            if card_value not in [1, 4, 7, 10, 11, 13]:
                card = self.create_action(card_idx, card_value, verb, offset)
                actions.append(card)
            else:
                if card_value == 1:
                    actions += [
                        self.create_action(card_idx, card_value, verb, offset),
                        self.create_action(card_idx, card_value, verb, offset=11),
                        self.create_action(card_idx, card_value, verb="JAILBREAK")
                        ]
                elif card_value == 4:
                    offset = -card_value
                    card = self.create_action(card_idx, card_value, verb, offset)
                    actions.append(card)
                elif card_value == 7:
                    card = self.create_action(card_idx, card_value, "FLEXMOVE")
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

    def check_legal_actions(self, board:Board):
        legal_actions = []
        for action in self.actions:
            if action["verb"] == "MOVE":
                for ball_idx, ball in enumerate(self.balls):
                    offset = action["offset"]
                    path = board.calculate_move_path(ball, offset)
                    is_legal = ball.is_legal_move(path, board)
                    if is_legal:
                        new_action = deepcopy(action)
                        new_action['path'] = path
                        new_action['ball_idx'] = ball_idx
                        legal_actions.append(new_action)

            elif action['verb'] == "FLEXMOVE":
                moveable = self.count_moveable_balls()
                if len(moveable) == 1:
                    offset = 7
                    ball_idx = moveable[0]
                    ball = self.balls[ball_idx]
                    path = board.calculate_move_path(ball, offset)
                    is_legal = ball.is_legal_move(path, board)
                    if is_legal:
                        new_action = deepcopy(action)
                        new_action['verb'] = "MOVE"
                        new_action['path'] = path
                        new_action['ball_idx'] = ball_idx
                        legal_actions.append(new_action)
                    
                elif len(moveable) == 2:
                    ball_idx1 = moveable[0]
                    ball_idx2 = moveable[1]
                    ball1 = self.balls[ball_idx1]
                    ball2 = self.balls[ball_idx2]
                    
                    #Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_idx'] = ball_idx
                            legal_actions.append(new_action)

                    #Handle pairs
                    pair_actions = self.process_flexmove_pairs(board, action, ball1, ball2, ball_idx1, ball_idx2)
                    legal_actions += pair_actions
                
                elif len(moveable) == 3:
                    #Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_idx'] = ball_idx
                            legal_actions.append(new_action)
                    
                    #Handle pairs
                    for i, k in [[0, 1], [0, 2], [1, 2]]:
                        ball_idx1 = moveable[i]
                        ball_idx2 = moveable[k]
                        ball1 = self.balls[ball_idx1]
                        ball2 = self.balls[ball_idx2]
                        pair_actions = self.process_flexmove_pairs(board, action, ball1, ball2, ball_idx1, ball_idx2)
                        legal_actions += pair_actions
                
                elif len(moveable) == 4:
                    #Handle singles
                    offset = 7
                    for ball_idx in moveable:
                        ball = self.balls[ball_idx]
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            new_action = deepcopy(action)
                            new_action['verb'] = "MOVE"
                            new_action['path'] = path
                            new_action['ball_idx'] = ball_idx
                            legal_actions.append(new_action)
                    
                    #Handle pairs
                    for i, k in [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]:
                        ball_idx1 = moveable[i]
                        ball_idx2 = moveable[k]
                        ball1 = self.balls[ball_idx1]
                        ball2 = self.balls[ball_idx2]
                        pair_actions = self.process_flexmove_pairs(board, action, ball1, ball2, ball_idx1, ball_idx2)
                        legal_actions += pair_actions

            elif action['verb'] == "JAILBREAK":
                for ball_idx, ball in enumerate(self.balls):
                            if ball.can_jailbreak():
                                new_action = deepcopy(action)
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
                                    new_action = deepcopy(action)
                                    new_action['ball_idx'] = ball_idx
                                    new_action['target_ball_pos'] = b.position
                                    legal_actions.append(new_action)
            else:
                raise TypeError(f"Unkown verb in action {action}")
        self.actions = legal_actions
        return 
        
    def count_moveable_balls(self):
        moveable = []
        for ball_idx, ball in enumerate(self.balls):
            if ball.state != States.JAILED:
                moveable.append(ball_idx)
        return moveable
    
    def process_flexmove_pairs(self, board:Board, action, ball1:Ball, ball2:Ball, ball_idx1:int, ball_idx2:int):
        actions = []
        for offset1, offset2 in [[6, 1], [5, 2], [4, 3], [3, 4], [2, 5], [1, 6]]:
            path1 = board.calculate_move_path(ball1, offset1)
            is_legal1 = ball1.is_legal_move(path1, board)
            path2 = board.calculate_move_path(ball2, offset2)
            is_legal2 = ball2.is_legal_move(path2, board)
            if is_legal1 and is_legal2:
                new_action = deepcopy(action)
                new_action['ball_idx1'] = ball_idx1
                new_action['ball_idx2'] = ball_idx2
                new_action["offset1"] = offset1
                new_action["offset2"] = offset2
                new_action['path1'] = path1
                new_action['path2'] = path2
                actions.append(new_action)
        return actions