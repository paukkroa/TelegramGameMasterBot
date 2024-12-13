from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import Forbidden
from typing import Callable
import random

import db
from utils.helpers import get_username_by_id, convert_swigs_to_units
from utils.logger import get_logger
from games.Game import Game

logger = get_logger(__name__)

class GuessNumber(Game):
    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None,
                 min_number: int = 1,
                 max_number: int = 20):
        super().__init__(name="Guess number", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game,
                         session_id=session_id)
        self.target_number = min_number - 1
        self.min_number = min_number
        self.max_number = max_number
        self.guesses = {player_id: None for player_id in player_ids} # Track guess of each user - {id, value}
        self.drinks = {player_id: None for player_id in player_ids}
        self.winner_id = 0
        self.invalid_players = []

    def set_min_number(self, min_number: int):
        self.min_number = min_number

    def set_max_number(self, max_number: int):
        self.max_number = max_number

    async def start(self):
        await self.send_group_chat(f"Let's play number game!")
        self._draw_number()

        for player_id in self.player_ids:
            response = await self.send_player_chat(player_id, f"Guess a number between {self.min_number} and {self.max_number}")
            if response == Forbidden:
                self.guesses[player_id] = self.min_number - 1 # Indicate false guess, exclude user
                self.invalid_players.append(get_username_by_id(player_id, self.context))

        if self.invalid_players:
            await self.send_group_chat(f"Could not send messages to {', '.join(self.invalid_players)}.")

        # Poll for answers in private messages
        self.handlers.append(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, self._handle_guess
        ))

        self.add_handlers()

    def _draw_number(self):
        self.target_number = random.randint(self.min_number, self.max_number)

    async def _handle_guess(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        guess = update.message.text

        try:
            guess_number = int(guess)
            if guess_number < self.min_number or guess_number > self.max_number:
                await self.send_player_chat(user_id, f"Number must be between {self.min_number} and {self.max_number}.")
                return
            self.guesses[user_id] = guess_number

            # Check if everyone has answered
            if all(guess is not None for guess in self.guesses.values()):
                await self._calculate_winner()

        except ValueError:
            self.guesses[user_id] = self.min_number - 1  # Indicate false guess, exclude user

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

        message = (f"Winner is {winner_username}! Secret number was {self.target_number} "
                   f"and they guessed {sorted_guesses[0][1]}.")

        if len(sorted_guesses) >= 2:
            second_id = sorted_guesses[1][0]
            second_username = await get_username_by_id(second_id, self.context)
            message += f' Second was {second_username}.'
            if self.session_id:
                db.add_points_to_player(self.sql_connection, self.session_id, second_id, 3)

        if len(sorted_guesses) >= 3:
            third_id = sorted_guesses[2][0]
            third_username = await get_username_by_id(third_id, self.context)
            message += f' Third was {third_username}.'
            if self.session_id:
                db.add_points_to_player(self.sql_connection, self.session_id, third_id, 1)

        # AWARD DRINKS

        message += f'\n\nDrinks awarded:\n'

        for player_id, guess in reversed_guesses:
            username = await get_username_by_id(player_id, self.context)
            difference = abs(guess - self.target_number)

            if guess == (self.min_number-1) or guess is None: # player did not obey rules
                difference = self.max_number + 1

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
        else:
            db.end_session(self.sql_connection, self.session_id)
            logger.info(f"Gamewise session {self.session_id} ended.")
        