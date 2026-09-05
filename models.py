"""SQLAlchemy models for ChemQuest."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    explanation = db.Column(db.Text, default="")
    subject = db.Column(db.String(20), default="chemistry")
    source_doc_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    chunk_reference = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('UserProgress', backref='question', lazy='dynamic',
                               cascade='all, delete-orphan')


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    processed_date = db.Column(db.DateTime, default=datetime.utcnow)
    questions_generated = db.Column(db.Integer, default=0)


class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answered_correctly = db.Column(db.Boolean, default=False)
    attempt_count = db.Column(db.Integer, default=1)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(50))