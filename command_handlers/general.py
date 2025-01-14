from telegram import Update, ForceReply
from telegram.ext import ContextTypes

import db

from ai_utils.llm import generic_message_llm_handler, generic_image_message, reply_message_with_image_handler, reply_message_handler
from utils.config import sql_connection, BOT_TG_ID, BOT_NAME
from utils.logger import get_logger

logger = get_logger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, quiet = False) -> None:
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
    flag = db.add_player_to_chat(sql_connection, chat_id, user.id)
    db.add_player_to_chat(sql_connection, chat_id, BOT_TG_ID)

    if not quiet:
        # flag = True == player was added to chat succesfully
        if flag:
            if update.message.chat.type != 'group':
                message = rf"Hi {user.mention_html()}! Get back to the group chat to start the party!"
            else:
                message = rf"Welcome {user.mention_html()}!"
            await update.message.reply_html(
                    message,
                    reply_markup=ForceReply(selective=True),
                )
        else:
            await update.message.reply_html(
                rf"{user.mention_html()}, you are already registered.",
                reply_markup=ForceReply(selective=True),
            )
    else:
        if flag:
            logger.info(f"User {user.id} added to {chat_id} quietly.")
        else:
            logger.info(f"User {user.id} has already registered to chat {chat_id}.")

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
                                    
Type /help_ai to get instructions on how to interact with the AI Game Master.
""")

# TODO: Add command to list all available games
# TODO: Add command to insert private information about a player (player facts)

async def list_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of all registered players in databse"""
    # TODO: get from actual session and make response cleaner
    players = db.get_all_players(sql_connection)
    await update.message.reply_text(str(players))

async def handle_generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await generic_message_llm_handler(update, context, sql_connection)

async def handle_generic_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await generic_image_message(update, context, sql_connection)

async def handle_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        reply_photo = update.message.reply_to_message.photo[-1]
        await reply_message_with_image_handler(update, context, sql_connection)
    except IndexError:
        await reply_message_handler(update, context, sql_connection)


async def ai_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help-ai is issued."""
    user = update.effective_user
    await update.message.reply_text(rf"""Tag me and write your message, like this: @{BOT_NAME} <message>.
                                    
Enable AI features by giving the bot admin rights in the group chat.
                                    
To set the context for the AI Game Master, use the following commands:
- /context_all: Use all messages in the chat as context.
                                    
- /context_static: Use only messages within a static window as context. Use /start_context to start the window and /end_context to end it. You can also define specific starting and end points, for example: "/start_context 2024-10-03 16:00:00" or "/start_context 2024-10-03" (defaults to 00:00:00).
                                    
- /context_rolling: Use only messages within a rolling window as context. Default is 1 hour. You can define the window size and time unit, for example: "/context_rolling 5 h" or "/context_rolling 2 d".
                                    
- /context_last_n: Use only the last N messages as context. Default is 10. You can define the number of messages, for example: "/context_last_n 20".
                                    
- /context_session: Use only messages witihin a tournament as context. The messages won't be available after the tournament ends.
                                    
- /context_none: Disable context for the AI Game Master.
""")