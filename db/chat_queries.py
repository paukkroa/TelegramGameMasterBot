import sqlite3

from utils.logger import get_logger

logger = get_logger(__name__)

# TODO: Use hashing for chat_id for improved security
def create_chat(conn: sqlite3.Connection, chat_id: str, chat_name: str = '') -> None:
    cursor = conn.cursor()
    # Check if the chat_id already exists
    cursor.execute('SELECT 1 FROM D_CHAT WHERE chat_id = ?', (chat_id,))
    if cursor.fetchone() is not None:
        logger.info(f"Chat with id {chat_id}, name {chat_name} already exists in D_CHAT.")
        return

    # Insert the new chat
    cursor.execute('''
    INSERT INTO D_CHAT (chat_id, chat_name) VALUES (?, ?)
    ''', (chat_id, chat_name))
    conn.commit()

# TODO: Use hashing for chat_id for improved security
def delete_chat(conn: sqlite3.Connection, chat_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM D_CHAT WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

# TODO: Use hashing for player_id and chat_id for improved security
def add_player_to_chat(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    # Check if the player already exists in the chat
    cursor.execute('SELECT 1 FROM R_CHAT_MEMBERS WHERE chat_id = ? AND player_id = ?', (chat_id, player_id))
    if cursor.fetchone() is not None:
        logger.info(f"Player with id {player_id} already exists in chat {chat_id}.")
        return

    # Insert the player into the chat
    cursor.execute('''
    INSERT INTO R_CHAT_MEMBERS (chat_id, player_id) VALUES (?, ?)
    ''', (chat_id, player_id))
    conn.commit()

# TODO: Use hashing for player_id and chat_id for improved security
def remove_player_from_chat(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM R_CHAT_MEMBERS WHERE chat_id = ? AND player_id = ?
    ''', (chat_id, player_id))
    conn.commit()

# TODO: Use hashing for chat_id for improved security
def get_chat_member_usernames(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT dp.username 
    FROM D_PLAYER dp
    JOIN R_CHAT_MEMBERS rcm ON dp.player_id = rcm.player_id
    WHERE rcm.chat_id = ?
    ''', (chat_id,))
    usernames = cursor.fetchall()
    usernames = [username[0] for username in usernames]
    return usernames

def get_chat_member_ids(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT player_id FROM R_CHAT_MEMBERS WHERE chat_id = ?
    ''', (chat_id,))
    member_ids = cursor.fetchall()
    member_ids = [id[0] for id in member_ids]
    return member_ids