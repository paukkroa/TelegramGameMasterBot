import os
import db.schema as db

# Telegram variables
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_NAME = os.environ['BOT_NAME']
BOT_TG_ID = os.environ['BOT_ID']
BOT_TG_ID_STR = str(BOT_TG_ID)

# LLM variables
LLM_ENABLED = os.getenv("ENABLE_LLM", 'False').lower() in ('true', '1', 't') # Allows values such as 'True', 'TRUE', 'tRuE', '1', 't'
LLM_ENGINE = os.environ['LLM_ENGINE'] # ollama, gemini
LLM_MODEL = os.environ['LLM_MODEL'] # e.g. qwen2.5:14b-instruct, gemini-2.0-flash-exp

sql_connection = db.connect()
current_waitlists = dict()
ongoing_tournaments = dict()