from telegram import Update
from telegram.ext import ContextTypes

import db
from utils.config import sql_connection
from utils.logger import get_logger

logger = get_logger(__name__)

async def handle_ranking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    query = update.callback_query
    await query.answer()

    # None if player has no recent sessions
    session_id = str(db.get_most_recent_session_by_player(sql_connection, user.id))
    logger.info(f"Player {user.username} latest session id: {session_id}")

    # Interrupt if session id is None and it is needed
    if not session_id and 'session' in query.data.lower():
        msg = f"Fetching session stats failed: {user.username} does not have a recent session."
        await context.bot.send_message(chat_id=chat.id, text=msg)
        return

    if query.data == 'ranking:session_points':
        await send_session_ranking(context, chat.id, 'points', session_id)

    elif query.data == 'ranking:session_drinks':
        await send_session_ranking(context, chat.id, 'drinks', session_id)

    elif query.data == 'ranking:alltime_points':
        await send_all_time_ranking(context, chat.id, 'points')

    elif query.data == 'ranking:alltime_drinks':
        await send_all_time_ranking(context, chat.id, 'drinks')

    elif query.data == 'ranking:alltime_games':
        await send_all_time_ranking(context, chat.id, 'games')

    elif query.data == 'ranking:alltime_tournaments':
        await send_all_time_ranking(context, chat.id, 'tournaments')

async def send_all_time_ranking(context: ContextTypes.DEFAULT_TYPE, chat_id: int, key: str) -> None:
    ranking = db.get_group_alltime_ranking(sql_connection, chat_id, key)

    msg = f"All-time {key} ranking:\n"
    for index, player in enumerate(ranking, start=1):
        msg += f"\n{index}. {player['username']} - {int(round(player[key], 0))}"

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def send_session_ranking(context: ContextTypes.DEFAULT_TYPE,
                               chat_id: int, key: str, session_id: str) -> None:
    ranking = db.get_group_session_ranking(sql_connection, session_id, chat_id, key)

    msg = f"Tournament {key} ranking:\n"
    for index, player in enumerate(ranking, start=1):
        msg += f"\n{index}. {player['username']} - {int(round(player[key], 0))}"

    await context.bot.send_message(chat_id=chat_id, text=msg)