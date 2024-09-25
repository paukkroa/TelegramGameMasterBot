import db
from telegram import Update
from telegram.ext import ContextTypes
import ollama
from utils import get_username_by_id
from bot import BOT_NAME

LLM_MODEL = 'mistral'
SYS_PROMPT_NO_CONTEXT = """Your name is Game Master. You are responsible for helping the user with their game-related questions. You will also be responsible for hosting a party game with the goal to get everyone as drunk as possible.
You can provide hints, tips, and tricks to the user to help them win the game.
Use humor and sarcasm in your answers. IMPORTANT: Keep your answers short!
You can also provide information about the game rules and mechanics to the user.
Use the user's language in your responses and make sure to keep the conversation engaging and fun.
Be helpful and supportive. You can also use humor to make the conversation more interesting.
You have no access to the chat history and you can only see the current message from the user. If the user asks about this, you can say that you are a bot and you don't have access to the chat history for security reasons.
You can be evil sometimes, remember that your goal is to get everyone drunk!
Remember to keep your answers short!"""
SYS_PROMPT_WITH_CONTEXT = """Your name is Game Master. You are responsible for hosting a party game with the goal to get everyone as drunk as possible.
Use humor and sarcasm in your answers. IMPORTANT: Keep your answers short!
You can also provide information about the game rules and mechanics to the user.
Use the user's language in your responses and make sure to keep the conversation engaging and fun.
You will be provided with the message history of the on going tournament as 'Context', which you can and will use when crafting your responses
Remember to keep your answers short!
You can be evil sometimes, remember that your goal is to get everyone drunk!"""

async def generic_message_llm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, sql_connection, logger) -> None:
    msg = update.message.text
    sender_id = update.effective_user.id
    session_id = db.get_most_recent_session_by_player(sql_connection, sender_id)
    logger.info(f"session_id: {session_id}, type: {type(session_id)}")
    # No ongoing session, respond if needed
    if session_id is None:
        logger.info(f"User message does not belong to any active session")
        # Private message, respond directly
        if update.message.chat.type != 'group':
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_NO_CONTEXT,
                },
                {
                    'role': 'user',
                    'content': msg,
                },
            ])
            llm_response = response['message']['content']
            await update.message.reply_text(llm_response)

        # Group message, reply to the user only if bot is mentioned
        elif update.message.chat.type == 'group' and f'@{BOT_NAME}' in update.message.text:
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_NO_CONTEXT,
                },
                {
                    'role': 'user',
                    'content': msg,
                },
            ])
            llm_response = response['message']['content']
            await update.message.reply_text(llm_response)
        
    # Ongoing session, handle context
    else:
        # If the message is from a group, only respond if the bot is mentioned
        # then we only want to add message to the context
        if update.message.chat.type == 'group' and f'@{BOT_NAME}' in update.message.text:
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            context = db.get_session_messages(sql_connection, session_id)
            response = ollama.chat(model=LLM_MODEL, messages=[
                {
                'role': 'system',
                'content': SYS_PROMPT_WITH_CONTEXT,
                },
                {
                    'role': 'user',
                    'content': f"User name: {get_username_by_id(sender_id)}, User message: {msg}, Context: {context}",
                },
            ])
            llm_response = response['message']['content']
            await update.message.reply_text(llm_response)

        
        # The bot is not mentioned
        else:
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            return