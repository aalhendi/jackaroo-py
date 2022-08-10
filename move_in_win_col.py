# TODO: Fix these ghetto tests...

import numpy as np
from game import Game

game = Game()  # TODO: Impl this into game
deck = game.deck

game.init_game()
for i in [0, 1, 2, 3]:
    game.players[i].hand = np.array([1, 4, 3, 2], dtype=np.int8)

    jb = game.players[i].create_action(0, 1, "JAILBREAK")
    jb["ball_idx"] = 1
    game.players[i].current_action = jb
    card = game.players[i].play_action(game.board)
    game.stack.append(card)

    jb = game.players[i].create_action(0, 4, "MOVE", offset=-4)
    jb["ball_pos"] = game.players[i].base_idx
    jb["path"] = game.board.calculate_move_path(game.players[i].balls[1], -4)
    game.players[i].current_action = jb
    card = game.players[i].play_action(game.board)
    game.stack.append(card)

game.board.print()
print("====================== LEGIT ================")
game.process_hands()
