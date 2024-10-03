from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, date

from utils.config import sql_connection
from utils.logger import get_logger

import db.settings_queries as db

logger = get_logger(__name__)

time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}

async def validate_date_string(update: Update, context: ContextTypes.DEFAULT_TYPE, date_text: str) -> None:
    try:
        date.fromisoformat(date_text)
        return True
    except ValueError:
        await update.message.reply_text(rf"Invalid date format: {date_text}. Please use the format YYYY-MM-DD HH:MM:SS")
        return False
    
def _convert_time_to_seconds(time: int, time_unit: str) -> int:
    if time_unit == 's':
        return time
    elif time_unit == 'm':
        return time * 60
    elif time_unit == 'h':
        return time * 3600
    elif time_unit == 'd':
        return time * 86400

async def set_chat_to_all_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id
    db.set_chat_to_all_context(sql_connection, chat_id, player_id)
    await update.message.reply_text("Chat context set to all messages.")

async def start_static_window(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Date format: YYYY-MM-DD HH:MM:SS"""
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id

    msg_words = update.message.text.split(' ') + ['']
    
    if len(msg_words) > 2:
        date = str(msg_words[1])
        time = str(msg_words[2])
        if time == '':
            time = ' 00:00:00'
        start_time = date + time
        if not validate_date_string(update, context, start_time):
            return
        else:
            logger.info(f"Start time: {start_time}")
    else:
        start_time = None
        
    db.set_chat_to_static_context(sql_connection, chat_id, player_id, start_time)
    await update.message.reply_text("Chat context set to static window.")

async def end_static_window(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id
    db.update_chat_static_context_end_time(sql_connection, chat_id, player_id)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(rf"Static window ended at {current_time}.")

async def set_chat_to_rolling_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id

    msg_words = update.message.text.split(' ') + ['']

    valid_time_units = list(time_units.keys())

    if len(msg_words) > 2:
        try:
            window_size = int(msg_words[1])
        except:
            await update.message.reply_text("Invalid window size. Please provide a valid integer.")
            return
    else:
        window_size = 1

    if len(msg_words) > 3:
        time_unit = str(msg_words[2])
        if time_unit.lower() not in valid_time_units:
            await update.message.reply_text(rf"Invalid time unit. Please provide a valid time unit ({valid_time_units}).")
            return

    else:
        time_unit = 'h'

    window_size_in_seconds = _convert_time_to_seconds(window_size, time_unit)

    db.set_chat_to_rolling_context(sql_connection, chat_id, player_id, window_size_in_seconds)
    await update.message.reply_text(rf"Chat context set to rolling window of {window_size} {time_units[time_unit]}.")

async def set_chat_to_n_messages_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id

    msg_words = update.message.text.split(' ') + ['']

    if len(msg_words) > 1:
        try:
            n_messages = int(msg_words[1])
        except:
            await update.message.reply_text("Invalid number of messages. Please provide a valid integer.")
            return

    db.set_chat_to_n_messages_context(sql_connection, chat_id, player_id, n_messages)
    await update.message.reply_text(rf"Chat context set to last {n_messages} messages.")

async def set_chat_to_session_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id

    db.set_chat_to_session_context(sql_connection, chat_id, player_id)
    await update.message.reply_text("Chat context set to session.")

async def set_chat_to_no_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    player_id = update.effective_user.id

    db.set_chat_to_no_context(sql_connection, chat_id, player_id)
    await update.message.reply_text("Chat context set to no context.")