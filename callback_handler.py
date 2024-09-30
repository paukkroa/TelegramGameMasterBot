import sqlite3

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

    query = update.callback_query
    await query.answer()

    # TODO: Figure out how to show session stats
    # None if player not in session / has no recent sessions
    session_id = str(db.get_most_recent_session_by_player(sql_connection, user.id))
    print(f"Player {user.username} latest session id: {session_id}")

    # Interrupt if session id is None and it is needed
    if not session_id and 'session' in query.data.lower():
        msg = f"Fetching session stats failed: {user.username} does not have a recent session."
        await context.bot.send_message(chat_id=chat.id, text=msg)
        return

    # HANDLERS BELOW

    # TODO: Make separate functions when this has too many routes
    if query.data == 'stats:player_session':
        stats = db.get_player_session_stats(sql_connection, session_id, user.id)
        msg = (f"Tournament stats for {user.username}:\n\n"
               f"Points: {stats['points']}\n"
               f"Drink units: {int(round(stats['drink_units'], 0))}\n"
               f"Games: {stats['games']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:player_alltime':
        stats = db.get_player_all_time_stats(sql_connection, user.id)
        msg = (f"All-time stats for {user.username}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
               f"Games: {stats['total_games']}\n"
               f" Tournaments: {stats['total_tournaments']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:group_session':
        stats = db.get_group_session_stats(sql_connection, session_id, chat.id)
        msg = (f"Tournament stats for {chat_name}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
               f"Games: {stats['total_games']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'stats:group_alltime':
        stats = db.get_group_all_time_stats(sql_connection, chat.id)
        msg = (f"All-time stats for {chat_name}:\n\n"
               f"Points: {stats['total_points']}\n"
               f"Drink units: {int(round(stats['total_drink_units'], 0))}\n"
               f"Games: {stats['total_games']}\n"
               f" Tournaments: {stats['total_tournaments']}")
        await context.bot.send_message(chat_id=chat.id, text=msg)

    elif query.data == 'ranking:session_points':
        await send_session_ranking(sql_connection, context, chat.id, 'points', session_id)

    elif query.data == 'ranking:session_drinks':
        await send_session_ranking(sql_connection, context, chat.id, 'drinks', session_id)

    elif query.data == 'ranking:alltime_points':
        await send_all_time_ranking(sql_connection, context, chat.id, 'points')

    elif query.data == 'ranking:alltime_drinks':
        await send_all_time_ranking(sql_connection, context, chat.id, 'drinks')

    elif query.data == 'ranking:alltime_games':
        await send_all_time_ranking(sql_connection, context, chat.id, 'games')

    elif query.data == 'ranking:alltime_tournaments':
        await send_all_time_ranking(sql_connection, context, chat.id, 'tournaments')

async def send_all_time_ranking(conn: sqlite3.Connection, context: ContextTypes.DEFAULT_TYPE, chat_id: str, key: str) -> None:
    ranking = db.get_group_alltime_ranking(conn, chat_id, key)

    msg = f"All-time {key} ranking:\n"
    for index, player in enumerate(ranking, start=1):
        msg += f"\n{index}. {player['username']} - {int(round(player[key], 0))}"

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def send_session_ranking(conn: sqlite3.Connection, context: ContextTypes.DEFAULT_TYPE,
                               chat_id: str, key: str, session_id: str) -> None:
    ranking = db.get_group_session_ranking(conn, session_id, chat_id, key)

    msg = f"Tournament {key} ranking:\n"
    for index, player in enumerate(ranking, start=1):
        msg += f"\n{index}. {player['username']} - {int(round(player[key], 0))}"

    await context.bot.send_message(chat_id=chat_id, text=msg)