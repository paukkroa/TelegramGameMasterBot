from telegram.ext import ContextTypes

import db
from utils.config import sql_connection

async def handle_ranking_callback(key: str, context: ContextTypes.DEFAULT_TYPE, chat_id: int, session_id: str):
    if key == 'ranking:session_points':
        await send_session_ranking(context, chat_id, 'points', session_id)

    elif key == 'ranking:session_drinks':
        await send_session_ranking(context, chat_id, 'drinks', session_id)

    elif key == 'ranking:alltime_points':
        await send_all_time_ranking(context, chat_id, 'points')

    elif key == 'ranking:alltime_drinks':
        await send_all_time_ranking(context, chat_id, 'drinks')

    elif key == 'ranking:alltime_games':
        await send_all_time_ranking(context, chat_id, 'games')

    elif key == 'ranking:alltime_tournaments':
        await send_all_time_ranking(context, chat_id, 'tournaments')

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