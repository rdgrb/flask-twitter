from app import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "TB_USER"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    email = db.Column(db.String(255))
    bio = db.Column(db.String(150))
    password = db.Column(db.String(255))
    birth_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime)
    verified = db.Column(db.Boolean)

    def __init__(self, name, username, email, password, birth_date, created_at):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.birth_date = birth_date
        self.created_at = created_at


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))