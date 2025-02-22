import sqlite3
from werkzeug.security import generate_password_hash

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create users table with enhanced tracking
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  quiz_score INTEGER DEFAULT 0,
                  quiz_high_score INTEGER DEFAULT 0,
                  story_progress INTEGER DEFAULT 0,
                  story_score INTEGER DEFAULT 0,
                  total_games_played INTEGER DEFAULT 0,
                  achievements TEXT DEFAULT '[]',
                  last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Create quiz_history table
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  score INTEGER,
                  date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Create story_progress table
    c.execute('''CREATE TABLE IF NOT EXISTS story_progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  scenario_id INTEGER,
                  score INTEGER,
                  completed BOOLEAN DEFAULT 0,
                  date_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
