import logging
import os
import db
import ollama

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from Waitlist import Waitlist
from Tournament import Tournament
from games.GuessNumber import GuessNumber
from games.ChallengeGame import ChallengeGame
from games.GuessNumber import GuessNumber

from llm_utils import LLM_MODEL, SYS_PROMPT_WITH_CONTEXT, SYS_PROMPT_NO_CONTEXT
from utils import get_username_by_id

BOT_TOKEN = os.environ['TEST_BOT_TOKEN']
BOT_NAME = "roopentestibot"
BOT_TG_ID = os.environ['TEST_BOT_ID']

# LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

sql_connection = db.connect()
waitlist = Waitlist()

"""
______ _   _ _   _ _____ _____ _____ _____ _   _  _____ 
|  ___| | | | \ | /  __ \_   _|_   _|  _  | \ | |/  ___|
| |_  | | | |  \| | /  \/ | |   | | | | | |  \| |\ `--. 
|  _| | | | | . ` | |     | |   | | | | | | . ` | `--. \
| |   | |_| | |\  | \__/\ | |  _| |_\ \_/ / |\  |/\__/ /
\_|    \___/\_| \_/\____/ \_/  \___/ \___/\_| \_/\____/                                                    
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

# TODO: Add list of commands and their descriptions
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# TODO: Add command to list all available games
# TODO: Add command to start a random game with the players in a group
# TODO: Add command to insert private information about a player (player facts)

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add member into D_PLAYER automatically when they join the group"""
    for member in update.message.new_chat_members:

        # Exclude the bot (otherwise it adds itself to the game :D)
        if member.id == BOT_TG_ID:
            continue

        logger.info(f"New member joined: {member.username}, ID: {member.id}")
        await update.message.reply_text(f"Welcome {member.first_name}")

        db.insert_player(sql_connection, member.id)

async def handle_join_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add player into waitlist when they send /join """
    user = update.effective_user

    if waitlist.add_player(user.id):
        await update.message.reply_text("Joined session succesfully")
    else:
        await update.message.reply_text("You have already joined the session")

    return
    # TODO: Add actual session id
    db.add_player_to_session(sql_connection, 1, user.id)


async def handle_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add player into D_PLAYER if not exists"""
    user_id = update.effective_user.id
    player_exists = False

    existing_players = db.get_players(sql_connection)
    for player in existing_players:
        if player[1] == user_id:
            player_exists = True
            break

    if not player_exists:
        username = await get_username_by_id(user_id, context)
        db.insert_player(sql_connection, user_id, username)

    await update.message.reply_text("Joined group succesfully")

async def list_session_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of players for current session"""
    # TODO: get from actual session and make response cleaner
    players = db.get_players(sql_connection)
    await update.message.reply_text(str(players))

async def print_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await waitlist.list_players(update, context)

async def start_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    host = update.effective_user
    session_id = db.start_session(sql_connection, host.id)
    msg_words = update.message.text.split(' ')

    try:
        number_of_games = int(msg_words[1])
    except ValueError:
        number_of_games = 5

    logger.info(f"Tournament games: {number_of_games}")

    # TODO: fix? should work though
    for player_id in waitlist.player_ids:
        db.add_player_to_session(sql_connection, session_id, player_id)

    tournament = Tournament(session_id, waitlist.player_ids, number_of_games, update, context)
    logger.info(f"Tournament {tournament}")

    waitlist.clear()
    await tournament.start()

    # TODO: implement this when needed
    # session_players = db.get_session_players(sql_connection, session_id)

async def handle_number_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    game = GuessNumber(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    logger.info(f'Guess number game start')
    await game.start()

async def handle_challenge_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    game = ChallengeGame(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    game.set_rounds(5)
    logger.info(f"Challenge game start")
    await game.start()

# TODO: Add command to end the tournament

### LLM Functions

async def generic_message_llm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    # Remove bot mention from the message
    msg = msg.replace(f'@{BOT_NAME}', '')
    sender_id = update.effective_user.id
    sender_name = await get_username_by_id(sender_id, context)
    session_id = db.get_most_recent_session_by_player(sql_connection, sender_id)

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
                    'content': f"User name: {sender_name}, User message: {msg}",
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
        if update.message.chat.type == 'group' and f'@{BOT_NAME}' in update.message.text:
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            context = db.get_session_messages(sql_connection, session_id)
            logger.info(f"Retrieved context from session ({session_id} to model: {context})")
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
            await update.message.reply_text(llm_response)

        
        # The bot is not mentioned but the message is from a group, add the message to the context
        elif update.message.chat.type == 'group' and f'@{BOT_NAME}' not in update.message.text:
            db.add_message_to_session_context(sql_connection, session_id, update.effective_user.id, msg)
            logger.info(f"Added message from sender ({sender_id} to session ({session_id})")
            return
        
        # Most likely a private message, let's not add those 
        else:
            logger.info("Private message, not adding to context")
            return

"""
___  ___  ___  _____ _   _   _     _____  ___________ 
|  \/  | / _ \|_   _| \ | | | |   |  _  ||  _  | ___ \
| .  . |/ /_\ \ | | |  \| | | |   | | | || | | | |_/ /
| |\/| ||  _  | | | | . ` | | |   | | | || | | |  __/ 
| |  | || | | |_| |_| |\  | | |___\ \_/ /\ \_/ / |    
\_|  |_/\_| |_/\___/\_| \_/ \_____/\___/  \___/\_|                                                          
"""

async def TEMP_MESSAGE_FUNCTION(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    logger.info(f"User msg: {msg}")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Create the database connection and create the tables
    db.create_tables(conn=sql_connection)

    # Register the user 
    application.add_handler(CommandHandler("start", start))
    # Help command
    application.add_handler(CommandHandler("help", help_command))
    # Join single session
    application.add_handler(CommandHandler("join", handle_join_session))
    # Join group
    application.add_handler(CommandHandler("addme", handle_join_group))
    # List current session players
    application.add_handler(CommandHandler("players", list_session_players))
    # Print waitlist
    application.add_handler(CommandHandler("waitlist", print_waitlist))
    # Start tournament / session
    application.add_handler(CommandHandler("tournament", start_tournament))
    # Games for testing
    application.add_handler(CommandHandler("numbergame", handle_number_game_start))
    application.add_handler(CommandHandler("challenges", handle_challenge_game_start))
    
    # Track users who join the group and get their ids
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    # Handle generic group messages and respond with LLM
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.ChatType.PRIVATE, generic_message_llm_handler)
    )
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()