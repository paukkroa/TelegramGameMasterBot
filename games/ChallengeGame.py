from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import random
from typing import Callable

from games.Game import Game
from resources.challenges import all_challenges
from utils import get_username_by_id

class ChallengeGame(Game):
    def __init__(self, id: int, player_ids: list, update: Update, context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, start_next_game: Callable[[], None] = None):
        super().__init__(name="Random challenges", id=id, player_ids=player_ids, update=update, context=context,
                         is_part_of_tournament=is_part_of_tournament, start_next_game=start_next_game)
        self.rounds = 10
        self.challenges = []
        self.current_challenge_number = 1

    async def start(self):
        await self.update.message.reply_text("Let's play random challenges!")
        await self.update.message.reply_text("Send /next whenever you are ready for the next challenge")

        self.context.application.add_handler(CommandHandler("next", self.get_next_challenge))

    def set_rounds(self, rounds: int):
        self.rounds = rounds

    async def get_next_challenge(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Select random challenge and user"""

        if self.current_challenge_number > self.rounds:
            await self.end()
            return

        challenge_index = random.randint(0, len(all_challenges) - 1)
        challenge = all_challenges[challenge_index]
        user_index = random.randint(0, len(self.player_ids) - 1)
        user_id = self.player_ids[user_index]

        username = await get_username_by_id(user_id, context)
        await update.message.reply_text(f"Player: {username} \nChallenge: {challenge}")

        self.current_challenge_number += 1

    async def end(self):
        """End game and remove command handler"""
        await self.update.message.reply_text("Congratulations, game ended.")
        self.context.application.remove_handler(CommandHandler("next", self.get_next_challenge))

        self.current_challenge_number = 1
        self.challenges.clear()

        await self.start_next_game()