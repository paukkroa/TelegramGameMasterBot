from telegram import Update
from telegram.ext import ContextTypes

from games import ChallengeGame, GuessNumber, TeamQuiz

from utils.logger import get_logger
from utils.config import current_waitlists

logger = get_logger(__name__)

# TODO: Fix the below functions to work with the current_waitlist dict
# or delete them completely
async def handle_number_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print(waitlist)

    game = GuessNumber(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    logger.info(f'Guess number game start')
    await game.start()

async def handle_challenge_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print(waitlist)

    game = ChallengeGame(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    game.set_rounds(5)
    logger.info(f"Challenge game start")
    await game.start()

async def handle_team_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print("Waitlist", waitlist)

    game = TeamQuiz(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    game.set_rounds(4)
    logger.info(f"Team quiz start")
    await game.start()
