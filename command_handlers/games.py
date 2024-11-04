from telegram import Update
from telegram.ext import ContextTypes

from games import ChallengeGame, GuessNumber, TeamQuiz, Exposed

import db

from utils.logger import get_logger
from utils.config import current_waitlists, sql_connection

logger = get_logger(__name__)

async def handle_number_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print(waitlist)

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = GuessNumber(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    logger.info(f'Guess number game start')
    await game.start()

async def handle_challenge_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print(waitlist)

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = ChallengeGame(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(5)
    logger.info(f"Challenge game start")
    await game.start()

async def handle_team_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    print("Waitlist", waitlist)

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = TeamQuiz(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(4)
    logger.info(f"Team quiz start")
    await game.start()

async def handle_exposed_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    logger.info(f"Waitlist {waitlist}")

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = Exposed(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(4)
    logger.info(f"Exposed game start")
    await game.start()