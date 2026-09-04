"""ChemQuest - Duolingo-style chemistry quiz app."""
import os
import json
import random
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Question, Document, UserProgress
from utils import load_questions, ensure_dirs, get_all_topics

QUIZ_LENGTH = 10
XP_CORRECT = 10
XP_STREAK_BONUS = 5       # every 3 consecutive correct
XP_PERFECT_BONUS = 20
XP_PER_LEVEL = 100

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chemquest-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'data', 'quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def get_options(question):
    """Return options as a list, tolerating legacy double-encoded JSON strings."""
    opts = question.options
    if isinstance(opts, str):
        try:
            opts = json.loads(opts)
        except (ValueError, TypeError):
            return []
    return opts if isinstance(opts, list) else []


def seed_if_empty():
    questions = load_questions()
    for q in questions:
        opts = q.get('options', [])
        if isinstance(opts, str):
            try:
                opts = json.loads(opts)
            except (ValueError, TypeError):
                opts = []
        db.session.add(Question(
            id=q['id'], text=q['text'], options=opts,
            correct_answer=q['correct_answer'],
            question_type=q.get('question_type', 'mc'),
            topic=q.get('topic', 'General'),
            difficulty=q.get('difficulty', 1),
        ))
    db.session.commit()


@app.before_request
def setup():
    if not getattr(app, '_initialized', False):
        app._initialized = True
        ensure_dirs()
        os.makedirs('data', exist_ok=True)
        db.create_all()
        if Question.query.first() is None:
            seed_if_empty()


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''
    if not username or not password:
        flash('Username and password required')
        return redirect(url_for('index'))
    if User.query.filter_by(username=username).first():
        flash('Username already exists - try logging in')
        return redirect(url_for('index'))
    user = User(username=username, password_hash=generate_password_hash(password),
                last_quiz_date=None)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST'])
def login():
    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('dashboard'))
    flash('Invalid credentials')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    questions = Question.query.all()
    user_q = UserProgress.query.filter_by(user_id=current_user.id).all()
    total_answered = len(user_q)
    total_correct = sum(1 for p in user_q if p.answered_correctly)
    accuracy = round(100 * total_correct / total_answered) if total_answered else 0
    qids_by_topic = {}
    for q in questions:
        qids_by_topic.setdefault(q.topic, set()).add(q.id)
    mastery = {}
    for topic in get_all_topics():
        tp = [p for p in user_q if p.question_id in qids_by_topic.get(topic, set())]
        mastery[topic] = round(100 * sum(1 for p in tp if p.answered_correctly) / len(tp)) if tp else 0
    today = date.today().isoformat()
    answered_today = sum(1 for p in user_q
                         if p.last_attempt and p.last_attempt.date().isoformat() == today)
    daily_goal = QUIZ_LENGTH
    level = 1 + (current_user.total_xp or 0) // XP_PER_LEVEL
    if level != current_user.level:
        current_user.level = level
        db.session.commit()
    return render_template('dashboard.html', user=current_user,
                           total_answered=total_answered, total_correct=total_correct,
                           accuracy=accuracy, mastery=mastery,
                           answered_today=min(answered_today, daily_goal),
                           daily_goal=daily_goal)


@app.route('/quiz/start')
@login_required
def quiz_start():
    topic = (request.args.get('topic') or '').strip()
    if topic:
        pool = Question.query.filter_by(topic=topic).all()
        if not pool:
            flash(f'No questions found for topic: {topic}')
            return redirect(url_for('dashboard'))
    else:
        pool = Question.query.all()
    if not pool:
        flash('No questions available yet.')
        return redirect(url_for('dashboard'))
    pool = list(pool)
    random.shuffle(pool)
    selected = pool[:QUIZ_LENGTH]
    session['quiz_questions'] = [q.id for q in selected]
    session['quiz_topic'] = topic or 'Mixed'
    session['quiz_index'] = 0
    session['quiz_score'] = 0
    session['quiz_streak'] = 0
    session['quiz_correct'] = 0
    session['quiz_total'] = len(selected)
    session['answered'] = []
    return redirect(url_for('quiz'))


@app.route('/quiz')
@login_required
def quiz():
    index = session.get('quiz_index', 0)
    q_ids = session.get('quiz_questions', [])
    if not q_ids or index >= len(q_ids):
        return redirect(url_for('quiz_complete'))
    question = db.session.get(Question, q_ids[index])
    if question is None:
        return redirect(url_for('dashboard'))
    return render_template('quiz.html', question=question,
                           options=get_options(question),
                           index=index + 1, total=len(q_ids),
                           score=session.get('quiz_score', 0),
                           streak=session.get('quiz_streak', 0),
                           topic=session.get('quiz_topic', 'Mixed'))


@app.route('/quiz/next', methods=['GET'])
@login_required
def quiz_next():
    index = session.get('quiz_index', 0)
    q_ids = session.get('quiz_questions', [])
    if not q_ids or index >= len(q_ids):
        return jsonify({"complete": True})
    question = db.session.get(Question, q_ids[index])
    if question is None:
        return jsonify({"complete": True})
    return jsonify({"complete": False, "question_id": question.id,
                    "question": question.text, "options": get_options(question),
                    "question_type": question.question_type,
                    "topic": question.topic, "index": index + 1,
                    "total": len(q_ids), "score": session.get('quiz_score', 0),
                    "streak": session.get('quiz_streak', 0)})


@app.route('/quiz/submit', methods=['POST'])
@login_required
def quiz_submit():
    data = request.get_json(silent=True) or {}
    q_id = data.get('question_id')
    selected = data.get('answer')
    index = session.get('quiz_index', 0)
    q_ids = session.get('quiz_questions', [])
    question = db.session.get(Question, q_id) if q_id is not None else None
    if question is None:
        return jsonify({"error": "Question not found"}), 404
    answered = session.get('answered', [])
    if q_id in answered:
        return jsonify({"already_answered": True, "answer": question.correct_answer,
                        "score": session.get('quiz_score', 0),
                        "streak": session.get('quiz_streak', 0)})
    answered.append(q_id)
    session['answered'] = answered

    is_correct = (selected == question.correct_answer)
    if is_correct:
        session['quiz_score'] = session.get('quiz_score', 0) + XP_CORRECT
        session['quiz_streak'] = session.get('quiz_streak', 0) + 1
        session['quiz_correct'] = session.get('quiz_correct', 0) + 1
        current_user.total_xp = (current_user.total_xp or 0) + XP_CORRECT
        if session['quiz_streak'] % 3 == 0:
            current_user.total_xp += XP_STREAK_BONUS
    else:
        session['quiz_streak'] = 0
    db.session.add(UserProgress(user_id=current_user.id, question_id=q_id,
                                answered_correctly=is_correct, topic=question.topic))
    db.session.commit()
    # Always advance - never trap the learner on one question.
    session['quiz_index'] = index + 1
    finished = session['quiz_index'] >= len(q_ids)
    return jsonify({"correct": is_correct, "answer": question.correct_answer,
                    "score": session['quiz_score'], "streak": session['quiz_streak'],
                    "finished": finished,
                    "index": session['quiz_index'], "total": len(q_ids)})


@app.route('/quiz/complete')
@login_required
def quiz_complete():
    score = session.get('quiz_score', 0)
    correct = session.get('quiz_correct', 0)
    total = session.get('quiz_total', 0)
    max_score = total * XP_CORRECT
    perfect = total > 0 and correct == total
    if perfect and not session.get('bonus_awarded'):
        current_user.total_xp = (current_user.total_xp or 0) + XP_PERFECT_BONUS
        session['bonus_awarded'] = True
    # Streak (consecutive days with a completed quiz) + level.
    today = date.today()
    if total > 0:
        last = current_user.last_quiz_date
        if last is None:
            current_user.streak_days = 1
        elif last == today:
            pass
        elif (today - last).days == 1:
            current_user.streak_days = (current_user.streak_days or 0) + 1
        else:
            current_user.streak_days = 1
        current_user.last_quiz_date = today
    current_user.level = 1 + (current_user.total_xp or 0) // XP_PER_LEVEL
    db.session.commit()
    for key in ('quiz_questions', 'quiz_index', 'quiz_score', 'quiz_streak',
                'quiz_correct', 'quiz_total', 'answered', 'quiz_topic',
                'bonus_awarded'):
        session.pop(key, None)
    return render_template('complete.html', score=score, correct=correct,
                           total=total, max_score=max_score, perfect=perfect)


@app.route('/review')
@login_required
def review():
    topic_filter = (request.args.get('topic') or '').strip()
    status_filter = (request.args.get('status') or '').strip()  # correct|wrong
    query = UserProgress.query.filter_by(user_id=current_user.id)\
        .order_by(UserProgress.last_attempt.desc())
    if topic_filter:
        query = query.filter_by(topic=topic_filter)
    if status_filter == 'correct':
        query = query.filter_by(answered_correctly=True)
    elif status_filter == 'wrong':
        query = query.filter_by(answered_correctly=False)
    progress = query.all()
    qmap = {q.id: q for q in Question.query.all()}
    items = [(p, qmap.get(p.question_id), get_options(qmap[p.question_id]) if p.question_id in qmap else [])
             for p in progress]
    return render_template('review.html', items=items, topics=get_all_topics(),
                           topic_filter=topic_filter, status_filter=status_filter)


@app.route('/api/questions/<topic>')
@login_required
def api_questions(topic):
    questions = Question.query.filter_by(topic=topic).all()
    return jsonify([{"id": q.id, "text": q.text, "options": get_options(q),
                     "correct_answer": q.correct_answer,
                     "question_type": q.question_type,
                     "difficulty": q.difficulty} for q in questions])


@app.route('/api/questions')
@login_required
def api_all_questions():
    questions = Question.query.all()
    return jsonify([{"id": q.id, "text": q.text, "topic": q.topic,
                     "difficulty": q.difficulty} for q in questions])


@app.route('/api/topics')
@login_required
def api_topics():
    counts = {}
    for q in Question.query.all():
        counts[q.topic] = counts.get(q.topic, 0) + 1
    return jsonify({"topics": get_all_topics(), "counts": counts})


@app.route('/admin/process-docs')
def admin_process():
    key = request.args.get('key', '')
    admin_key = os.environ.get('ADMIN_KEY', 'changeme')
    if request.remote_addr not in ('127.0.0.1', '::1') and key != admin_key:
        return jsonify({"error": "Unauthorized"}), 403
    try:
        from document_processor import process_all_pdfs
    except Exception as e:  # missing optional OCR deps
        return jsonify({"error": f"document processor unavailable: {e}"}), 500
    try:
        results = process_all_pdfs()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    total_chars = sum(v.get('chars', 0) for v in results.values())
    return jsonify({"documents": len(results), "total_chars": total_chars,
                    "files": {k: {"pages": v.get("pages"), "chars": v.get("chars"),
                                  "status": v.get("status")} for k, v in results.items()}})


if __name__ == '__main__':
    with app.app_context():
        ensure_dirs()
        db.create_all()
    app.run(debug=True, port=5000)
