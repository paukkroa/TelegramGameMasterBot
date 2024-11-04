from telegram import Update
from telegram.ext import ContextTypes

from games import ChallengeGame, GuessNumber, TeamQuiz, Exposed

import db

from utils.logger import get_logger
from utils.config import current_waitlists, sql_connection

logger = get_logger(__name__)

async def delete_waitlist_quiet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    try:
        waitlist.clear()  # Is this needed anymore?
        del waitlist
        del current_waitlists[chat_id]
        logger.info(f"Waitlist deleted for chat {chat_id}")
    except KeyError:
        logger.info(f"No waitlist found for chat {chat_id}")

async def handle_number_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    logger.info(f"Waitlist {waitlist}")

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = GuessNumber(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    logger.info(f'Guess number game start')
    await delete_waitlist_quiet(update, context)
    await game.start()

async def handle_challenge_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    logger.info(f"Waitlist {waitlist}")

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    game = ChallengeGame(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(5)
    logger.info(f"Challenge game start")
    await delete_waitlist_quiet(update, context)
    await game.start()

async def handle_team_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    logger.info(f"Waitlist {waitlist}")

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    msg_words = update.message.text.split(' ') + ['']

    if len(msg_words) > 2:
        try:
            rounds = int(msg_words[1])
        except:
            await update.message.reply_text("Invalid number. Please provide a valid integer.")
            return
        
    else:
        rounds = 4

    game = TeamQuiz(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(rounds)
    logger.info(f"Team quiz start")
    await delete_waitlist_quiet(update, context)
    await game.start()

async def handle_exposed_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    waitlist = current_waitlists[chat_id]
    logger.info(f"Waitlist {waitlist}")

    if len(waitlist.player_ids) < 2:
        await update.message.reply_text("Not enough players to start the game.")
        return

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Gamewise session {session_id} started for chat {chat_id}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    msg_words = update.message.text.split(' ') + ['']

    if len(msg_words) > 2:
        try:
            rounds = int(msg_words[1])
        except:
            await update.message.reply_text("Invalid number. Please provide a valid integer.")
            return
        
    else:
        rounds = 10

    game = Exposed(id=1, player_ids=waitlist.player_ids, update=update, context=context, session_id=session_id)
    game.set_rounds(rounds)
    logger.info(f"Exposed game start")
    await delete_waitlist_quiet(update, context)
    await game.start()