import numpy.typing as npt
import random
from logging import warning
from typing import List, Dict, Tuple
from Player import Player
from deck import Deck
import utils.utils as utils
from ball import Ball, States
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
        if 'MOVE' in intent:
            #HANDLE MOVE
            offset = int(intent.split(" ")[0].split("=")[-1])
            ball_idx = int(intent.split(" ")[-1].split("=")[-1])
            path = self.calculate_move_path(player_balls[ball_idx], offset) #TODO: Check if encoding path at check_legal_intents and calling eval() is cheaper compute
            self.move(player_balls[ball_idx], path)

        elif 'DISCARD' in intent:
            #HANDLE discard
            warning("Not implemented DISCARD Processing")
            pass

        elif 'JAILBREAK' in intent:
            ball_idx = int(intent.split(" ")[-1].split("=")[-1])
            self.jailbreak(player_balls[ball_idx])

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

    def check_legal_intents(self, player_balls:List[Ball], intents:List[List[str]]) -> List[List[str]]:

        legal_intents:List[List[str]] = []
        for intent_list in intents:
            legal_intent_list:List[str] = []
            for i in intent_list:
                if 'MOVE' in i:
                    for ball_idx, ball in enumerate(player_balls):
                        offset = int(i.split(' ')[0].split("=")[-1])
                        path = self.calculate_move_path(ball, offset)
                        is_legal = self.is_legal_move(ball, path)
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

    def handle_collison(self, idx:int) -> None:
        target_ball = self.board.query_ball_at_idx(idx)
        self.board.update(target_ball.position, 0) #NOTE: Not needed. There for completion
        target_ball.upadate_position(-1) #TODO: Merge upadate position and update state. Have a jailbreak method etc.
        target_ball.update_state()

    def move(self, ball:Ball, path:List[int]) -> None:
        if self.board.is_occupied(path[-1]):
            self.handle_collison(path[-1])

        self.board.update(ball.position, 0)
        ball.upadate_position(path[-1])
        self.board.update(ball.position, ball.owner)
        ball.update_state()

    def jailbreak(self, ball:Ball) -> None:
        if self.board.is_occupied(ball.base_idx):
            self.handle_collison(ball.base_idx)

        ball.upadate_position(ball.base_idx)
        self.board.update(ball.base_idx, ball.owner)
        ball.update_state()

    def decide_intent(self, intents_map:Dict[int, List[str]]):
        # Tuple[int, str] return type
        #TODO: Impl basic set of rules?
        #Flatten intents:
        all_intents = []
        for _, intents in intents_map.items():
            for i in intents:
                all_intents.append(i)

        #Check if theres at least one card to be played
            if len(all_intents) == 0:
                #TODO: Order of discards should be considered
                card_idx = random.choice(list(intents_map.keys()))
                return card_idx, f"DISCARD"

            card_idx = random.choice(list(intents_map.keys()))

            #Ensures no card idx with 0 intents is selected
            while len(intents_map[card_idx]) == 0:
                card_idx = random.choice(list(intents_map.keys()))

            intent = random.choice(intents_map[card_idx])
            return card_idx, intent


    def calculate_move_path(self, ball:Ball, offset:int) -> List[int]:
        start = ball.position
        end = ball.position + offset

        #TODO: Handle victory paths & conditions

        # if offset == 5:
        #TODO: handle 5s and 7s
            # raise NotImplemented("Cant find 5 paths")

        if end > self.board.len - 1:
            one = list(range(start +1, self.board.len)) #left inclusive
            two = list(range(0, abs(offset) - len(one))) #loop around the board
            path = [*one, *two]
            # print(f"loop from {start} to {end} via {path}")
        elif ball.position + offset < 0:
            one = list(range(start-1, -1, -1)) #inclusive left exclusive right to 0
            two = list(range(self.board.len - 1, self.board.len - (abs(offset) - len(one)), -1)) #TODO: Check off by one error
            path = [*one, *two]
            # print(f"reverse loop from {start} to {end} via {path}")
        else:
            if offset > 0:
                path = list(range(start +1, end +1))
                # print(f"Standard forward from {start} to {end} via {path}")
            else:
                path = list(range(start-1, end, -1))
                # print(f"Standard backward from {start} to {end} via {path}")

        return path

    def is_legal_move(self, ball:Ball, path:List[int])-> bool:
        obstacles:List[Ball] = []
        if ball.state == States.JAILED:
            return False

        if not path:
            raise LookupError("No path to traverse")

        #TODO: Handle victory legal moves

        for i in path:
            if self.board.is_occupied(i):
                obstacles.append(self.board.query_ball_at_idx(i))

        if obstacles:
            problem_idx = 99 #NOTE: Just a default so static code checkers dont get mad
            for obstacle_idx, obstacle in enumerate(obstacles):
                if obstacle_idx == 0:
                    problem_idx = obstacle.position+1
                else:
                    if problem_idx > self.board.len:
                        problem_idx = 0
                    if obstacle.position == problem_idx: #TODO: Handle king?
                        warning("\nIllegal MOVE\n")
                        return False

                if obstacle.position == obstacle.base_idx:
                    warning("This path is obstructed")
                    return False #Illegal move. Obstacle in its base and you cannot overtake it

        return True


