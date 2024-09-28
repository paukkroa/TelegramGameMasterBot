import logging
import os
import db

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from Waitlist import Waitlist
from Tournament import Tournament
from games.GuessNumber import GuessNumber
from games.ChallengeGame import ChallengeGame
from games.GuessNumber import GuessNumber

from utils import get_username_by_id
from ai_utils.llm import generic_message_llm_handler

BOT_TOKEN = os.environ['TEST_BOT_TOKEN']
BOT_NAME = "roopentestibot"
BOT_TG_ID = os.environ['TEST_BOT_ID']
BOT_TG_ID_STR = str(BOT_TG_ID)

# LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

sql_connection = db.connect()
current_waitlists = dict()
ongoing_tournaments = dict()

"""
______ _   _ _   _ _____ _____ _____ _____ _   _  _____ 
|  ___| | | | \ | /  __ \_   _|_   _|  _  | \ | |/  ___|
| |_  | | | |  \| | /  \/ | |   | | | | | |  \| |\ `--. 
|  _| | | | | . ` | |     | |   | | | | | | . ` | `--. \
| |   | |_| | |\  | \__/\ | |  _| |_\ \_/ / |\  |/\__/ /
\_|    \___/\_| \_/\____/ \_/  \___/ \___/\_| \_/\____/                                                    
"""

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

# TODO: This might be obsolete with the new /start command
async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add member into D_PLAYER automatically when they join the group"""
    for member in update.message.new_chat_members:

        # Exclude the bot (otherwise it adds itself to the game :D)
        if str(member.id) == BOT_TG_ID_STR:
            continue

        logger.info(f"New member joined: {member.username}, ID: {member.id}")
        await update.message.reply_text(f"Welcome {member.first_name}")

        db.insert_player(sql_connection, member.id)

async def handle_join_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add player into waitlist when they send /join """
    user = update.effective_user
    chat_id = update.effective_chat.id

    if chat_id in current_waitlists.keys():
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist exists for chat {chat_id}: {waitlist}")
    else:
        waitlist = Waitlist(chat_id)
        current_waitlists[chat_id] = waitlist
        logger.info(f"Created new waitlist for chat {chat_id}: {waitlist}")

    if waitlist.add_player(user.id):
        logger.info(f"Player {user.id} added to waitlist in chat {chat_id}")
        logger.info(f"Current waitlist: {waitlist.player_ids}")
        await update.message.reply_text("Joined session succesfully")
    else:
        await update.message.reply_text("You have already joined the session")
        logger.info(f"Player {user.id} already in waitlist in chat {chat_id}")
        logger.info(f"Current waitlist: {waitlist.player_ids}")

# TODO: Delete this command as it is most likely obsolete (replaced by /start)
async def handle_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add player into D_PLAYER if not exists"""
    user_id = update.effective_user.id
    player_exists = False

    existing_players = db.get_all_players(sql_connection)
    logger.info(f"Existing players: {existing_players}")
    for player in existing_players:
        if player[0] == user_id:
            player_exists = True
            break

    if not player_exists:
        username = await get_username_by_id(user_id, context)
        db.insert_player(sql_connection, user_id, username)
        await update.message.reply_text("Joined group succesfully")
    else:
        await update.message.reply_text("You are already a member of this group")

async def list_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of all registered players in databse"""
    # TODO: get from actual session and make response cleaner
    players = db.get_all_players(sql_connection)
    await update.message.reply_text(str(players))

# TODO: Fix this
async def list_group_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of all registered players in the current chat"""
    chat_id = update.effective_chat.id
    players = db.get_chat_members(sql_connection, chat_id)
    players_str = "Group members: "
    for player in players:
        players_str += f"{player}, "
    players_str = players_str[:-2]
    await update.message.reply_text(str(players_str))    

async def print_waitlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    try:
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist found for chat {chat_id}: {waitlist}")
        await waitlist.list_players(update, context)
    except KeyError:
        logger.info(f"No waitlist found for chat {chat_id}")
        await update.message.reply_text("No waitlist found for the chat. Press /join to join the waitlist.")

async def start_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    try:
        waitlist = current_waitlists[chat_id]
        logger.info(f"Waitlist found for chat {chat_id}: {waitlist}")
    except KeyError:
        logger.info(f"No waitlist found for chat {chat_id}")
        await update.message.reply_text("No players are on the waitlist, cannot start tournament. Press /join to join the waitlist.")
        return
    
    session_id = db.start_session(sql_connection, chat_id)
    logger.info(f"Session {session_id} started for chat {chat_id}")
    # Add extra empty char to list to prevent index out of range error
    msg_words = update.message.text.split(' ') + ['']

    try:
        number_of_games = int(msg_words[1])
    except ValueError:
        number_of_games = 5

    logger.info(f"Tournament games: {number_of_games}")

    for player_id in waitlist.player_ids:
        logger.info(f"Adding player {player_id} to session {session_id}")
        db.add_player_to_session(sql_connection, session_id, player_id)

    # TODO: test if this works as intended. The session id should keep it in check(?)
    tournament = Tournament(session_id, waitlist.player_ids, number_of_games, update, context, sql_connection, BOT_TG_ID)
    ongoing_tournaments[chat_id] = tournament
    logger.info(f"Tournament {tournament}")

    waitlist.clear() # Is this needed anymore?
    del current_waitlists[chat_id]
    await tournament.start()

async def end_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """End the current session"""
    chat_id = update.effective_chat.id
    try:
        tournament = ongoing_tournaments[chat_id]
        logger.info(f"Tournament found for chat {chat_id}: {tournament}")
    except KeyError:
        logger.info(f"No tournament found for chat {chat_id}, checking for open sessions")
        session_id = db.get_most_recent_session_by_chat(sql_connection, chat_id)
        if session_id is not None:
            db.end_session(sql_connection, session_id)
            await update.message.reply_text("Session has been ended.")
        else:
            await update.message.reply_text("No active tournament found to end.")
        return
    
    await tournament.end()
    del ongoing_tournaments[chat_id]
    del tournament

    await update.message.reply_text(f"Tournament has been ended.")

# TODO: Fix the below functions to work with the current_waitlist dict
# or delete them completely
async def handle_number_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    game = GuessNumber(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    logger.info(f'Guess number game start')
    await game.start()

async def handle_challenge_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    game = ChallengeGame(id=1, player_ids=waitlist.player_ids, update=update, context=context)
    game.set_rounds(5)
    logger.info(f"Challenge game start")
    await game.start()

async def handle_generic_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await generic_message_llm_handler(update, context, sql_connection, BOT_NAME, BOT_TG_ID)

"""
___  ___  ___  _____ _   _   _     _____  ___________ 
|  \/  | / _ \|_   _| \ | | | |   |  _  ||  _  | ___ \
| .  . |/ /_\ \ | | |  \| | | |   | | | || | | | |_/ /
| |\/| ||  _  | | | | . ` | | |   | | | || | | |  __/ 
| |  | || | | |_| |_| |\  | | |___\ \_/ /\ \_/ / |    
\_|  |_/\_| |_/\___/\_| \_/ \_____/\___/  \___/\_|                                                          
"""

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Create the database connection and create the tables
    db.create_tables(conn=sql_connection)

    # Add bot id to D_PLAYER if not exists
    db.insert_player(sql_connection, BOT_TG_ID, BOT_NAME)

    # Register the user and chat
    application.add_handler(CommandHandler("start", start))
    # Help command
    application.add_handler(CommandHandler("help", help_command))
    # Join single session
    application.add_handler(CommandHandler("join", handle_join_waitlist))
    # Join group
    # Commented out because it's not needed with the new /start command
    # application.add_handler(CommandHandler("addme", handle_join_group))
    # List current session players
    application.add_handler(CommandHandler("all_players", list_all_players))
    # List group members
    application.add_handler(CommandHandler("group", list_group_members))
    # Print waitlist
    application.add_handler(CommandHandler("waitlist", print_waitlist))
    # Start tournament / session
    application.add_handler(CommandHandler("tournament", start_tournament))
    # end tournament / session
    application.add_handler(CommandHandler("force_end", end_session))
    # Games for testing
    application.add_handler(CommandHandler("numbergame", handle_number_game_start))
    application.add_handler(CommandHandler("challenges", handle_challenge_game_start))
    
    # Track users who join the group and get their ids
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    # Handle generic group messages and respond with LLM
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.ChatType.PRIVATE, handle_generic_message)
    )
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":
    main()