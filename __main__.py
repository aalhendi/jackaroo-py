from game import Game

game = Game()  # TODO: Impl this into game
deck = game.deck

# Play till winner
while True:
    # Play a whole deck, 4-4-5
    while deck.rounds_remaining > 0:
        game.deal_cards()
        deck.decrement_rounds()
        # Play whole hand
        
        while game.deck.expected_hand_length > 0:
            # Every player plays card
            game.process_hands()
            game.deck.decrement_hand_length()
            print(
                f"rounds left: {game.deck.rounds_remaining}, exp_hand: {game.deck.expected_hand_length}, turn_order {game.turn_order}")
            input("Completed Hand Cycle")
    
    print("\n\n")

    # Pass the deck, change the delaer
    game.roll_turn_order()
    deck.reset()
    deck.shuffle()
    input("Completed Deck Cycle")
