import ollama
from telegram import Update
from telegram.ext import ContextTypes
import logging
import sqlite3

import db
from ai_utils.llm_utils import LLM_MODEL, SYS_PROMPT_WITH_CONTEXT, SYS_PROMPT_NO_CONTEXT
from utils import get_username_by_id

# LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def generic_message_llm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, sql_connection: sqlite3.Connection, bot_name: str, bot_tg_id: int) -> None:
    msg = update.message.text
    # Remove bot mention from the message
    msg = msg.replace(f'@{bot_name}', '')
    sender_id = update.effective_user.id
    sender_name = await get_username_by_id(sender_id, context)
    session_id = db.get_most_recent_session_by_player(sql_connection, sender_id)

    # No ongoing session, respond if needed
    if session_id is None:
        logger.info(f"User message does not belong to any active session")
        # Private message, respond directly
        if f'@{bot_name}' in update.message.text:
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_NO_CONTEXT,
                },
                {
                    'role': 'user',
                    'content': f"User name: {sender_name}, User message: {msg}",
                },
            ])
            llm_response = response['message']['content']
            await update.message.reply_text(llm_response)
        
    # Ongoing session, handle context
    else:
        logger.info(f"Received message with session_id: {session_id}")
        # If the message is from a group, only respond if the bot is mentioned
        # then we only want to add message to the context
        if f'@{bot_name}' in update.message.text:
            context = db.get_session_messages(sql_connection, session_id)
            logger.info(f"Retrieved context from session ({session_id} to model: {context})")
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_WITH_CONTEXT,
                },
                {
                    'role': 'user',
                    'content': f"User name: {sender_name}, User message: {msg}, Context: {context}",
                },
            ])
            llm_response = response['message']['content']
            db.add_message_to_session_context(sql_connection, session_id, bot_tg_id, llm_response)
            await update.message.reply_text(llm_response)

        
        # The bot is not mentioned but the message is from a group, add the message to the context
        elif update.message.chat.type == 'group' and f'@{bot_name}' not in update.message.text:
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            return
        
        # Most likely a private message, let's not add those 
        else:
            logger.info("Private message, not adding to context")
            return