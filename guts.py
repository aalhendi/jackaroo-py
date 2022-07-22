from enum import Enum
from typing import List, Tuple
import numpy as np
import numpy.typing as npt
import random

#TODO: convert to enum
number_base_dict: dict[int, int] = {
    1 : 0,
    2 : 19,
    3 : 38,
    4 : 57,
}

base_number_dict: dict[int, int] = {
    0 : 1,
    19 : 2,
    38 : 3,
    57 : 4,
}

# STATES
# -1 : Jail
#  0 : Protected
#  1 : Active

class States(Enum):
    JAILED = -1
    PROTECTED = 0
    ACTIVE = 1
    
BOARD_LENGTH = 76
board = np.zeros(76, dtype=np.int8) # Board is a 76 element mask with player balls as non-zero ints.

def query_ball_at_idx(board, idx):
    print("QUERIER HERE:",idx, board[idx], board[idx] != 0, [ball.position == idx for ball in players[board[idx - 1]].balls] ,[ball.__dict__ for ball in players[board[idx - 1]].balls] )
    for ball in players[board[idx - 1]].balls:
        if ball.position == idx:
            print("Hmm colision")
            return ball

    print("error in query_ball_at idx", ball.__dict__, idx, board[idx])
    return False

def is_occupied(idx):
            # Returns true if non-zero - aka ball present
            return bool(board[idx])

class Player:
    class Ball:
        def __init__(self, base_idx) -> None:
            self.position = -1 #Out of bounds
            self.state = States.JAILED
            self.base_idx = base_idx

        def is_occupied(self, idx):
            # Returns true if non-zero - aka ball present
            return bool(board[idx])

        

        def jailbreak(self):
            #Check if theres someone there
            #TODO: Messy. Refactor.
            if self.is_occupied(board, self.base_idx):
                ball = self.query_ball_at_idx(board,self.base_idx)
                print("Someones on my base. Im Jailbreaking.")
                # return [k for k, v in number_base_dict.items() if v == ball.base_idx][-1], ball_idx, self.handle_collison(ball) #TODO: Fix this impl
            else:
                self.state = States.PROTECTED
                self.position = self.base_idx
                return True

        def handle_collison(self, target_ball):
            board[self.position] = 0
            self.position = target_ball.position
            board[self.position] = base_number_dict[self.base_idx]
            if self.position == self.base_idx:
                self.state = States.PROTECTED
            target_ball.state = States.JAILED
            target_ball.position = States.JAILED.value
            return target_ball


        def can_collide(self, target_ball):
            # Ball not protected
            if target_ball.state == States.ACTIVE:
                return True
            # Protected ball & not your ball
            elif target_ball.state == States.PROTECTED & target_ball.baseIdx != self.base_idx:
                #ball is protected
                return False
            # Its your ball. You messed up (States.PROTECTED & target_ball.baseIdx == self.baseIdx)
            else:
                print("you ate yourself :)")
                return True

        def calculate_true_move_path(self, offset):
            start = self.position
            end = self.position + offset
            #TODO: handle 5s
            if offset == 5:
                print("Not implemented")
            #handle victory
            if end > BOARD_LENGTH - 1: #TODO: check if off by one error: 0 indexing
                one = list(range(start +1, BOARD_LENGTH)) #left inclusive
                two = list(range(0, abs(offset) - len(one))) #loop around the board
                path = [*one, *two]
                print("looper", start, end, path)
            elif self.position + offset < 0:
                one = list(range(start-1, -1, -1)) #inclusive left exclusive right to 0
                two = list(range(BOARD_LENGTH - 1, BOARD_LENGTH - (abs(offset) - len(one)), -1)) #TODO: Check off by one error
                path = [*one, *two]
                print("reverse looper", start, end, path)
            else:
                print("calc true path pos, off, end", self.position, offset, self.position + offset)
                if offset > 0:
                    path = list(range(start +1, end +1))
                    print("standard forward", start, end, path)
                else:
                    path = list(range(start-1, end, -1))
                    print("standard backwards", start, end, path)
                
            return path


        def check_path(self, path):
            # Handle Obstructions in path (Protected balls) have a path func that iterates every loc and checks state. will be useful for 13
            obstacles = []
            for i in path:
                if self.is_occupied(board, i):
                    print("check path rbeaker")
                    ball = query_ball_at_idx(board, board[i])
                    if ball.state == States.PROTECTED and ball.base_idx != self.base_idx: #Not my ball
                        print("Movement blocked", ball.__dict__, self.__dict__, path, board)
                        return False, [] #Invalid Path
                    else:
                        obstacles.append(ball)
            return True, obstacles

        def move(self, path):
            #Valid path
            #TODO: HANDLE KING (13 offset)
            print(path, path[-1], "da path")
            if self.is_occupied(board, path[-1]):
                print("Move breaker")
                ball = self.query_ball_at_idx(path[-1])
                print("Target Occupied", self.__dict__, path, ball.__dict__)
                if self.can_collide(ball):
                    self.handle_collison(ball) #Sets new positions and states
                else:
                    print("error in move -> can_collide -> handle_collison")
                    return False
            else:
                #Not occupied
                board[self.position] = 0
                self.position = path[-1]
                board[self.position] = base_number_dict[self.base_idx]
                if self.position == self.base_idx:
                    self.state = States.PROTECTED

    def __init__(self, number: int) -> None:
        self.number: int = number
        self.base: int = number_base_dict[self.number] # The point which is the home base start point of player
        self.cards: List[int] = []
        self.balls = [self.Ball(self.base), self.Ball(self.base), self.Ball(self.base), self.Ball(self.base)]

    

    def draw(self, deck: npt.NDArray[np.int8], round_number: int) -> npt.NDArray[np.int8]:
        if round_number == 3: #last round
            self.cards = deck[ len(deck)-5: ].tolist()
            deck = deck[ : -5]
        else:
            self.cards = deck[ len(deck)-4: ].tolist()
            deck = deck[ : -4]
        
        return deck
    
    def get_intents(self, board, card):
        jailed: int = sum(list([ball.state == States.JAILED for ball in self.balls])) # Number of balls in jail
        # on_board: npt.NDArray[np.int8] = np.where(board > 0)[0].astype(np.int8) # idx of all balls on board
        on_board = []
        fiveable = []
        intents = [f'MOVE {card}']
        print(*board.reshape((4,19)), sep='\n')

        for idx in range(len(board)):
            if is_occupied(board, idx):
                ball = query_ball_at_idx(board, idx)
                on_board.append(ball)
                if ball.state == States.ACTIVE or ball.base_idx == self.base:
                    fiveable.append(ball)
                # print("fiveables", fiveable)
        print("Legal team here, ", on_board)

        if jailed == 4: # All jailed, can only play JB moves
            match card:
                case 5 if len(fiveable) > 0:
                    intents = [f'MOVE {card}']
                case 5:
                    intents = []
                case 1:
                    intents = [f'JAILBREAK {card}']
                case 13:
                    intents = [f'JAILBREAK {card}']
                case 10: 
                    intents = [f'BURN {card}']
                case _:
                    intents = []
        elif jailed < 4 and jailed > 0:
            match card:
                case 1:
                    intents = [f'MOVE {1}', f'MOVE {11}', f'JAILBREAK {card}']
                case 4:
                    intents = [f'MOVE {-card}']
                case 5 if len(fiveable) > 0:
                    intents = [f'MOVE {card}']
                case 5:
                    intents = []
                case 7:
                    # TODO: Handle 7
                    intents = [f'MOVE {card}']
                case 10:
                    # TODO: Handle last person in round 10
                    intents.append(f'BURN {card}')
                case 11:
                    intents = [f'SWAP {card}']
                case 13:
                    intents.append(f'JAILBREAK {card}')
        else: # all ur balls balls active
            match card:
                case 1:
                    intents = [f'MOVE {1}', f'MOVE {11}']
                case 4:
                    intents = [f'MOVE {-card}']
                case 5 if len(fiveable) > 0:
                    intents = [f'MOVE {card}']
                case 5:
                    intents = []
                case 7:
                    # TODO: Handle 7
                    intents = [f'MOVE {card}']
                case 10:
                    # TODO: Handle last person in round 10
                    intents = [f'MOVE {card}', f'BURN {card}']
                case 11:
                    intents = [f'SWAP {card}']

        return intents 

    
    def check_legal_moves(self, board: npt.NDArray[np.int8]) -> dict[int, str]:
        # TODO: handle victory locs
        # TODO: Handle 7
        card_idx_intent_dict = dict()
        for idx, card in enumerate(self.cards):
            intents = self.get_intents(board, card)        
            if len(intents) > 0:
                card_idx_intent_dict.update({idx: intents})
        #TODO: Run simul on all balls to see which are legal moves and on which balls
        return card_idx_intent_dict 

    def decide_card(self, board: npt.NDArray[np.int8], legal_idx: List[int]) -> Tuple[int, str]:
        if len(legal_idx) <= 0:
            # No legal moves were found, gotta discard
            #TODO: Order of discards should be considered
            idx = int(np.random.randint(0, len(self.cards)))
            return idx, f"DISCARD {self.cards[idx]}", None, None

        #Legal Moves
        #TODO: Impl board & decision
        # SHUFFLE START
        keys = list(legal_idx.keys())
        random.shuffle(keys)
        shuffled_legal_idx = dict()
        for key in keys:
            shuffled_legal_idx.update({key: legal_idx[key]})
        # SHUFFLE END

        #Loop through cards
        for key, intents in shuffled_legal_idx.items():
            #Force JB
            if intents: #TODO: is this needed?
                # Loop through intents if any
                for intent in intents:
                    if 'JAILBREAK' in intent:
                        print("I have decided to JB")
                        return key, intent, None, None
                
                    # Not JB pick random intent from first card of shuffled cards 
                    else:
                        intent = random.choice(intents)
                        if 'MOVE' in intent:
                            # Find which balls can move
                            moveable = []
                            for ball in self.balls:
                                if ball.state != States.JAILED:
                                    moveable.append(ball)
                            ball_options = dict()
                            if len(moveable) > 0:
                                for ball in moveable:
                                    offset = int(intent.split(" ")[-1])
                                    path = ball.calculate_true_move_path(offset)
                                    can_move, obstacles = ball.check_path(board, path)
                                    if can_move:
                                        ball_options.update({ball:path})
                                # Select random moveable ball
                                print("Moveable balls", len(ball_options), ball_options)
                                ball = random.choice(list(ball_options.keys()))
                                path = ball_options.pop(ball)
                                return key, intent, ball, path
                else:
                    print(f"idk what this move is idx:{key}, val{intent}")
                    return key, intent, None, None
            else:
                raise Exception("NO intents lmao")



    def play_card(self, idx: int) -> int:
        return self.cards.pop(idx) # Deletes card at index AND returns it to be played

class Game:
    def __init__(self,) -> None:
        self.deck: npt.NDArray[np.int8] = np.repeat(np.linspace(1, 13, 13, dtype=np.int8), 4)
        self.round: int = 0
        # self.players = np.array(players)
        self.stack:List[int] = [] # Stack of played cards
    
    def shuffle_deck(self) -> None:
        np.random.shuffle(self.deck)

    def jailbreak(self, board, player: Player, ball_idx: np.intp) -> None:
        status = player.balls[ball_idx].jailbreak(board)
        if status:
            print("Successfull JB")
        else:
            print("Not so lucky trying to JB")
        board[player.base] = player.number 
    
    def process_card(self, player: Player, card: int, intent: str, ball=None, path=None) -> None: 
        self.stack.append(card) # Add the card to the stack of played cards
        #TODO: Refactor into can jailbreak. have func return bool. then have ball returned to pass into self.jailbreak
        player_ball_states = [ball.state == States.JAILED for ball in player.balls]
        if 'JAILBREAK' in intent and any(player_ball_states):
            ball_states = np.array([ball.state.value for ball in player.balls], dtype=np.int8)
            ball_idx = np.argmax(ball_states < 0) # find first jailed ball
            self.jailbreak(board, player, ball_idx)
            return True
        if ('MOVE' in intent) and bool(ball) and bool(path):
            offset = int(intent.split(" ")[-1])
            ball.move(board, path)
        else:
            print('MOVE' in intent, intent, bool(ball), ball, bool(path), path)
            print("nothing to process.... Card played:", card, intent)
        

    def deal_cards(self) -> None:
        self.round += 1
        for p in players:
            self.deck = p.draw(self.deck, self.round)
    
    def prep_dealer(self) -> None:
        players = np.roll(players, 1) # Player on the right now deals
        self.deck = np.repeat(np.linspace(0, 12, 13, dtype=np.int8), 4) # Cards are recollected by dealer
        self.shuffle_deck() # Deck is reshuffled
    
    def play_turn(self, player: Player) -> None:
        card_idx_intent_dict = player.check_legal_moves(board)
        print(f"Player {player.number}'s hand:",card_idx_intent_dict)
        card_idx, intent, ball, path = player.decide_card(board, card_idx_intent_dict)
        print("Final decision: ", card_idx, intent)
        card = player.play_card(card_idx)
        if ball:
            self.process_card(player, card, intent, ball, path)
        else:
            self.process_card(player, card, intent)


players = [Player(n) for n in [1, 2, 3, 4]]
