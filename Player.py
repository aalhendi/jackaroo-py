from typing import Dict, List
from ball import Ball
import numpy as np
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

            all_intents.append(intents)
        self.intents = all_intents

    def map_intents(self) -> Dict[int, List[str]]:
        intents_map = dict()
        for idx, card in enumerate(self.hand):
            intents_map.update({idx : self.intents[idx]})
        self.intents_map = intents_map
