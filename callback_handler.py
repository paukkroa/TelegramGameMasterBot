from telegram import Update
from telegram.ext import ContextTypes

import db

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sql_connection = db.connect()

    user = update.effective_user
    chat = update.effective_chat

    if chat.type in ['group', 'supergroup']:
        chat_name = chat.title
    else:
        chat_name = user.username

    session_id = str(db.get_most_recent_session_by_player(sql_connection, user.id))

    query = update.callback_query
    await query.answer()

    # TODO: Make separate functions when this has too many routes
    if query.data == 'stats:player_session':
        stats = db.get_player_session_stats(sql_connection, session_id, user.id)
        msg = (f"Session stats for {user.username}:\n\n"
               f"Points: {stats['points']}\n"
               f"Drink units: {stats['drink_units']}\n"
               f"Games: {stats['games']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:player_alltime':
        stats = db.get_player_all_time_stats(sql_connection, user.id)
        msg = (f"All-time stats for {user.username}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {stats['total_drink_units']}\n"
               f"Games: {stats['total_games']}\n"
               f" Tournaments: {stats['total_tournaments']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:group_session':
        stats = db.get_group_session_stats(sql_connection, session_id, chat.id)
        msg = (f"Session stats for {chat_name}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {stats['total_drink_units']}\n"
               f"Games: {stats['total_games']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:group_alltime':
        stats = db.get_group_all_time_stats(sql_connection, chat.id)
        msg = (f"All-time stats for {chat_name}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {stats['total_drink_units']}\n"
               f"Games: {stats['total_games']}\n"
               f" Tournaments: {stats['total_tournaments']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)
