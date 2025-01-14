from telegram import Update
from telegram.ext import ContextTypes
import sqlite3

from db.session_queries import *
from db.settings_queries import get_chat_settings
from ai_utils.llm_utils import SYS_PROMPT_WITH_CONTEXT, SYS_PROMPT_NO_CONTEXT, SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY, SYS_PROMPT_GAME_END, SYS_PROMPT_TEAM_QUIZ_END
from utils.helpers import get_username_by_id, send_chat_safe, file_downloader
from utils.logger import get_logger
from utils.config import BOT_NAME, BOT_TG_ID, LLM_ENGINE, LLM_MODEL, LLM_ENABLED
from ai_utils.engines import LLMService, BlankLLMService

logger = get_logger(__name__)

# Initialize the LLM service
if LLM_ENABLED:
    try:
        llm = LLMService()
    except ValueError as e:
        logger.error(f"Error initializing LLM service, most likely model is not configured properly in environment variables: {e}")
        llm = BlankLLMService()
else:
    llm = BlankLLMService() # Dummy service when LLM is disabled

def _get_context_and_sys_prompt(chat_settings, chat_id, session_id, sql_connection):
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

    return context, sys_prompt

async def generic_message_llm_handler(update: Update, 
                                      tg_context: ContextTypes.DEFAULT_TYPE, 
                                      sql_connection: sqlite3.Connection, 
                                      bot_name: str = BOT_NAME, 
                                      bot_tg_id: int = BOT_TG_ID) -> None:
    """
    Handle every message that is sent in a chat with the bot in it.

    Args:
        update (Update): Telegram update object
        tg_context (ContextTypes.DEFAULT_TYPE): Telegram context object
        sql_connection (sqlite3.Connection): SQLite connection object
        bot_name (str, optional): Username of the bot. Defaults to BOT_NAME.
        bot_tg_id (int, optional): Telegram ID of the bot. Defaults to BOT_TG_ID.
    """

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
        
        # --- Check if LLM service is available ---
        if not llm.is_available():
            logger.error("LLM service is not available")
            add_message_to_chat_context(sql_connection, chat_id, sender_id, msg)
            logger.info(f"Added message from sender ({sender_id} to chat context ({chat_id})")
            await send_chat_safe(tg_context, chat_id=update.effective_chat.id, message="Unfortunately my brain is not available right now. Please try again later.")
            return

        # --- Get context and sys_prompt for the message ---
        context, sys_prompt = _get_context_and_sys_prompt(chat_settings, chat_id, session_id, sql_connection)

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
        

async def in_game_message(update: Update, 
                       tg_context: ContextTypes.DEFAULT_TYPE, 
                       sql_connection: sqlite3.Connection, 
                       message_type: str = "end",
                       game_name: str = "game",
                       base_message: str = "The game has ended!",
                       bot_tg_id: int = BOT_TG_ID) -> None:
    """
    Call an in-game message from the LLM model.

    Args:
        update (Update): Telegram update object
        tg_context (ContextTypes.DEFAULT_TYPE): Telegram context object
        sql_connection (sqlite3.Connection): SQLite connection object
        message_type (str, optional): Type of message to send. Options: ["end", ""]. "end" is the game end message, anything other is just a regular prompt within the game's context. Defaults to "end".
        bot_tg_id (int, optional): Telegram ID of the bot. Defaults to BOT_TG_ID.
    """
    
    chat_id = update.effective_chat.id
    session_id = get_latest_session_by_chat(sql_connection, chat_id) 

     # --- Check if llm is enabled ---
    if not LLM_ENABLED:
        logger.warning(f"LLM is disabled in environment variables, can't send game end message")
        return False
    
    # --- Check if LLM service is available ---
    if not llm.is_available():
        logger.error("LLM service is not available, can't send game end message")
        return False
    
    # --- Get context for the message ---
    context = get_session_messages(sql_connection, session_id)
    logger.info(f"Retrieved latest game context for chat {chat_id}. Session ID: {session_id}")

    # --- Get correct system prompt ---
    if message_type == "end":
        sys_prompt = SYS_PROMPT_GAME_END
    elif message_type == "team_quiz_end":
        sys_prompt = SYS_PROMPT_TEAM_QUIZ_END
    else:
        sys_prompt = SYS_PROMPT_WITH_CONTEXT_SESSION_ONLY

    # --- Create prompt ---
    content = f"\n--- Name of the game ---\n{game_name}\n--- Base message below ---\n{base_message}\n--- Context below ---\n{context}"
    
    # --- Get response from the LLM model ---
    llm.set_sys_prompt(sys_prompt)
    llm_response = llm.chat(content)
    
    # --- Add message to the chat context ---
    add_message_to_chat_context(sql_connection, chat_id, bot_tg_id, llm_response)
    logger.info(f"Added message from bot ({bot_tg_id} to chat context ({chat_id})")

    # --- Send response to the chat ---
    await send_chat_safe(tg_context, chat_id=update.effective_chat.id, message=llm_response)
    return True
        
