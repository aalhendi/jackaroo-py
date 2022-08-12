# TODO: Fix these ghetto tests...

import numpy as np
from game import Game
from utils.actions import action_map

game = Game()  # TODO: Impl this into game
deck = game.deck

game.init_game()
for i in game.turn_order:
    game.players[i].hand = np.array([1, 4, 1, 5], dtype=np.int8)

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

    action = action_map["1"][2]
    action.update({"ball_idx": 0})
    game.players[i].current_action = action
    card = game.players[i].play_action(game.board)
    game.stack.append(card)

game.board.print()
game.deck.expected_hand_length = 1  # 4 - 3 cards played
print("====================== LEGIT ================")
game.process_hands()
