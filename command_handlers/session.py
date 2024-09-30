from telegram import Update
from telegram.ext import ContextTypes

import db
from utils.config import sql_connection, BOT_TG_ID, current_waitlists, ongoing_tournaments
from utils.logger import get_logger
from session import Tournament, Waitlist

logger = get_logger(__name__)

async def start_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    try:
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist found for chat {chat_id}: {waitlist}")
    except KeyError:
        logger.info(f"No waitlist found for chat {chat_id}")
        await update.message.reply_text(
            "No players are on the waitlist, cannot start tournament. Press /join to join the waitlist.")
        return

    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Session {session_id} started for chat {chat_id}")
    # Add extra empty char to list to prevent index out of range error
    msg_words = update.message.text.split(' ') + ['']

    try:
        number_of_games = int(msg_words[1])
    except ValueError:
        number_of_games = 5

    logger.info(f"Tournament games: {number_of_games}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    tournament = Tournament(session_id, waitlist.player_ids, number_of_games, update, context, sql_connection,
                            BOT_TG_ID)
    ongoing_tournaments[chat_id] = tournament
    logger.info(f"Tournament {tournament}")

    waitlist.clear()  # Is this needed anymore?
    del current_waitlists[chat_id]
    del waitlist
    await tournament.start()


async def end_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """End the current session"""
    chat_id = update.effective_chat.id
    try:
        tournament = ongoing_tournaments[chat_id]
        logger.info(f"Tournament found for chat {chat_id}: {tournament}")
    except KeyError:
        logger.info(f"No tournament found for chat {chat_id}, checking for open sessions")
        session_id = db.get_latest_ongoing_session_by_chat(sql_connection, chat_id)
        if session_id is not None:
            db.end_session(sql_connection, session_id)
            await update.message.reply_text("Session has been ended.")
        else:
            await update.message.reply_text("No active tournament found to end.")
        return

    await tournament.end()
    del ongoing_tournaments[chat_id]
    del tournament

    await update.message.reply_text(f"Tournament has been ended.")


async def handle_join_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add player into waitlist when they send /join """
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id in current_waitlists.keys():
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist exists for chat {chat_id}: {waitlist}")
    else:
        waitlist = Waitlist(chat_id)
        current_waitlists[chat_id] = waitlist
        logger.info(f"Created new waitlist for chat {chat_id}: {waitlist}")

    if waitlist.add_player(user.id):
        logger.info(f"Player {user.id} added to waitlist in chat {chat_id}")
        logger.info(f"Current waitlist: {waitlist.player_ids}")
        await update.message.reply_text("Joined session succesfully")
    else:
        await update.message.reply_text("You have already joined the session")
        logger.info(f"Player {user.id} already in waitlist in chat {chat_id}")
        logger.info(f"Current waitlist: {waitlist.player_ids}")


async def print_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    try:
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist found for chat {chat_id}: {waitlist}")
        await waitlist.list_players(update, context)
    except KeyError:
        logger.info(f"No waitlist found for chat {chat_id}")
        await update.message.reply_text("No waitlist found for the chat. Press /join to join the waitlist.")
