import os
import db.schema as db
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Telegram variables ---
BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_NAME = os.environ['BOT_NAME']
BOT_TG_ID = os.environ['BOT_ID']
BOT_TG_ID_STR = str(BOT_TG_ID)

# --- LLM variables ---
# Remember to add appropriate engine specific API keys, e.g. GOOGLE_API_KEY for Gemini 
try:
    LLM_ENABLED = os.getenv("ENABLE_LLM", 'False').lower() in ('true', '1', 't') # Allows values such as 'True', 'TRUE', 'tRuE', '1', 't'
except:
    LLM_ENABLED = False
if LLM_ENABLED:
    try:
        LLM_ENGINE = os.environ['LLM_ENGINE'] # ollama, gemini
        LLM_MODEL = os.environ['LLM_MODEL'] # e.g. qwen2.5:14b-instruct, gemini-2.0-flash-exp
    except:
        logger.error("LLM_ENGINE or LLM_MODEL not found in environment variables")
        LLM_ENGINE = None
        LLM_MODEL = None
else:
    LLM_ENGINE = None
    LLM_MODEL = None

sql_connection = db.connect()
current_waitlists = dict()
ongoing_tournaments = dict()