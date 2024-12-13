# Telegram Game Master Bot

Welcome to the Telegram Game Master Bot project! This bot is designed to help manage and facilitate party games on Telegram.

## Features

- **Game Management**: Create custom games to play with your friends
- **Play Tournaments With Your Friends**: Play Tournaments consisting of multiple minigames. Get player based scores and see who comes out on top!
- **LLM Notifications**: An LLM-powered game master guides you through the games, follows the tournaments and gives comments when mentioned in chat

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
    export BOT_IT='id'
    export BOT_NAME='bot_username'
    ```
5. **(Optional) Configure Ollama to use LLM features**:
   Set up Ollama according to their instructions (https://ollama.com).
   Download a model, e.g.:
   ```bash
    ollama pull mistral
    ```
   Choose your preffered model in llm_utils.py.
   Run Ollama server:
   ```bash
    ollama serve
    ```
   We won't offer OpenAI API support due to data privacy concerns regarding the nature and use cases of the project.
   
    

## Usage

## Commands

- `/start` - Initialize the bot in a chat. Needs to be run privately and in the game group by each user.
- `/help` - Get help.
- `/join` - Join a Tournament waitlist. Games are based on the people on the waitlist.
- `/waitlist` - See players currently on the Tournament waitlist.
- `/players` - List registered players of the current chat.
- `/tournament (n)` - Start a tournament of n games. Default is 5 games.
- `/force_end` - End a tournament.
- `@botusername Message` - Chat with the bot. Gets the chat context in tournaments, otherwise gives zero-shot responses.
- And other commands depending on the games

## Contributing

Feel free to submit issues or pull requests. Contributions are welcome!
