from ast import literal_eval
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
        for card in self.hand:
            intents = [f'MOVE={card}']
            if card == 1:
                intents = [f'MOVE=1', f'MOVE=11', f'JAILBREAK']
            elif card == 4:
                intents = [f'MOVE={-card}']
            elif card == 10:
                intents.append(f'BURN')
            elif card == 11:
                intents = [f'SWAP']
            elif card == 13:
                intents.append(f'JAILBREAK')

            all_intents.append(intents)
        self.intents = all_intents

    def map_intents(self) -> None:
        intents_map = dict()
        for idx, _ in enumerate(self.hand):
            intents_map.update({idx : self.intents[idx]})
        self.intents_map = intents_map

    def burn(self) -> int:
        #TODO: skip next guys turn. Could be a game method that checks hand lengths in can_play_turn()
        #TODO: add burned card to stack
        np.random.shuffle(self.hand)
        burned = self.hand[0]
        self.hand = self.hand[1:]
        return burned

    def decide_intent(self):
        # Tuple[int, str] return type
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
            self.current_intent = "DISCARD"
            return card_idx

        card_idx = random.choice(list(self.intents_map.keys()))

        #Ensures no card idx with 0 intents is selected
        while len(self.intents_map[card_idx]) == 0:
            card_idx = random.choice(list(self.intents_map.keys()))

        self.current_intent = random.choice(self.intents_map[card_idx])

        return card_idx 

    def clear_intent(self)->None:
        self.current_intent = ""

    def process_intent(self, cardIdx:int, board:Board):
        if 'MOVE' in self.current_intent:
            #HANDLE MOVE
            ball_idx = int(self.current_intent.split(" ")[1].split("=")[-1])
            path = literal_eval(self.current_intent.split(" ")[-1].split("=")[-1])
            self.balls[ball_idx].move(path, board)

        elif 'DISCARD' in self.current_intent:
            #HANDLE discard
            warning("Not implemented DISCARD Processing")
            pass

        elif 'JAILBREAK' in self.current_intent:
            ball_idx = int(self.current_intent.split(" ")[-1].split("=")[-1])
            self.balls[ball_idx].jailbreak(board)

        elif 'BURN' in self.current_intent:
            warning("Not implemented BURN Processing")
            # burn(next_player_hand)
            pass

        elif 'SWAP' in self.current_intent:
            #HANDLE SWAP
            warning("Not implemented SWAP Processing")
            pass
        else:
            raise TypeError(f"Unkown intent {self.current_intent}")

        self.clear_intent()

    def check_legal_intents(self, board:Board) -> List[List[str]]:
        legal_intents:List[List[str]] = []
        for intent_list in self.intents:
            legal_intent_list:List[str] = []
            for i in intent_list:
                if 'MOVE' in i:
                    for ball_idx, ball in enumerate(self.balls):
                        offset = int(i.split(' ')[0].split("=")[-1])
                        path = board.calculate_move_path(ball, offset)
                        is_legal = self.is_legal_move(ball, path, board)
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
                    #HANDLE SWAP
                    pass

                else:
                    raise TypeError(f"Unkown intent {i}")
            legal_intents.append(legal_intent_list)
        
        self.intents = legal_intents
    
    def is_legal_move(self, ball:Ball, path:List[int], board:Board)-> bool:
        obstacles:List[Ball] = []
        if ball.state == States.JAILED:
            return False

        if not path:
            raise LookupError("No path to traverse")

        #TODO: Handle victory legal moves

        for i in path:
            if board.is_occupied(i):
                obstacles.append(board.query_ball_at_idx(i))

        if obstacles:
            problem_idx = 99 #NOTE: Just a default so static code checkers dont get mad
            for obstacle_idx, obstacle in enumerate(obstacles):
                if obstacle_idx == 0:
                    problem_idx = obstacle.position+1
                else:
                    if problem_idx > board.len:
                        problem_idx = 0
                    if obstacle.position == problem_idx: #TODO: Handle king?
                        warning("\nIllegal MOVE\n")
                        return False

                if obstacle.position == obstacle.base_idx:
                    warning("This path is obstructed")
                    return False #Illegal move. Obstacle in its base and you cannot overtake it

        return True
