from Game import Game

game = Game(num_players=4)

winners = game.run(step=True)
print(winners)
