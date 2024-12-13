import os
import db.schema as db

BOT_TOKEN = os.environ['BOT_TOKEN']
BOT_NAME = os.environ['BOT_NAME']
BOT_TG_ID = os.environ['BOT_ID']
BOT_TG_ID_STR = str(BOT_TG_ID)

sql_connection = db.connect()
current_waitlists = dict()
ongoing_tournaments = dict()