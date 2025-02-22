from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_db():
    # Drop existing tables and recreate them
    conn = get_db_connection()
    conn.execute('DROP TABLE IF EXISTS users')
    conn.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        quiz_score INTEGER DEFAULT 0,
        quiz_high_score INTEGER DEFAULT 0,
        story_progress INTEGER DEFAULT 0,
        story_score INTEGER DEFAULT 0,
        total_games_played INTEGER DEFAULT 0,
        achievements TEXT DEFAULT '[]'
    )
    ''')
    
    # Create a test user
    hashed_password = generate_password_hash('test123')
    conn.execute('''
    INSERT INTO users (username, password, email, quiz_score, quiz_high_score, story_progress, story_score, total_games_played, achievements)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test', hashed_password, 'test@example.com', 0, 0, 0, 0, 0, '[]'))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):
    def __init__(self, id, username, email=None, quiz_score=0, quiz_high_score=0, story_progress=0, story_score=0, total_games_played=0, achievements='[]'):
        self.id = id
        self.username = username
        self.email = email
        self.quiz_score = quiz_score
        self.quiz_high_score = quiz_high_score
        self.story_progress = story_progress
        self.story_score = story_score
        self.total_games_played = total_games_played
        self.achievements = json.loads(achievements) if isinstance(achievements, str) else achievements

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'] if 'email' in user.keys() else None,
            quiz_score=user['quiz_score'],
            quiz_high_score=user['quiz_high_score'],
            story_progress=user['story_progress'],
            story_score=user['story_score'],
            total_games_played=user['total_games_played'],
            achievements=user['achievements']
        )
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                user_obj = User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'] if 'email' in user.keys() else None,
                    quiz_score=user['quiz_score'],
                    quiz_high_score=user['quiz_high_score'],
                    story_progress=user['story_progress'],
                    story_score=user['story_score'],
                    total_games_played=user['total_games_played'],
                    achievements=user['achievements']
                )
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            print(f"Login error: {str(e)}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')
        
        if not username or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')
            
        try:
            conn = get_db_connection()
            if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
                flash('Username already exists.', 'danger')
                return render_template('register.html')
                
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                        (username, hashed_password, email))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred during registration.', 'danger')
            print(f"Registration error: {str(e)}")
            
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/quiz_game')
@login_required
def quiz_game():
    questions = [
        {
            'question': 'What is a budget?',
            'options': [
                'A plan for spending and saving money',
                'A type of bank account',
                'A credit card limit',
                'A type of investment'
            ],
            'correct': 0
        },
        {
            'question': 'What is compound interest?',
            'options': [
                'Interest earned only on the principal amount',
                'Interest earned on both principal and accumulated interest',
                'A fixed interest rate',
                'A type of loan'
            ],
            'correct': 1
        },
        {
            'question': 'What is diversification in investing?',
            'options': [
                'Putting all money in one investment',
                'Spreading investments across different assets',
                'Saving money in a bank account',
                'Taking out multiple loans'
            ],
            'correct': 1
        }
    ]
    return render_template('quiz.html', questions=questions)

@app.route('/update_quiz_score', methods=['POST'])
@login_required
def update_quiz_score():
    score = request.json.get('score', 0)
    try:
        conn = get_db_connection()
        # Update the user's score
        current_score = current_user.quiz_score + score
        high_score = max(current_user.quiz_high_score, current_score)
        total_games = current_user.total_games_played + 1
        
        conn.execute('''
            UPDATE users 
            SET quiz_score = ?, quiz_high_score = ?, total_games_played = ?
            WHERE id = ?
        ''', (current_score, high_score, total_games, current_user.id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'new_score': current_score})
    except Exception as e:
        print(f"Error updating score: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update score'})

@app.route('/story_game')
@login_required
def story_game():
    scenarios = [
        {
            'title': 'Budgeting Basics',
            'description': 'Learn how to create and maintain a budget',
            'image': 'budget.jpg',
            'progress': 0
        },
        {
            'title': 'Smart Saving',
            'description': 'Discover strategies for effective saving',
            'image': 'saving.jpg',
            'progress': 25
        },
        {
            'title': 'Investment Introduction',
            'description': 'Start your investment journey',
            'image': 'investment.jpg',
            'progress': 50
        }
    ]
    return render_template('story.html', scenarios=scenarios)

@app.route('/update_story_progress', methods=['POST'])
@login_required
def update_story_progress():
    progress = request.json.get('progress', 0)
    try:
        conn = get_db_connection()
        conn.execute('UPDATE users SET story_progress = ? WHERE id = ?',
                    (progress, current_user.id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating progress: {str(e)}")
        return jsonify({'success': False})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True, host='0.0.0.0')
