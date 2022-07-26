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
        self.intents = []
        self.intents_map = dict()
        self.current_intent = ""

    # def __repr__(self) -> str:
    #     p_dict = self.__dict__
    #     myballs =  [ball.__repr__ for ball in self.balls]
    #     p_dict['balls'] = myballs
    #     return json.dumps(p_dict)

    def update_hand(self, new_hand):
        self.hand = new_hand

    def get_intents(self):
        all_intents = []
        for card_idx, card in enumerate(self.hand):
            intents = [f'MOVE={card} CARD_IDX={card_idx}']
            if card == 1:
                intents = [f'MOVE=1 CARD_IDX={card_idx}', f'MOVE=11 CARD_IDX={card_idx}', f'JAILBREAK CARD_IDX={card_idx}']
            elif card == 4:
                intents = [f'MOVE={-card} CARD_IDX={card_idx}']
            elif card == 10:
                intents.append(f'BURN CARD_IDX={card_idx}')
            elif card == 11:
                intents = [f'SWAP CARD_IDX={card_idx}']
            elif card == 13:
                intents.append(f'JAILBREAK CARD_IDX={card_idx}')

            all_intents.append(intents)
        self.intents = all_intents

    def map_intents(self) -> None:
        intents_map = dict()
        for idx, _ in enumerate(self.hand):
            intents_map.update({idx : self.intents[idx]})
        self.intents_map = intents_map

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

    def decide_intent(self):
        #TODO: Impl basic set of rules?
        #Flatten intents:
        all_intents = []
        for _, intents in self.intents_map.items():
            for i in intents:
                all_intents.append(i)

        #Check if theres at least one card to be played
        if len(all_intents) == 0:
            #TODO: Order of discards should be considered
            card_idx = random.choice(list(self.intents_map.keys()))
            self.current_intent = f"DISCARD CARD_IDX={card_idx}"
            return

        card_idx = random.choice(list(self.intents_map.keys()))

        #Ensures no card idx with 0 intents is selected
        while len(self.intents_map[card_idx]) == 0:
            card_idx = random.choice(list(self.intents_map.keys()))

        self.current_intent = random.choice(self.intents_map[card_idx])

    def clear_intent(self)->None:
        self.current_intent = ""
        self.intents = []
        self.intents_map = dict()

    def play_turn(self, board:Board):
        if 'MOVE' in self.current_intent:
            #HANDLE MOVE
            parts = self.current_intent.split(" ", 3)
            ball_idx = int(parts[2].split("=")[-1])
            path = literal_eval(parts[3].split("=")[-1])
            card_idx = int(parts[1].split("=")[-1])
            self.balls[ball_idx].move(path, board)

        elif 'DISCARD' in self.current_intent:
            card_idx = int(self.current_intent.split(" ")[-1].split("=")[-1])

        elif 'JAILBREAK' in self.current_intent:
            parts = self.current_intent.split(" ")
            card_idx = int(parts[1].split("=")[-1])
            ball_idx = int(parts[-1].split("=")[-1])
            self.balls[ball_idx].jailbreak(board)

        elif 'BURN' in self.current_intent:
            card_idx = int(self.current_intent.split(" ")[-1].split("=")[-1])
            warning("Not implemented BURN Processing")
            # burn(next_player_hand)
            pass

        elif 'SWAP' in self.current_intent:
            parts = self.current_intent.split(" ")
            card_idx = int(parts[1].split("=")[-1])
            b1_idx = int(parts[2].split("=")[-1])
            b2_pos = int(parts[3].split("=")[-1])
            b1 = self.balls[b1_idx]
            b2 = board.query_ball_at_idx(b2_pos)
            b1.swap(b2, board)

        else:
            raise TypeError(f"Unkown intent {self.current_intent}")

        self.clear_intent()
        card = self.remove_card(card_idx)
        return card

    def check_legal_intents(self, board:Board) -> List[List[str]]:
        legal_intents:List[List[str]] = []
        for intent_list in self.intents:
            legal_intent_list:List[str] = []
            for i in intent_list:
                if 'MOVE' in i:
                    for ball_idx, ball in enumerate(self.balls):
                        offset = int(i.split(' ')[0].split("=")[-1])
                        path = board.calculate_move_path(ball, offset)
                        is_legal = ball.is_legal_move(path, board)
                        if is_legal:
                            legal_intent_list.append(i+ f" ball_idx={ball_idx} path={path}")

                elif 'JAILBREAK' in i:
                    for ball_idx, ball in enumerate(self.balls):
                        if ball.can_jailbreak():
                            legal_intent_list.append(i+ f" ball_idx={ball_idx}")

                elif 'BURN' in i:
                        #TODO: Check if last player in with 1 card in round
                        legal_intent_list.append(i)

                elif 'SWAP' in i:
                    for ball_idx, ball in enumerate(self.balls):
                        swappable = ball.can_swap(board)
                        for b in swappable:
                            legal_intent_list.append(i+ f" ball_idx={ball_idx} target_ball_pos={b.position}")

                else:
                    raise TypeError(f"Unkown intent {i}")
            legal_intents.append(legal_intent_list)
        
        self.intents = legal_intents
    