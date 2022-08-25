from Game import Game
from utils.logger import logger
from tqdm import tqdm


logger.info("RUN START")
for _ in tqdm(range(1000)):
    game = Game(num_players=4)
    winners = game.run(step=False)
    if winners[0] and winners[2]:
        winning_team = 1
    else:
        winning_team = 2
    logger.info(
        f"Rounds Played: {game.rounds_played} - Winners:{winners} - Winning Team: {winning_team}")
logger.info("RUN END\n")
