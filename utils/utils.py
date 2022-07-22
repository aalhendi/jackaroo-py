from logging import warning
import random
from typing import Dict, List, Tuple
from ball import Ball, States
from board import Board
import numpy.typing as npt
import numpy as np

def calculate_move_path(ball:Ball, board:Board, offset:int) -> list[int]:
    start = ball.position
    end = ball.position + offset

    #TODO: Handle victory paths & conditions
    
    # if offset == 5:
    #TODO: handle 5s and 7s
        # raise NotImplemented("Cant find 5 paths")
    
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

# def can_burn(next_hand_length:int) -> bool:
#     if next_hand_length > 0:
#         return True
#     else:
#         return False

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

def jailbreak(board:Board, ball:Ball, all_balls:List[List[Ball]]) -> None:
    if is_occupied(board, ball.base_idx):
        handle_collison(board, all_balls, ball.base_idx)

    ball.position = ball.base_idx
    board.update(ball.base_idx, ball.owner)
    ball.update_state()

def burn(hand:npt.NDArray[np.int8]) -> Tuple[npt.NDArray[np.int8], int]:
    #TODO: skip next guys turn. Could be a game method that checks hand lengths in can_play_turn()
    #TODO: add burned card to stack
    print(hand)
    np.random.shuffle(hand)
    burned = hand[0]
    hand = hand[1:]
    return hand, burned



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

