# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Flashcard, GameSession
from config import Config
from random import choice

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()
    # Initialize pre-loaded flashcards if none exist
    if Flashcard.query.count() == 0:
        init_flashcards()

def init_flashcards():
    # Predefined cybersecurity awareness flashcards
    flashcards = [
        {"question": "What is phishing?", "answer": "A technique used to trick individuals into revealing sensitive information."},
        {"question": "What does MFA stand for?", "answer": "Multi-Factor Authentication."},
        {"question": "Name a common malware type used in cyber extortion.", "answer": "Ransomware."},
        {"question": "What is the purpose of a firewall?", "answer": "To monitor and control incoming and outgoing network traffic."},
        {"question": "What does VPN stand for?", "answer": "Virtual Private Network."},
        {"question": "What is social engineering in cybersecurity?", "answer": "Manipulating individuals to divulge confidential information."}
    ]
    for card in flashcards:
        new_card = Flashcard(
            question=card['question'],
            answer=card['answer'],
            category="Cybersecurity"
        )
        db.session.add(new_card)
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter((User.username==username_or_email) | (User.email==username_or_email)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Logged in successfully!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    sessions = GameSession.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, sessions=sessions)

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process the submitted answer and display it on the same page.
        user_answer = request.form.get('answer')
        correct_answer = session.get('correct_answer')
        
        # Create or update game session to track performance
        game_session_id = session.get('game_session_id')
        if not game_session_id:
            game_session = GameSession(user_id=session['user_id'], score=0, total_attempted=0)
            db.session.add(game_session)
            db.session.commit()
            session['game_session_id'] = game_session.id
        else:
            game_session = GameSession.query.get(game_session_id)
        
        game_session.total_attempted += 1
        if user_answer.strip().lower() == correct_answer.strip().lower():
            game_session.score += 1
            result = 'correct'
        else:
            result = 'wrong'
        db.session.commit()
        
        # Render the game page with the answer feedback.
        question = session.get('current_question')
        return render_template('game.html', 
                               question=question,
                               user_answer=user_answer,
                               correct_answer=correct_answer,
                               result=result)
    else:
        # GET: Present a new flashcard question.
        flashcard = choice(Flashcard.query.all())
        session['current_question'] = flashcard.question
        session['correct_answer'] = flashcard.answer
        return render_template('game.html', question=flashcard.question)

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    game_session_id = session.get('game_session_id')
    if game_session_id:
        game_session = GameSession.query.get(game_session_id)
        score = game_session.score
        total = game_session.total_attempted
    else:
        score = 0
        total = 0
    return render_template('progress.html', score=score, total=total)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
