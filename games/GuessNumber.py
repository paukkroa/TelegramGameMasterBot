from db import *
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from typing import List, Callable
import random

from utils import get_username_by_id
from games.Game import Game


class GuessNumber(Game):
    def __init__(self, id: int, player_ids: list, update: Update, context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, start_next_game: Callable[[], None] = None):
        super().__init__(name="Guess number", id=id, player_ids=player_ids, update=update, context=context,
                         is_part_of_tournament=is_part_of_tournament, start_next_game=start_next_game)
        self.target_number = 0
        self.guesses = {player_id: None for player_id in player_ids}  # Track guess of each user; {id, value}
        self.winner_id = 0

    async def start(self):
        await self.update.message.reply_text(f"Let's play number game!")
        self._draw_number()

        for player_id in self.player_ids:
            await self.context.bot.send_message(chat_id=player_id, text="Guess a number between 1 and 20")

        # Poll for answers in private messages
        self.context.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, self._handle_guess)
        )

    def _draw_number(self):
        self.target_number = random.randint(1, 20)

    async def _handle_guess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        guess = update.message.text

        try:
            guess_number = int(guess)
            self.guesses[user_id] = guess_number

            # Check if everyone has answered
            if all(guess is not None for guess in self.guesses.values()):
                await self._calculate_winner()

        except ValueError:
            self.guesses[user_id] = 0  # Indicate false guess, exclude user

    async def _calculate_winner(self):
        closest_user_id = ""
        closest_distance = float('inf')
        closest_guess = float('inf')

        for player_id, guess in self.guesses.items():
            if guess == 0 or guess is None:  # player did not obey rules
                continue

            distance = abs(self.target_number - guess)
            if distance < closest_distance:
                closest_distance = distance
                closest_user_id = player_id
                closest_guess = guess

        if closest_user_id != "":
            username = await get_username_by_id(closest_user_id, self.context)
            await self.update.message.reply_text(
                f"Winner is {username}! Secret number was {self.target_number} and they guessed"
                f" {closest_guess}"
            )
        else:
            await self.update.message.reply_text("We do not have a winner :(")

        await self.end()

    async def end(self):
        await self.update.message.reply_text("Number game ended.")
        self.context.application.remove_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, self._handle_guess)
        )
        await self.start_next_game()
