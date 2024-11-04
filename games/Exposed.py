import random

import setuptools
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import Callable

import db
from games.Game import Game
from utils.logger import get_logger
from utils.helpers import get_username_by_id, convert_swigs_to_units, convert_shots_to_units
from resources.exposed import exposed

logger = get_logger(__name__)

class Exposed(Game):
    """
    Choose between two players and reveal their secrets.
    Played in the main chat using options.
    """
    def __init__(self,
                 id: int,
                 player_ids: list,
                 update: Update,
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False,
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None):
        super().__init__(name="Team quiz",
                         id=id,
                         player_ids=player_ids,
                         update=update,
                         context=context,
                         is_part_of_tournament=is_part_of_tournament,
                         start_next_game=start_next_game,
                         session_id=session_id)

        self.rounds = 8
        self.current_round = 1
        self.timer_seconds = 20
        self.questions_for_game = []
        self.round_votes = []
        self.vote_results = {}
        self.winners = []
        self.current_question = None
        self.is_round_ongoing = False
        self.player_points = {player_id: 0 for player_id in self.player_ids}
        self.player_usernames = {}
        self.player_has_answered = {player_id: False for player_id in self.player_ids}

    async def populate_player_usernames(self):
        for player_id in self.player_ids:
            self.player_usernames[player_id] = await get_username_by_id(player_id, self.context)

    async def start(self):
        await self.send_group_chat(f"Let's play Exposed!")
        await self.send_group_chat("Send /begin when you are ready.")

        await self.populate_player_usernames()
        self.draw_questions()

        self.handlers.append(CommandHandler("begin", self.next_question))
        self.handlers.append(CallbackQueryHandler(self.handle_answer, pattern=r'^quiz:'))
        self.add_handlers()

    def set_rounds(self, rounds):
        self.rounds = rounds

    def draw_questions(self):
        self.questions_for_game = random.sample(exposed, self.rounds)

    async def next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_round_ongoing = True
        self.round_votes = []
        self.current_question = self.questions_for_game[self.current_round - 1]

        available_options = list(self.player_usernames.values())
        logger.info(f"Available options: {available_options}")
        options = random.sample(available_options, 2)
        logger.info(f"Selected options: {options}")

        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"quiz:{option}")]
            for option in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        self.vote_results[self.current_round] = []

        await self.send_group_chat(f"You have {self.timer_seconds} seconds to answer!")
        await self.context.bot.send_message(chat_id=self.chat_id, text=self.current_question['question'],
                                            reply_markup=reply_markup)
        # Start a timer for answering
        self.context.job_queue.run_once(self.timer_end, self.timer_seconds)
        await self.context.job_queue.start()

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        answering_player = update.effective_user

        logger.info(f"Answer by {answering_player.username}")

        if not self.is_round_ongoing:
            return

        if self.player_has_answered[answering_player.id]:
            await self.send_player_chat(answering_player.id, "You have answered already.")
            return

        query = update.callback_query
        await query.answer()
        selected_option = query.data.split(':')[1]

        self.round_votes.append(selected_option)
        self.vote_results[self.current_round] = self.round_votes
        self.player_has_answered[answering_player.id] = True

        # Everyone has answered, otherwise wait for the timer to end
        if all(value for value in self.player_has_answered.values()):
            await self.context.job_queue.stop(wait=False)
            await self.end_round()
    
    async def calculate_results(self):
        results = self.vote_results[self.current_round]
        total_votes = len(results)
        distribution = {option: round(((results.count(option) / total_votes) * 100), 0) for option in set(results)}
        return distribution
        
    async def timer_end(self, context):
        await self.send_group_chat("Time's up!")
        await self.end_round()

    async def end_round(self):
        self.is_round_ongoing = False
        await self.context.job_queue.stop(wait=False)
        if len(self.round_votes) > 0:
            results = await self.calculate_results()
            result_message = "Results:\n"
            winner = 0 # 0 = no winner, 1 = winner, 2 = winner with >95% votes
            for option, percentage in results.items():
                result_message += f"{option}: {percentage}%\n"
                if percentage > 50:
                    winner = 1
                    winner_name = option
                if percentage > 95:
                    winner = 2
                    winner_name = option

            await self.send_group_chat(result_message)
            if winner == 1:
                await self.send_group_chat(f"{winner_name} you got the most votes, take three sips!")
            elif winner == 2:
                await self.send_group_chat(f"No questions about the result, {winner_name}, take a shot!")
            if winner != 0:
                self.winners.append({winner_name: winner})
        
        else:
            await self.send_group_chat("No one answered in time, everyone takes a sip!")

        self.current_round += 1

        for player_id in self.player_ids:
            self.player_has_answered[player_id] = False
        
        if self.current_round > self.rounds:
            await self.end()
            return

        await self.next_question(self.update, self.context)

    async def end(self):
        await self.send_group_chat("Thanks for playing Exposed!")
        self.remove_handlers()

        for item in self.winners:
            for username, status in item.items():
                player_id = [key for key, value in self.player_usernames.items() if value == username][0]
                if status == 1: # 3 sips
                    drink_units = convert_swigs_to_units(3)
                elif status == 2: # shot
                    drink_units = convert_shots_to_units(1)
                db.add_drinks_to_player(self.sql_connection, self.session_id, player_id, drink_units)

        self.num_of_teams = 0
        self.current_round = 1
        self.current_question = None
        self.is_round_ongoing = False
        self.questions_for_game = []

        if self.is_part_of_tournament:
            await self.start_next_game()