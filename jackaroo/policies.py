from __future__ import annotations
import random
from typing import Any
import typing
if typing.TYPE_CHECKING:
    from Player import Player # NOTE: This avoids circular dependency
from Ball import Ball, States
from Board import Board


def random_policy(player: Player) -> dict[str, Any]:
    # Check if theres at least one card to be played
    if len(player.actions) == 0:
        card_idx = random.randrange(len(player.hand))
        card_value = player.hand[card_idx]
        action = {"card_value": card_value,
                  "verb": "DISCARD", "is_burn": False}
    else:
        action = random.choice(player.actions)
    return action


def jailbrak_pacifict(player: Player, board: Board) -> dict[str, Any]:
    if len(player.actions) == 0:
        #print("no actions", player.actions)
        card_idx = player.hand.index(min(player.hand))
        card_value = player.hand[card_idx]
        return {"card_value": card_value,
                  "verb": "DISCARD", "is_burn": False}
    else:
        jbs: list[int] = []
        for a in player.actions:
            if a['verb'] == 'JAILBREAK':
                jbs.append(a['card_value'])
        if jbs and any([b.state == States.JAILED for b in player.balls]) and not isinstance(board.query_ball_at_idx(player.base_idx), Ball):
            minimum_jb = min(jbs)
            for a in player.actions:
                if a['card_value'] == minimum_jb and a['verb'] == 'JAILBREAK':
                    return a
            print("something went wrong in jailbreak pacifist")
            return random.choice(player.actions)
        else:
        #    print("jbs might not exist")
            return random.choice(player.actions)
