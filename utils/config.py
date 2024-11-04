import os
import db.schema as db

BOT_TOKEN = os.environ['TEST_BOT_TOKEN']
BOT_NAME = os.environ['TEST_BOT_NAME']
BOT_TG_ID = os.environ['TEST_BOT_ID']
BOT_TG_ID_STR = str(BOT_TG_ID)

sql_connection = db.connect()
current_waitlists = dict()
ongoing_tournaments = dict()