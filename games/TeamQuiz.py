import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import Callable

from games.Game import Game
from utils.logger import get_logger
from resources.questions import questions

logger = get_logger(__name__)

class TeamQuiz(Game):
    """
    Players are divided into teams.
    Every player gets a trivia question with 4 options.
    Only fastest answer from every team is counted.
    Round ends when a team answers correctly or all teams have answered wrong.

    NOTES:
    Options for implementation:

    - Let every team answer and correct guesses get points
    - (CURRENT) Only fastest correct answer gets points
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

        self.num_of_teams = 0
        self.rounds = 8
        self.current_round = 1
        self.questions_for_game = []
        self.team_points = {}
        self.current_question = None
        self.is_round_ongoing = False

    async def start(self):
        await self.send_group_chat(f"Let's play team quiz!")
        await self.draw_teams()
        await self.send_group_chat("Send /next when you want to start.")

        for team_id in self.teams.keys():
            self.team_points[team_id] = 0

        self.draw_questions()

        self.handlers.append(CommandHandler("next", self.next_question))
        self.handlers.append(CallbackQueryHandler(self.handle_answer, pattern=r'^quiz:'))
        self.add_handlers()

    def set_num_of_teams(self, num):
        self.num_of_teams = num

    def set_rounds(self, rounds):
        self.rounds = rounds

    async def draw_teams(self):
        num_of_players = len(self.player_ids)

        if num_of_players == 2:
            self.num_of_teams = 2

        elif self.num_of_teams == 0:
            self.num_of_teams = num_of_players // 2

        if num_of_players < 2:
            self.num_of_teams = 1

        await self.divide_players_into_teams(self.num_of_teams)

        msg = f"The teams are as follows:\n"

        for team_id, team in self.teams.items():
            msg += f"\nTeam {team_id}: "

            for j, member in enumerate(team['members']):
                if j > 0:
                    msg += ", "

                msg += member['username']

        await self.send_group_chat(msg)

    def draw_questions(self):
        self.questions_for_game = random.sample(questions, self.rounds)

    async def next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_round_ongoing = True
        self.current_question = self.questions_for_game[self.current_round - 1]

        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"quiz:{option}")]
            for option in self.current_question['options']
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.context.bot.send_message(chat_id=self.chat_id, text=self.current_question['question'],
                                            reply_markup=reply_markup)

        # TODO: decide if question is sent in the group or dm
        """        
        for player_id in self.player_ids:
            await self.context.bot.send_message(chat_id=player_id, text=self.current_question['question'],
                                                reply_markup=reply_markup)
        """

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        answering_player = update.effective_user
        answering_team = self.player_teams[answering_player.id]

        logger.info(f"Answer by {answering_player.username}")

        if not self.is_round_ongoing:
            await self.send_player_chat(answering_player.id, "Round has already ended.")
            return

        if self.teams[answering_team]['has_answered']:
            await self.send_player_chat(answering_player.id, "Your team answered already.")
            return

        query = update.callback_query
        await query.answer()
        selected_option = query.data.split(':')[1]

        logger.info(f"Selected {selected_option}")

        self.teams[answering_team]['has_answered'] = True
        correct_answers = self.current_question['correct']

        # Team is winner
        if selected_option in correct_answers:
            self.team_points[answering_team] += 1
            await self.send_group_chat(f"Round winner is team {answering_team}! {answering_player.username} "
                                       f"got the correct answer.")
            await self.end_round()

        if all(team['has_answered'] for team in self.teams.values()):
            await self.send_group_chat("Round ended. Everyone guessed wrong.")
            await self.end_round()

    async def end_round(self):
        self.is_round_ongoing = False
        # Init answers
        self.current_round += 1
        for team_id in self.teams.keys():
            self.teams[team_id]['has_answered'] = False

        if self.current_round > self.rounds:
            await self.end()
            return

        await self.send_group_chat(f"Send /next when ready for the next round.")

    async def end(self):
        await self.send_group_chat("Team quiz ended.")
        self.remove_handlers()

        self.num_of_teams = 0
        self.current_round = 1
        self.team_points = {}
        self.current_question = None
        self.is_round_ongoing = False
        self.questions_for_game = []

        if self.is_part_of_tournament:
            await self.start_next_game()
