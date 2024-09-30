from telegram import Update, ForceReply
from telegram.ext import ContextTypes

import db

from ai_utils.llm import generic_message_llm_handler
from utils.config import sql_connection, BOT_TG_ID, BOT_NAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Create the chat and user in the database when the bot is started.
    Add the bot to the chat as well.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    chat_name = update.effective_chat.title

    # These functions have unique constraints so they will not add duplicates
    db.create_chat(sql_connection, chat_id, chat_name)
    db.insert_player(sql_connection, user.id, user.username)
    db.add_player_to_chat(sql_connection, chat_id, user.id)
    db.add_player_to_chat(sql_connection, chat_id, BOT_TG_ID)

    if update.message.chat.type != 'group':
        message = rf"Hi {user.mention_html()}! Are you ready to start playing? Add me to a group chat with your friends and press /start there. Press /help for more information."
    else:
        message = rf"Hi {user.mention_html()}! Welcome to the group! Make sure all your friends here press /start as well. Press /help for more information."
    await update.message.reply_html(
            message,
            reply_markup=ForceReply(selective=True),
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    await update.message.reply_text(rf"""I'm a bot that can help you organize party game tournaments with your friends. The workflow is simple:

1. Add me to a group chat with your friends. You can admit admin rights to me to enable contextual messages.
2. Press /start to start join the group.
3. Press /join to join the waitlist for the next tournament.
4. Press /tournament to start a tournament with the players in the waitlist.
5. Play games and have fun!

If you have any questions, feel free to ask by tagging me in the group chat (remember to give me admin rights to enable this). Have fun!
""")

# TODO: Add command to list all available games
# TODO: Add command to insert private information about a player (player facts)

async def list_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of all registered players in databse"""
    # TODO: get from actual session and make response cleaner
    players = db.get_all_players(sql_connection)
    await update.message.reply_text(str(players))

async def handle_generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await generic_message_llm_handler(update, context, sql_connection, BOT_NAME, BOT_TG_ID)
