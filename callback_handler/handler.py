from telegram import Update
from telegram.ext import ContextTypes

import db
from rankings import handle_ranking_callback
from stats import handle_stats_callback
from utils.logger import get_logger
from utils.config import sql_connection

logger = get_logger(__name__)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    # HANDLERS BELOW

    if query.data.startswith('stats'):
        await handle_stats_callback(query.data, context, session_id, chat.id, chat_name, user)
    elif query.data.startswith('ranking'):
        await handle_ranking_callback(query.data, context, chat.id, session_id)
