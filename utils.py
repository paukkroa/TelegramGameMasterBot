from telegram.error import BadRequest
from telegram.ext import ContextTypes

async def get_username_by_id(user_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    try:
        user = await context.bot.get_chat(user_id)
        username = user.username if user.username else "Incognito user"
        return username
    except BadRequest:
        return "Null"

def convert_swigs_to_units(swigs: int) -> float:
    """Expect that the drink is 5% alcohol and one 0.33l can is 24 swigs"""
    swig_ml = 330 / 24 * swigs
    alc_ml = swig_ml * 0.05
    return alc_ml / 15.2

def convert_shots_to_units(shots: int) -> float:
    """Expect that the shot is 40% alcohol and maybe 3cl"""
    alc_ml = 30 * 0.4 * shots
    return alc_ml / 15,2