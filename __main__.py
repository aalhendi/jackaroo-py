from logging import warning
import random
import numpy.typing as npt
import numpy as np
from typing import Dict, List, Tuple
from ball import Ball, States
from board import Board
from deck import Deck
from game import Game

deck = Deck()
game = Game() #TODO: Impl this into game
board = Board()
p1 = [Ball(0), Ball(0), Ball(0), Ball(0)]
p2 = [Ball(19), Ball(19), Ball(19), Ball(19)]
p3 = [Ball(38), Ball(38), Ball(38), Ball(38)]
p4 = [Ball(57), Ball(57), Ball(57), Ball(57)]

deck.shuffle()

p1h, p2h, p3h, p4h = deck.deal()

def get_intents(hand: npt.NDArray[np.int8]):
    all_intents = []
    for card in hand:
        intents = [f'MOVE={card}']
        match card:
            case 1:
                intents = [f'MOVE=1', f'MOVE=11', f'JAILBREAK']
            case 4:
                intents = [f'MOVE={-card}']
            case 10:
                intents.append(f'BURN')
            case 11:
                intents = [f'SWAP']
            case 13:
                intents.append(f'JAILBREAK')

        # for i in intents:
        #     all_intents.append(i)
        all_intents.append(intents)
    return all_intents

p1i, p2i, p3i, p4i = [get_intents(p) for p in [p1h, p2h, p3h, p4h]]

def calculate_move_path(ball:Ball, offset:int) -> list[int]:
    start = ball.position
    end = ball.position + offset

    #TODO: Handle victory paths & conditions
    
    if offset == 5:
    #TODO: handle 5s
        raise NotImplemented("Cant find 5 paths")
    
    if end > board.len - 1: 
        one = list(range(start +1, board.len)) #left inclusive
        two = list(range(0, abs(offset) - len(one))) #loop around the board
        path = [*one, *two]
        # print(f"loop from {start} to {end} via {path}")
    elif ball.position + offset < 0:
        one = list(range(start-1, -1, -1)) #inclusive left exclusive right to 0
        two = list(range(board.len - 1, board.len - (abs(offset) - len(one)), -1)) #TODO: Check off by one error
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

def is_occupied(board:Board, idx:int) -> bool:
            # Returns true if non-zero - aka ball present
            return bool(board.tiles[idx])

def query_ball_at_idx(board:Board, all_balls:List[List[Ball]], idx:int) -> Ball | None:
    #unpack list of balls
    player_idx = board.tiles[idx] - 1
    player_balls = all_balls[player_idx]
    for ball in player_balls:
        if ball.position == idx and ball.state != States.JAILED: #TODO: is second condition needed?
            return ball
    
    print("error in query_ball_at idx", ball, idx, board.tiles[idx])
    raise Exception("Something is really broken.")

def is_legal_move(board:Board, ball:Ball, all_balls:List[List[Ball]], path:List[int])-> bool:
    obstacles:List[Ball] = []
    if ball.state == States.JAILED:
        return False

    if not path:
        raise LookupError("No path to traverse")

    #TODO: Handle victory legal moves

    for i in path:
        if is_occupied(board, i):
            obstacles.append(query_ball_at_idx(board, all_balls, i))
    
    if obstacles:
        for obstacle_idx, obstacle in enumerate(obstacles):
            if obstacle_idx == 0: #TODO: Have problem idx defined a few lines above as None. then check if it exists, 
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

def can_jailbreak(ball:Ball)->bool:
    if ball.state == States.JAILED:
        return True
    else:
        return False

def can_burn(next_hand_length:int) -> bool:
    if next_hand_length > 0:
        return True
    else:
        return False

def check_legal_intents(board:Board, player_balls:List[Ball], all_balls:List[List[Ball]], intents:List[List[str]], next_hand_length:int) -> List[List[str]]:
    legal_intents:List[List[str]] = []
    for intent_list in intents:
        legal_intent_list:List[str] = []
        for i in intent_list:
            if 'MOVE' in i:
                for ball_idx, ball in enumerate(player_balls):
                    offset = int(i.split(' ')[0].split("=")[-1])
                    path = calculate_move_path(ball, offset)
                    is_legal = is_legal_move(board, ball, all_balls, path)
                    if is_legal:
                        legal_intent_list.append(i+ f" ball_idx={ball_idx}")

            elif 'JAILBREAK' in i:
                for ball_idx, ball in enumerate(player_balls):
                    if can_jailbreak(ball):
                        legal_intent_list.append(i+ f" ball_idx={ball_idx}")

            elif 'BURN' in i:
                if can_burn(next_hand_length): #TODO: Reimplement & Refactor
                    i += f"={next_hand_length}"
                    legal_intent_list.append(i)
            
            elif 'SWAP' in i:
                #HANDLE SWAP
                pass

            else:
                raise TypeError(f"Unkown intent {i}")
        legal_intents.append(legal_intent_list)
    return legal_intents

print(p1h)
print(p1i)
p1[0].position = 0
p1[0].state = States.PROTECTED
board.update(0, 1)

p1[1].position = 70
p1[1].state = States.ACTIVE
board.update(70, 1)

board.print()
legal_intents = check_legal_intents(board, p1, [p1, p2, p3, p4], p1i, len(p2h))
print(legal_intents)

def handle_collison(board:Board, all_balls:List[List[Ball]], idx:int) -> None:
    target_ball = query_ball_at_idx(board, all_balls, idx)
    board.update(target_ball.position, 0) #NOTE: Not needed. There for completion
    target_ball.position = -1
    target_ball.update_state()


def move(board:Board, ball:Ball, all_balls:List[List[Ball]], path:List[int]) -> None:
    if is_occupied(board, path[-1]):
        handle_collison(board, all_balls,  path[-1])
    
    board.update(ball.position, 0)
    ball.position = path[-1]
    board.update(ball.position, ball.owner)
    ball.update_state()

move(board, p1[0], [p1,p2,p3,p4], [1, 2, 3])
board.print()
print(p1[0])

def jailbreak(board:Board, ball:Ball, all_balls:List[List[Ball]]) -> None:
    if is_occupied(board, ball.base_idx):
        handle_collison(board, all_balls, ball.base_idx)

    ball.position = ball.base_idx
    board.update(ball.base_idx, ball.owner)
    ball.update_state()

jailbreak(board, p1[2], [p1, p2, p3, p4])
board.print()

def burn(hand:npt.NDArray[np.int8]) -> Tuple[npt.NDArray[np.int8], int]:
    #TODO: skip next guys turn. Could be a game method that checks hand lengths in can_play_turn()
    #TODO: add burned card to stack
    print(hand)
    np.random.shuffle(hand)
    burned = hand[0]
    hand = hand[1:]
    return hand, burned
    
p2h, burned = burn(p2h)

def map_intents(hand: npt.NDArray[np.int8], legal_intents:List[List[str]]) -> Dict[int, List[str]]:
    intents_map = dict()
    for idx, card in enumerate(hand):
        intents_map.update({idx : legal_intents[idx]})
    return intents_map


def decide_intent(intents_map:Dict[int, List[str]], hand:npt.NDArray[np.int8]) -> Tuple[int, str]:
    #TODO: Impl basic set of rules
    #Flatten intents:
    all_intents = []
    for idx, intents in intents_map.items():
        for i in intents:
            all_intents.append(i)
    print(all_intents) 

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
        
legal_intents = check_legal_intents(board, p1, [p1, p2, p3, p4], p1i, len(p2h))
intents_map = map_intents(p1h, legal_intents)

card_idx, intent = decide_intent(intents_map, p1h)
print(intent)

def process_intent(board:Board, intent:str, player_balls:List[Ball], all_balls:List[List[Ball]], next_player_hand:npt.NDArray[np.int8]):
    if 'MOVE' in intent:
        #HANDLE MOVE
        offset = int(intent.split(" ")[0].split("=")[-1])
        ball_idx = int(intent.split(" ")[-1].split("=")[-1])
        path = calculate_move_path(player_balls[ball_idx], offset) #TODO: Check if encoding path at check_legal_intents and calling eval() is cheaper compute
        move(board, player_balls[ball_idx], all_balls, path)

    elif 'DISCARD' in intent:
        #HANDLE discard 
        warning("Not implemented DISCARD Processing")
        pass

    elif 'JAILBREAK' in intent:
        ball_idx = int(intent.split(" ")[-1].split("=")[-1])
        jailbreak(board, player_balls[ball_idx], all_balls)

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

print(p1)
board.print()
print(intent)
process_intent(board, intent, p1, [p1, p2, p3, p4], p2h)
board.print()
print(p1)