from flask_app.config.orm import Schema,table

@table
class Answer(Schema):
    def __init__(self, **data):
        self.id = data['id']
        self.answer = data['answer']
        self.selected = data['selected']
        self._answerer_id = data['answerer_id']
        self._question_id = data['question_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @property
    def question(self):
        return Question.retrieve_one(id=self._question_id)

    @property
    def answerer(self):
        return User.retrieve_one(id=self._answerer_id)

@Answer.validator("Answer must be at least 20 characters")
def answer(val):
    return len(val) >= 20

from flask_app.models.question_model import Question
from flask_app.models.user_model import User