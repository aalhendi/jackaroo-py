from jackaroo.Game import Game
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

game = Game(num_players=4)


def test_deck_length():
    deck_len = (game.num_players*13)
    assert len(game.deck.cards) == deck_len


def test_hand_lengths():
    game.deal_cards()
    player_hand_lengths = [len(p.hand) for p in game.players]
    game.deal_cards()
    game.deal_cards()
    player_hand_lengths2 = [len(p.hand) for p in game.players]

    assert len(set(player_hand_lengths)) == 1 == len(set(player_hand_lengths2))
