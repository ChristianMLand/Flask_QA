from flask_app import bcrypt
from flask_app.config.orm import Schema,table
import re

@table
class User(Schema):
    def __init__(self, **data):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @property
    def questions(self):
        return Question.retrieve_all(asker_id=self.id)

    @property
    def answers(self):
        return Answer.retrieve_all(answerer_id=self.id)

@User.validator("Username name must be at least 5 characters!")
def username(val):
    return len(val) >= 2

@User.validator("Must be a valid email!")
def email(val):
    return re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$').match(val)

@User.validator("Email is already in use!")
def email(val):
    return not bool(User.retrieve_one(email=val))

@User.validator("Password must be at least 8 characters!")
def password(val):
    return len(val) >= 8

@User.validator("Passwords must match!",match="password")
def confirm_password(val,match):
    return val == match

@User.validator("Invalid Email!")
def login_email(val):
    return bool(User.retrieve_one(email=val))

@User.validator("Invalid Password!",email="login_email")
def login_password(val,email):
    user = User.retrieve_one(email=email)
    return user and bcrypt.check_password_hash(user.password,val)

from flask_app.models.question_model import Question
from flask_app.models.answer_model import Answer