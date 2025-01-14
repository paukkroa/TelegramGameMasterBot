from telegram.error import BadRequest
from telegram.error import RetryAfter, Forbidden
import asyncio
from telegram.ext import ContextTypes
from telegram import Update
from utils.logger import get_logger

logger = get_logger(__name__)

async def get_username_by_id(user_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    try:
        user = await context.bot.get_chat(user_id)
        username = user.username if user.username else "Incognito user"
        return username
    except BadRequest:
        return "Null"

def convert_swigs_to_units(swigs: int) -> float:
    """Expect that the drink is 5% alcohol and one 0.33l can is 24 swigs"""
    swig_ml = 330 / 24 * swigs
    alc_ml = swig_ml * 0.05
    units = alc_ml / 15.2
    return units

def convert_shots_to_units(shots: int) -> float:
    """Expect that the shot is 40% alcohol and maybe 3cl"""
    alc_ml = 30 * 0.4 * shots
    units = alc_ml / 15.2
    return units

async def send_chat_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message: str, reply_markup=None):
    try:
        await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except RetryAfter as e:
        logger.info(f"Caught flood control, retrying after {e.retry_after+1} seconds")
        await asyncio.sleep(e.retry_after+1)
        await send_chat_safe(context, chat_id, message, reply_markup)
    except Forbidden as e: # Player has not initiated a private chat with the bot
        logger.info(e)
        return e
    except BadRequest as e:
        logger.info(e)
        return e
    
async def file_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # Download file
    new_file = await update.message.effective_attachment[-1].get_file()
    file = await new_file.download_to_drive()
    
    return file