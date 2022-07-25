from game import Game

game = Game() #TODO: Impl this into game
deck = game.deck

game.init_game()

game.process_hands()

game.board.print()
for i in [0, 1, 2, 3]:
    print(game.players[i].balls, game.players[i].hand, game.players[i].intents, game.players[i].intents_map, sep='\n')


card_idx, intent = game.decide_intent(game.players[0].intents_map)

print(card_idx, intent)

game.process_intent(intent, game.players[0].balls)

game.process_hands()
game.board.print()
for i in [0, 1, 2, 3]:
    print(game.players[i].balls, game.players[i].hand, game.players[i].intents, game.players[i].intents_map, sep='\n')
