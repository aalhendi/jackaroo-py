# Create a new game instance
from guts import Color, Game, Player

players = [Player(color) for color in [Color.BLACK, Color.BLUE, Color.GREEN, Color.RED]]
game = Game(players=players)

print(len(game.deck))
game.shuffle_deck()
game.deal_cards(players)

[print(p.cards) for p in players]
print(len(game.deck))