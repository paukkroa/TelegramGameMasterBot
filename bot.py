import logging
import os
import db
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import ollama

BOT_TOKEN = os.environ['TEST_BOT_TOKEN']

# LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

#TODO: Provide context for the LLM
async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    content = update.message.text
    content.replace('/chat', '')
    logger.info(f"User message: {content}")
    response = ollama.chat(model='mistral', messages=[
        {
        'role': 'system',
        'content': """You are a game master, master of games. 
        You are responsible for hosting a game of DrinkDoozle, a game where the goal is to reward and punish players with drinks.
        Be fair to each player, but if a player says a bad word to you, make sure to punish them with a drink of your choice.
        You can also reward players with drinks for good behavior.
        Answer sarcastically to players who ask you questions, but make sure to keep the game fun and engaging.""",
        },
        {
            'role': 'user',
            'content': content,
        },
    ])
    llm_response = response['message']['content']
    logger.info(f"Bot response: {llm_response}")
    await update.message.reply_text(llm_response)

# TODO: Handle generic messages according to their sender, the current context (ongoing game, group chat, etc.)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # If the message is from a group, only respond if the bot is mentioned
    if update.message.chat.type == 'group' and '@YourBotUsername' not in update.message.text:
        return
    
    msg = update.message.text
    logger.info(f"User message: {msg}")
    await update.message.reply_text(update.message.text)

# TODO: Add command to start a game session with the players inside a group
# TODO: Add command to end a game session
# TODO: Add command to list all available games
# TODO: Add command to start a random game with the players in a group
# TODO: Add command to start a tournament of multiple games (random or pre-seleted)
# TODO: Add command to insert private information about a player (player facts)

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
    sql_connection = db.connect()
    db.create_tables(conn=sql_connection)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()