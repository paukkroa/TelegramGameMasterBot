from telegram.ext import ContextTypes

import db
from utils.config import sql_connection

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