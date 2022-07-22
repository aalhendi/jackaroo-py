from game import Game
import utils.utils as utils

game = Game() #TODO: Impl this into game
deck = game.deck
p1, p2, p3, p4 = game.players

game.init_game()

game.process_hands()

game.board.print
for i in [0, 1, 2, 3]:
    print(game.players[i].balls, game.players[i].hand, game.players[i].intents, game.players[i].intents_map, sep='\n')


card_idx, intent = utils.decide_intent(game.players[0].intents_map, game.players[0].hand)

print(card_idx, intent)

game.process_intent(intent, p1.balls)

game.process_hands()
game.board.print 
for i in [0, 1, 2, 3]:
    print(game.players[i].balls, game.players[i].hand, game.players[i].intents, game.players[i].intents_map, sep='\n')