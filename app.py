"""ChemQuest — Duolingo-style chemistry/physics/math quiz app.
No authentication required — every visitor can start a quiz immediately.
"""
import os
import json
import random
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

from utils import load_questions, ensure_dirs, get_all_topics, get_options

from models import db, Question, UserProgress

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chemquest-public-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'data', 'quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

QUIZ_LENGTH = 10
XP_CORRECT = 10
XP_STREAK_BONUS = 5
XP_PERFECT_BONUS = 20
XP_PER_LEVEL = 100


def load_questions_at_start():
    with app.app_context():
        if Question.query.first() is None:
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


load_questions_at_start()


def shuffled_options(question):
    """Freshly shuffled copy of options so the answer has no fixed position."""
    opts = list(get_options(question))
    random.shuffle(opts)
    return opts


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/quiz/start')
def quiz_start():
    topic = (request.args.get('topic') or '').strip()
    if topic:
        pool = Question.query.filter_by(topic=topic).all()
        if not pool:
            flash(f'No questions found for topic: {topic}')
            return redirect(url_for('index'))
    else:
        pool = Question.query.all()
    if not pool:
        flash('No questions available yet.')
        return redirect(url_for('index'))
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
def quiz():
    index = session.get('quiz_index', 0)
    q_ids = session.get('quiz_questions', [])
    if not q_ids or index >= len(q_ids):
        return redirect(url_for('quiz_complete'))
    question = db.session.get(Question, q_ids[index])
    if question is None:
        return redirect(url_for('index'))
    return render_template('quiz.html', question=question,
                           options=shuffled_options(question),
                           index=index + 1, total=len(q_ids),
                           score=session.get('quiz_score', 0),
                           streak=session.get('quiz_streak', 0),
                           topic=session.get('quiz_topic', 'Mixed'))


@app.route('/quiz/next', methods=['GET'])
def quiz_next():
    index = session.get('quiz_index', 0)
    q_ids = session.get('quiz_questions', [])
    if not q_ids or index >= len(q_ids):
        return jsonify({"complete": True})
    question = db.session.get(Question, q_ids[index])
    if question is None:
        return jsonify({"complete": True})
    return jsonify({"complete": False, "question_id": question.id,
                    "question": question.text, "options": shuffled_options(question),
                    "question_type": question.question_type,
                    "topic": question.topic, "index": index + 1,
                    "total": len(q_ids), "score": session.get('quiz_score', 0),
                    "streak": session.get('quiz_streak', 0)})


@app.route('/quiz/submit', methods=['POST'])
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
        current_total_xp = session.get('total_xp', 0) or 0
        session['total_xp'] = current_total_xp + XP_CORRECT
        if session['quiz_streak'] % 3 == 0:
            session['total_xp'] = session['total_xp'] + XP_STREAK_BONUS
    else:
        session['quiz_streak'] = 0
    db.session.add(UserProgress(question_id=q_id,
                                answered_correctly=is_correct, topic=question.topic))
    session['quiz_index'] = index + 1
    finished = session['quiz_index'] >= len(q_ids)
    return jsonify({"correct": is_correct, "answer": question.correct_answer,
                    "explanation": question.explanation or "",
                    "score": session['quiz_score'], "streak": session['quiz_streak'],
                    "finished": finished,
                    "index": session['quiz_index'], "total": len(q_ids)})


@app.route('/quiz/complete')
def quiz_complete():
    score = session.get('quiz_score', 0)
    correct = session.get('quiz_correct', 0)
    total = session.get('quiz_total', 0)
    max_score = total * XP_CORRECT
    perfect = total > 0 and correct == total
    current_total = session.get('total_xp', 0) or 0
    if perfect and not session.get('bonus_awarded'):
        current_total += XP_PERFECT_BONUS
        session['bonus_awarded'] = True
    today = date.today().isoformat()
    last = session.get('last_quiz_date')
    if total > 0:
        if last is None:
            streak = session.get('streak_days', 0) + 1
        elif last == today:
            streak = session.get('streak_days', 0)
        elif (date.fromisoformat(today) - date.fromisoformat(last)).days == 1:
            streak = (session.get('streak_days', 0) or 0) + 1
        else:
            streak = 1
        session['streak_days'] = streak
    session['last_quiz_date'] = today
    for key in ('quiz_questions', 'quiz_index', 'quiz_score', 'quiz_streak',
                'quiz_correct', 'quiz_total', 'answered', 'quiz_topic',
                'bonus_awarded', 'total_xp', 'streak_days', 'last_quiz_date'):
        session.pop(key, None)
    return render_template('complete.html', score=score, correct=correct,
                           total=total, max_score=max_score, perfect=perfect)


@app.route('/review')
def review():
    topic_filter = (request.args.get('topic') or '').strip()
    status_filter = (request.args.get('status') or '').strip()
    progress = UserProgress.query.order_by(UserProgress.last_attempt.desc()).all()
    qmap = {q.id: q for q in Question.query.all()}
    items = [(p, qmap.get(p.question_id), get_options(qmap[p.question_id]) if p.question_id in qmap else [])
             for p in progress]
    return render_template('review.html', items=items, topics=get_all_topics(),
                           topic_filter=topic_filter, status_filter=status_filter)


@app.route('/api/questions/<topic>')
def api_questions(topic):
    questions = Question.query.filter_by(topic=topic).all()
    return jsonify([{"id": q.id, "text": q.text, "options": shuffled_options(q),
                     "correct_answer": q.correct_answer,
                     "explanation": q.explanation or "",
                     "question_type": q.question_type,
                     "difficulty": q.difficulty} for q in questions])


@app.route('/api/questions')
def api_all_questions():
    questions = Question.query.all()
    return jsonify([{"id": q.id, "text": q.text, "topic": q.topic,
                     "difficulty": q.difficulty} for q in questions])


@app.route('/api/topics')
def api_topics():
    questions = Question.query.all()
    counts = {}
    for q in questions:
        counts[q.topic] = counts.get(q.topic, 0) + 1
    return jsonify({"topics": get_all_topics(), "counts": counts})


@app.route('/admin/process-docs')
def admin_process():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return jsonify({"error": "Unauthorized"}), 403
    try:
        from document_processor import process_all_pdfs
    except Exception as e:
        return jsonify({"error": f"document processor unavailable: {e}"}), 500
    try:
        results = process_all_pdfs()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Build the response dict manually to avoid syntax issues with dict comprehensions inside jsonify
    doc_list = []
    for k, v in results.items():
        doc_list.append({
            "pages": v.get("pages"),
            "chars": v.get("chars"),
            "status": v.get("status")
        })
    total_chars = sum(v.get('chars', 0) for v in results.values())
    return jsonify({"documents": len(results), "total_chars": total_chars,
                    "files": doc_list})


if __name__ == '__main__':
    with app.app_context():
        ensure_dirs()
        db.create_all()
    app.run(debug=True, port=5000)