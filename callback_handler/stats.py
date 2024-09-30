from telegram import User
from telegram.ext import ContextTypes

import db
from utils.config import sql_connection

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

