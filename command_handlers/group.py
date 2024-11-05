from telegram import Update
from telegram.ext import ContextTypes

import db
from utils.logger import get_logger
from utils.config import BOT_TG_ID_STR, sql_connection

logger = get_logger(__name__)

# TODO: This might be obsolete with the new /start command
async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add member into D_PLAYER automatically when they join the group"""
    for member in update.message.new_chat_members:

        # Exclude the bot (otherwise it adds itself to the game :D)
        if str(member.id) == BOT_TG_ID_STR:
            continue

        logger.info(f"New member joined: {member.username}, ID: {member.id}")
        await update.message.reply_text(f"Welcome {member.first_name}")

        db.insert_player(sql_connection, member.id, member.username)


async def list_group_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of all registered players in the current chat"""
    chat_id = update.effective_chat.id
    players = db.get_chat_member_usernames(sql_connection, chat_id)
    players_str = "Group members: "
    for player in players:
        players_str += f"{player}, "
    players_str = players_str[:-2]
    await update.message.reply_text(str(players_str))
