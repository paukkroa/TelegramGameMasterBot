import db
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from typing import Callable
import random
import sqlite3

from utils import get_username_by_id, convert_swigs_to_units
from games.Game import Game


class GuessNumber(Game):
    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 sql_connection: sqlite3.Connection = db.connect(),
                 session_id: str = None, 
                 bot_tg_id: str = None):
        super().__init__(name="Guess number", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game,
                         sql_connection=sql_connection, 
                         session_id=session_id, 
                         bot_tg_id=bot_tg_id)
        self.target_number = 0
        self.guesses = {player_id: None for player_id in player_ids} # Track guess of each user - {id, value}
        self.drinks = {player_id: None for player_id in player_ids}
        self.winner_id = 0

    async def start(self):
        await self.send_group_chat(f"Let's play number game!")
        self._draw_number()

        for player_id in self.player_ids:
            await self.send_player_chat(player_id, "Guess a number between 1 and 20")

        # Poll for answers in private messages
        self.handlers.append(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, self._handle_guess
        ))

        self.add_handlers()

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
        # Order is best first - these are lists
        sorted_guesses = sorted(self.guesses.items(), key=lambda item: abs(item[1] - self.target_number))
        # Order is worst first
        reversed_guesses = sorted_guesses[::-1]

        # POINTS AND RESULTS

        winner_id = sorted_guesses[0][0]
        winner_username = await get_username_by_id(winner_id, self.context)

        if self.session_id:
            db.add_points_to_player(self.sql_connection, self.session_id, winner_id, 5)

        message = f'''
        Winner is {winner_username}! Secret number was {self.target_number} and they guessed {sorted_guesses[0][1]}.
        '''

        if len(sorted_guesses) >= 2:
            second_id = sorted_guesses[1][0]
            second_username = await get_username_by_id(second_id, self.context)
            message += f'Second was {second_username}'
            if self.session_id:
                db.add_points_to_player(self.sql_connection, self.session_id, second_id, 3)

        if len(sorted_guesses) >= 3:
            third_id = sorted_guesses[2][0]
            third_username = await get_username_by_id(third_id, self.context)
            message += f'and third was {third_username}'
            if self.session_id:
                db.add_points_to_player(self.sql_connection, self.session_id, third_id, 1)

        # AWARD DRINKS

        message += f'\n\n Drinks awarded:\n'

        for player_id, guess in reversed_guesses:
            username = await get_username_by_id(player_id, self.context)
            difference = abs(guess - self.target_number)

            if guess == 0 or guess is None: # player did not obey rules
                difference = 20

            message += f'\n{username}: {difference}'
            drink_units = convert_swigs_to_units(difference)

            if self.session_id:
                db.add_drinks_to_player(self.sql_connection, self.session_id, player_id, drink_units)

        await self.send_group_chat(message)
        await self.end()

    async def end(self):
        await self.send_group_chat("Number game ended.")
        self.remove_handlers()

        for player_id in self.player_ids:
            if self.session_id:
                db.increase_player_game_count(self.sql_connection, self.session_id, player_id, 1)

        if self.is_part_of_tournament:
            await self.start_next_game()