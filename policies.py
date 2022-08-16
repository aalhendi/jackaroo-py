import random


def random_policy(actions, hand):
    # Check if theres at least one card to be played
    if len(actions) == 0:
        card_idx = random.randrange(len(hand))
        card_value = hand[card_idx]
        action = {"card_value": card_value,
                  "verb": "DISCARD", "is_burn": False}
    else:
        action = random.choice(actions)
    return action


def homemade_heuristic(actions, hand):
    raise NotImplemented("Homemade Heuristic not implemented...")
