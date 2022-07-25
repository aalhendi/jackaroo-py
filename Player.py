from ball import Ball
import numpy as np

class Player():
    def __init__(self, base_idx) -> None:
        self.base_idx = base_idx
        self.balls = [Ball(self.base_idx), Ball(self.base_idx), Ball(self.base_idx), Ball(self.base_idx)]
        self.hand = np.array([], dtype=np.int8)
        self.intents = []
        self.intents_map = dict()

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


