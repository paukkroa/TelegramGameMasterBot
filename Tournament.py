from telegram import Update
from telegram.ext import ContextTypes
from typing import Type
import random

from utils import get_username_by_id
from games.GuessNumber import GuessNumber
from games.ChallengeGame import ChallengeGame
from games.Game import Game
from EventPoller import EventPoller

class Tournament:
    def __init__(self, id: int, player_ids: list, number_of_games: int, update: Update,
                 context: ContextTypes.DEFAULT_TYPE):
        self.player_ids = player_ids
        self.update = update
        self.context = context
        self.games = []
        self.number_of_games = number_of_games
        self.current_game_index = 0
        self.is_active = False
        self.poller = EventPoller(30, self.player_ids, self.update, self.context)

    async def start(self) -> None:
        self.is_active = True
        await self.draw_games()

        if self.games:
            await self.poller.start()
            await self.start_next_game()

        return
        # TEST
        await self.games[0].start()

    async def start_next_game(self) -> None:
        if self.current_game_index < len(self.games):
            current_game = self.games[self.current_game_index]

            await self.update.message.reply_text(
                f"Starting game {self.current_game_index + 1} of {self.number_of_games}"
            )
            await current_game.start()

            self.current_game_index += 1

        else:
            await self.end()

    async def draw_games(self) -> None:
        # Add games whenever they get implemented
        game_classes = [GuessNumber, ChallengeGame]

        if self.number_of_games <= 0:
            await self.update.message.reply_text("Error: number of games must be greater than 0.")
            return

        if self.number_of_games > len(game_classes):
            await self.update.message.reply_text("Warning: selected number of games is greater than available"
                                                 " games")
            self.number_of_games = len(game_classes)

        if self.number_of_games == 0:
            await self.update.message.reply_text("Error: no games selected")
            return

        selected_games = random.sample(game_classes, self.number_of_games)

        # TODO: define actual game ids
        counter = 1
        for game_class in selected_games:
            game_instance = self._create_game_instance(game_class, counter, self.player_ids, self.update, self.context)
            self.games.append(game_instance)
            counter += 1

        await self.update.message.reply_text(f"Created {len(self.games)} games")

    def set_games(self, games: list) -> None:
        self.games = games

    def _create_game_instance(self, game_class: Type[Game], id: int, player_ids: list, update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> Game:
        return game_class(id=id, player_ids=player_ids, is_part_of_tournament=True,
                          start_next_game=self.start_next_game, update=update, context=context)

    async def end(self):
        self.is_active = False
        await self.update.message.reply_text("Tournament finished!")
        self.context.job_queue.get_jobs_by_name(self.task_name)[0].schedule_removal()