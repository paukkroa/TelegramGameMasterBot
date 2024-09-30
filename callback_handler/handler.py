from telegram import Update
from telegram.ext import ContextTypes

import db
import callback_handler.rankings as rh
import callback_handler.stats as sh
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

    if query.data == 'stats:player_session':
        await sh.send_player_session_stats(context, session_id, chat.id, user)

    elif query.data == 'stats:player_alltime':
        await sh.send_player_all_time_stats(context, chat.id, user)

    elif query.data == 'stats:group_session':
        await sh.send_group_session_stats(context, session_id, chat.id, chat_name)

    elif query.data == 'stats:group_alltime':
        await sh.send_group_all_time_stats(context, chat.id, chat_name)

    elif query.data == 'ranking:session_points':
        await rh.send_session_ranking(context, chat.id, 'points', session_id)

    elif query.data == 'ranking:session_drinks':
        await rh.send_session_ranking(context, chat.id, 'drinks', session_id)

    elif query.data == 'ranking:alltime_points':
        await rh.send_all_time_ranking(context, chat.id, 'points')

    elif query.data == 'ranking:alltime_drinks':
        await rh.send_all_time_ranking(context, chat.id, 'drinks')

    elif query.data == 'ranking:alltime_games':
        await rh.send_all_time_ranking(context, chat.id, 'games')

    elif query.data == 'ranking:alltime_tournaments':
        await rh.send_all_time_ranking(context, chat.id, 'tournaments')

