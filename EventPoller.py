from telegram import Update
from telegram.ext import ContextTypes
import random

from utils import get_username_by_id
from resources.phrases import all_phrases
from resources.challenges import challenges_easy

class EventPoller:
    def __init__(self, interval: int, player_ids: list, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maybe take the task as an argument at some point"""
        self.interval = interval
        self.update = update
        self.context = context
        self.task_name = "Random event"
        self.player_ids = player_ids
        self.chat_id = self.update.effective_chat.id

    async def send_group_chat(self, message: str):
        await self.context.bot.send_message(chat_id=self.chat_id, text=message)

    async def start(self):
        """Start polling"""
        job_queue = self.context.job_queue
        job_queue.run_repeating(self.task, interval=self.interval, first=self.interval, name=self.task_name)

    async def task(self, context: ContextTypes.DEFAULT_TYPE):
        """Perform a random event with a given chance"""
        chance = random.randint(1, 10)
        print(f"Random number drawn: {chance}")

        if chance == 1:
            print("Event triggered.")
            random_user_id = random.sample(self.player_ids, 1)[0]
            username = await get_username_by_id(random_user_id, self.context)

            phrase = random.sample(all_phrases, 1)[0]
            challenge = random.sample(challenges_easy, 1)[0]
            await self.send_group_chat(f"{phrase} \n\n{username}, {challenge}!")

        else:
            print("No event triggered this time.")

    def end(self):
        self.context.job_queue.get_jobs_by_name(self.task_name)[0].schedule_removal()