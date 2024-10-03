import ollama
from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

from db.session_queries import *
from db.settings_queries import get_chat_settings
from ai_utils.llm_utils import LLM_MODEL, SYS_PROMPT_WITH_CONTEXT, SYS_PROMPT_NO_CONTEXT, SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY
from utils.helpers import get_username_by_id
from utils.logger import get_logger
from utils.config import BOT_NAME, BOT_TG_ID

logger = get_logger(__name__)

# TODO: Add rolling context window
async def generic_message_llm_handler(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE, 
                                      sql_connection: sqlite3.Connection, 
                                      bot_name: str = BOT_NAME, 
                                      bot_tg_id: int = BOT_TG_ID) -> None:
    msg = update.message.text
    # Remove bot mention from the message
    msg = msg.replace(f'@{bot_name}', '')
    sender_id = update.effective_user.id
    sender_name = await get_username_by_id(sender_id, context)
    chat_id = update.effective_chat.id
    session_id = get_latest_ongoing_session_by_chat(sql_connection, chat_id)
    chat_settings = get_chat_settings(sql_connection, chat_id)

    # Bot is mentioned, reply to the text
    if f'@{bot_name}' in update.message.text:
        # Retrieve all of the message history
        if chat_settings['context_window_type'] == 'all':
            context = get_all_chat_messages(sql_connection, chat_id)
            logger.info(f"Retrieved all chat messages for chat {chat_id}: {context}")
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
        # Retrieve messages with a rolling time window
        elif chat_settings['context_window_type'] == 'rolling':
            context = get_chat_messages_from_rolling_time_window(sql_connection, chat_id)
            logger.info(f"Retrieved rolling context for chat {chat_id}: {context}")
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
            
        # Retrieve messages with a static time window
        elif chat_settings['context_window_type'] == 'static':
            context = get_chat_messages_within_time_window(sql_connection, chat_id)
            logger.info(f"Retrieved static context messages for chat {chat_id}: {context}")
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

        elif chat_settings['context_window_type'] == 'n-messages':
            context = get_last_n_messages(sql_connection, chat_id, chat_settings['n_messages'])
            logger.info(f"Retrieved last n-messages (n: {chat_settings['n_messages']}) for chat {chat_id}: {context}")
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

        elif chat_settings['context_window_type'] == 'session':
            context = get_session_messages(sql_connection, session_id)
            logger.info(f"Retrieved session {session_id} context for chat {chat_id}: {context}")
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY,
                },
                {
                    'role': 'user',
                    'content': f"User name: {sender_name}, User message: {msg}, Context: {context}",
                },
            ])
            llm_response = response['message']['content']
        # No context window
        else: 
            logger.info(f"Message in chat {chat_id} has no context window, prompting with zero-shot.")
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
        
        # Add user message to the chat context
        add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
        logger.info(f"Added message from sender ({sender_id} to chat context ({chat_id})")
        # Add bot message to the chat context
        add_message_to_chat_context(sql_connection, chat_id, bot_tg_id, llm_response)
        logger.info(f"Added message from bot ({bot_tg_id} to chat context ({chat_id})")
        await update.message.reply_text(llm_response)

    # Bot is not mentioned, add message to context
    else: 
        # Add user message to the chat context
        add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
        logger.info(f"Added message from sender ({sender_id} to chat ({chat_id})")
        