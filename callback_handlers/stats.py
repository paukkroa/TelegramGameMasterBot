from telegram import User, Update
from telegram.ext import ContextTypes

import db
from utils.config import sql_connection
from utils.logger import get_logger

logger = get_logger(__name__)

async def handle_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if chat.type in ['group', 'supergroup']:
        chat_name = chat.title
    else:
        chat_name = user.username

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

    if query.data == 'stats:player_session':
        await send_player_session_stats(context, session_id, chat.id, user)

    elif query.data == 'stats:player_alltime':
        await send_player_all_time_stats(context, chat.id, user)

    elif query.data == 'stats:group_session':
        await send_group_session_stats(context, session_id, chat.id, chat_name)

    elif query.data == 'stats:group_alltime':
        await send_group_all_time_stats(context, chat.id, chat_name)

async def send_player_session_stats(context: ContextTypes.DEFAULT_TYPE, session_id: str, chat_id: int, user: User):
    stats = db.get_player_session_stats(sql_connection, session_id, user.id)
    msg = (f"Tournament stats for {user.username}:\n\n"
           f"Points: {stats['points']}\n"
           f"Drink units: {int(round(stats['drink_units'], 0))}\n"
           f"Games: {stats['games']}")
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def send_player_all_time_stats(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user: User):
    stats = db.get_player_all_time_stats(sql_connection, user.id)
    msg = (f"All-time stats for {user.username}:\n\n"
           f"Points: {stats['total_points']}\n"
           f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
           f"Games: {stats['total_games']}\n"
           f"Tournaments: {stats['total_tournaments']}")
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def send_group_session_stats(context: ContextTypes.DEFAULT_TYPE, session_id: str, chat_id: int, chat_name: str):
    stats = db.get_group_session_stats(sql_connection, session_id, chat_id)
    msg = (f"Tournament stats for {chat_name}:\n\n"
           f"Points: {stats['total_points']}\n"
           f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
           f"Games: {stats['total_games']}")
    await context.bot.send_message(chat_id=chat_id, text=msg)
async def send_group_all_time_stats(context: ContextTypes.DEFAULT_TYPE, chat_id: int, chat_name: str):
    stats = db.get_group_all_time_stats(sql_connection, chat_id)
    msg = (f"All-time stats for {chat_name}:\n\n"
           f"Points: {stats['total_points']}\n"
           f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
           f"Games: {stats['total_games']}\n"
           f"Tournaments: {stats['total_tournaments']}")
    await context.bot.send_message(chat_id=chat_id, text=msg)

