from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.Text, nullable=True)
    author_info = db.Column(db.Text, nullable=True)
