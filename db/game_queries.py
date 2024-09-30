import sqlite3

def insert_game(conn: sqlite3.Connection, name: str, description: str, game_type: str, rules: str = None, telegram_commands: str = None) -> int:
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO D_GAMES (name, description, type, rules, telegram_commands) VALUES (?, ?, ?, ?, ?)
    ''', (name, description, game_type, rules, telegram_commands))
    conn.commit()
    game_id = cursor.lastrowid
    return game_id
