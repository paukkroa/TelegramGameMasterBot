from telegram.error import BadRequest
from telegram.ext import ContextTypes

async def get_username_by_id(user_id: str, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = await context.bot.get_chat(user_id)
        username = user.username if user.username else "Incognito user"
        return username
    except BadRequest:
        return "Null"
