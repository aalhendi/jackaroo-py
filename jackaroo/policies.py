from __future__ import annotations
import random
from typing import Any


def random_policy(actions:list[dict[str, Any]], hand:list[int])-> dict[str, Any]:
    # Check if theres at least one card to be played
    if len(actions) == 0:
        card_idx = random.randrange(len(hand))
        card_value = hand[card_idx]
        action = {"card_value": card_value,
                  "verb": "DISCARD", "is_burn": False}
    else:
        action = random.choice(actions)
    return action


# def homemade_heuristic(actions, hand)-> None:
#     raise NotImplemented("Homemade Heuristic not implemented...")
