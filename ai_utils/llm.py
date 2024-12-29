import ollama
from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

from db.session_queries import *
from db.settings_queries import get_chat_settings
from ai_utils.llm_utils import SYS_PROMPT_WITH_CONTEXT, SYS_PROMPT_NO_CONTEXT, SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY, SUMMARIZE_PROMPT
from utils.helpers import get_username_by_id, send_chat_safe
from utils.logger import get_logger
from utils.config import BOT_NAME, BOT_TG_ID, LLM_ENGINE, LLM_MODEL, LLM_ENABLED
from ai_utils.engines import LLMService

logger = get_logger(__name__)

# Initialize the LLM service
llm = LLMService(engine=LLM_ENGINE, model=LLM_MODEL)

# TODO: Add a check to see if Ollama is available
async def generic_message_llm_handler(update: Update, 
                                      tg_context: ContextTypes.DEFAULT_TYPE, 
                                      sql_connection: sqlite3.Connection, 
                                      bot_name: str = BOT_NAME, 
                                      bot_tg_id: int = BOT_TG_ID) -> None:
    
    # Check if ollama is available
    if not llm.is_available():
        logger.error("LLM service is not available")
        await send_chat_safe(tg_context, chat_id=update.effective_chat.id, message="Unfortunately my brain is not available right now. Please try again later.")
        return

    msg = update.message.text
    sender_id = update.effective_user.id
    sender_name = await get_username_by_id(sender_id, tg_context)
    chat_id = update.effective_chat.id
    session_id = get_latest_ongoing_session_by_chat(sql_connection, chat_id)
    chat_settings = get_chat_settings(sql_connection, chat_id)    

    # Bot is mentioned, reply to the text
    if f'@{bot_name}' in msg:
        # Remove bot mention from the message
        msg = msg.replace(f'@{bot_name}', '')

        # --- Check if llm is enabled ---
        if not LLM_ENABLED:
            logger.warning(f"LLM is disabled in environment variables, adding message to session context")
            add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
            logger.info(f"Added message from sender ({sender_id} to chat ({chat_id})")
            response = "My brain is not enabled right now. Please try again later."
            await send_chat_safe(tg_context, chat_id=update.effective_chat.id, message=response)
            return

        # --- Get context for the message ---

        # Retrieve all of the message history
        if chat_settings['context_window_type'] == 'all':
            context = get_all_chat_messages(sql_connection, chat_id)
            logger.info(f"Retrieved all chat messages for chat {chat_id}")
            sys_prompt = SYS_PROMPT_WITH_CONTEXT

        # Retrieve messages with a rolling time window
        elif chat_settings['context_window_type'] == 'rolling':
            context = get_chat_messages_from_rolling_time_window(sql_connection, chat_id)
            logger.info(f"Retrieved rolling context for chat {chat_id}")
            sys_prompt = SYS_PROMPT_WITH_CONTEXT
            
        # Retrieve messages with a static time window
        elif chat_settings['context_window_type'] == 'static':
            context = get_chat_messages_within_time_window(sql_connection, chat_id)
            logger.info(f"Retrieved static context messages for chat {chat_id}")
            sys_prompt = SYS_PROMPT_WITH_CONTEXT

        # Retrieve n-last messages
        elif chat_settings['context_window_type'] == 'n-messages':
            context = get_last_n_messages(sql_connection, chat_id)
            logger.info(f"Retrieved last n-messages (n: {chat_settings['n_messages']}) for chat {chat_id}")
            sys_prompt = SYS_PROMPT_WITH_CONTEXT

        # Retrieve messages from the session if it is ongoing
        elif chat_settings['context_window_type'] == 'session':
            context = get_session_messages(sql_connection, session_id)
            logger.info(f"Retrieved session {session_id} context for chat {chat_id}")
            sys_prompt = SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY

        else:
            logger.info(f"Message in chat {chat_id} has no context window, prompting with zero-shot.")
            context = None
            sys_prompt = SYS_PROMPT_NO_CONTEXT

        # --- Create prompt ---
        if context is None:
            content = f"User name: {sender_name}, User message: {msg}"
        else:
            content = f"User name: {sender_name}, User message: {msg}, Context: {context}"
        
        # --- Get response from the LLM model ---
        llm.set_sys_prompt(sys_prompt)
        llm_response = llm.chat(content)
        
        # --- Add messages to the chat context ---
        add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
        logger.info(f"Added message from sender ({sender_id} to chat context ({chat_id})")
        add_message_to_chat_context(sql_connection, chat_id, bot_tg_id, llm_response)
        logger.info(f"Added message from bot ({bot_tg_id} to chat context ({chat_id})")

        # --- Send response to the chat ---
        await send_chat_safe(tg_context, chat_id=update.effective_chat.id, message=llm_response)

    # Bot is not mentioned, add message to context
    else: 
        # Add user message to the chat context
        add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
        logger.info(f"Added message from sender ({sender_id} to chat ({chat_id})")
        