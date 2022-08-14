# TODO: Fix these ghetto tests...

import numpy as np
from game import Game
from utils.actions import action_map

game = Game()  # TODO: Impl this into game
deck = game.deck

for i in game.turn_order:
    game.players[i].hand = np.array([1, 4, 3, 2], dtype=np.int8)

    action = action_map["1"][2]
    action.update({"ball_idx": 1})
    game.players[i].current_action = action
    card = game.players[i].play_action(game.board)
    game.stack.append(card)

    action = action_map["4"][0]
    action.update({"ball_pos": game.players[i].base_idx, "path": game.board.calculate_move_path(
        game.players[i].balls[1], -4)})
    game.players[i].current_action = action
    card = game.players[i].play_action(game.board)
    game.stack.append(card)

game.board.print()
game.deck.expected_hand_length = 2  # 4 - 2 cards played
print("====================== LEGIT ================")
game.process_hands()
game.deck.decrement_hand_length()
game.process_hands()
