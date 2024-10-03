import sqlite3


def connect(db: str = 'drink_games.db') -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    return conn

def close_connection(conn: sqlite3.Connection) -> None:
    conn.close()

def create_tables(conn: sqlite3.Connection) -> None:
    # Registered players D_PLAYER
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_PLAYER (
        player_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Facts for trivias D_PLAYER_FACTS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_PLAYER_FACTS (
        fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        fact TEXT NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Chat information D_CHAT
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_CHAT (
        chat_id TEXT PRIMARY KEY,
        chat_name TEXT,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_CHAT_SETTINGS (
        chat_id TEXT PRIMARY KEY,
        context_window_type TEXT NOT NULL DEFAULT 'all', -- all, static, rolling
        rolling_context_window_size INTEGER, -- in seconds
        static_window_start_time TIMESTAMP,
        static_window_end_time TIMESTAMP,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Chat members R_CHAT_MEMBERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_CHAT_MEMBERS (
        chat_id TEXT NOT NULL,
        player_id INTEGER NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES D_CHAT(chat_id),
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Game sessions D_SESSION
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_SESSION (
        session_id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        chat_running_id INTEGER NOT NULL DEFAULT 1,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        ongoing BOOLEAN DEFAULT 1,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES D_CHAT(chat_id)
    );
    ''')

    # Session participants R_SESSION_PLAYERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_PLAYERS (
        session_id TEXT NOT NULL,
        player_id INTEGER,
        points INTEGER DEFAULT 0,
        drink_units FLOAT DEFAULT 0,
        games INTEGER DEFAULT 0,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id),
        FOREIGN KEY (session_id) REFERENCES D_PLAYER(session_id)
    );
    ''')

    # All available games D_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_GAMES (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL,
        rules TEXT,
        telegram_commands TEXT,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Games played in sessions R_SESSION_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_GAMES (
        session_id TEXT NOT NULL,
        game_id INTEGER NOT NULL,
        winner_id INTEGER NOT NULL,
        loser_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES D_SESSION(session_id),
        FOREIGN KEY (game_id) REFERENCES D_GAMES(game_id),
        FOREIGN KEY (winner_id) REFERENCES D_PLAYER(player_id),
        FOREIGN KEY (loser_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Chat context R_CHAT_CONTEXT
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_CHAT_CONTEXT (
        chat_id TEXT NOT NULL,
        session_id TEXT,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES D_CHAT(chat_id),
        FOREIGN KEY (session_id) REFERENCES D_SESSION(session_id),
        FOREIGN KEY (sender_id) REFERENCES D_PLAYER(player_id)
    );
    ''')