from telegram import Update
from telegram.ext import ContextTypes
from typing import Type
import random
from games.GuessNumber import GuessNumber
from games.Game import Game

class Tournament:
    def __init__(self, id: int, player_ids: list, number_of_games: int, update: Update,
                 context: ContextTypes.DEFAULT_TYPE):
        self.player_ids = player_ids
        self.update = update
        self.context = context
        self.games = []
        self.number_of_games = number_of_games

    async def start(self):
        await self.draw_games()
        # TEST
        await self.games[0].start()

    async def draw_games(self) -> None:
        # Add games whenever they get implemented
        game_classes = [GuessNumber]

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
        return game_class(id=id, player_ids=player_ids, update=update, context=context)
