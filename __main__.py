from game import Game

game = Game() #TODO: Impl this into game
deck = game.deck

game.init_game()

game.process_hands()

game.board.print()
# for i in [0, 1, 2, 3]:
#     print(game.players[i].balls, game.players[i].hand, 
#     # game.players[i].intents,
#     game.players[i].intents_map, sep='\n')
print(game.players[0].hand, game.players[0].intents_map, game.players[0].current_intent, sep='\n')


game.players[0].play_turn(game.board)

# game.process_hands()
game.board.print()
print(game.players[0].hand, game.players[0].intents_map, game.players[0].current_intent, sep='\n')
# for i in [0, 1, 2, 3]:
#     print(game.players[i].balls, game.players[i].hand, game.players[i].intents, game.players[i].intents_map, sep='\n')
