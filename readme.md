# Telegram Game Master Bot

Welcome to the Telegram Game Master Bot project! This bot is designed to help manage and facilitate party games on Telegram.

## Features

- **Game Management**: Create custom games to play with your friends
- **Play Tournaments With Your Friends**: Play Tournaments consisting of multiple minigames. Get player based scores and see who comes out on top!
- **LLM Capabilities**: An LLM-powered game master guides you through the games, follows the tournaments and gives comments when mentioned in chat. Now with vision capabilities!

## Example Bot
Try this one out with **@partygamemasterbot** on Telegram! 

*Please note that the message data is stored on the server. Images are not stored.*
*LLM functionalities might be limited due to usage limits*

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/paukkroa/TelegramGameMasterBot.git
    ```
2. **Navigate to the project directory**:
    ```bash
    cd TelegramGameMasterBot
    ```
3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Export bot variables**:
    ```bash
    export BOT_TOKEN='token'
    export BOT_ID='id'
    export BOT_NAME='bot_username'
    ```
5. **(Optional) Configure LLM features**:
   ```bash
    export ENABLE_LLM='True'
    export LLM_ENGINE='ollama' (see supported APIs below)
    export LLM_MODEL='mistral'
    ```
   
## Usage

## Commands

- `/start` - Initialize the bot in a chat. Needs to be run privately and in the game group by each user.
- `/help` - Get help.
- `/join` - Join a Tournament waitlist. Games are based on the people on the waitlist.
- `/leave` - Leave a Tournament waitlist.
- `/remove @username` - Remove a player from a waitlist.
- `/waitlist` - See players currently on the Tournament waitlist.
- `/clear` - Clear the waitlist
- `/players` - List registered players of the current chat.
- `/tournament (n)` - Start a tournament of n games. Default is 5 games.
- `/force_end` - End a tournament.
- `@botusername Message` - Chat with the bot. Gets the chat context in tournaments, otherwise gives zero-shot responses.
- And other commands depending on the games

## LLM functionalities

Supported APIs are:
### - **Gemini**
Make sure you have set GOOGLE_API_KEY in environment variables
```bash
export GOOGLE_API_KEY=''
```
### - **Ollama**
Make sure Ollama is running at localhost:11434 (default Ollama port)

## Vision capabilities
The bot now supports vision capabilities! (Gemini only as of now)
Send an image to the bot and tag it to get an response.
You can also reply to previous messages to get a response from them!

## BotFather utilities
Here is the list of commands for BotFather:
```bash
start - Register into the group
join - Join the waitlist
leave - Leave the waitlist
tournament - Start the tournament
force_end - End the tournament
waitlist - See the players on the waitlist
remove - Remove player from the waitlist
group - See the players in the current group
stats_group - See stats from your group
stats_player - See personal stats
rank_latest_tournament - See rankings of the latest tournament
rank_alltime - See alltime rankings
help - Instructions
help_ai - AI instructions
```

## Contributing

Feel free to submit issues or pull requests. Contributions are welcome!
