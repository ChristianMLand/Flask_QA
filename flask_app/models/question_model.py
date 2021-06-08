from flask_app.config.orm import Schema,table

@table
class Question(Schema):
    def __init__(self, **data):
        self.id = data['id']
        self.question = data["question"]
        self.description = data["description"]
        self.answered = data["answered"]
        self._asker_id = data["asker_id"]
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @property
    def asker(self):
        return User.retrieve_one(id=self._asker_id)

    @property
    def answers(self):
        return Answer.retrieve_all(question_id=self.id,selected=False)
    
    @property
    def selected_answer(self):
        return Answer.retrieve_one(question_id=self.id,selected=True)

@Question.validator("Question must be at least 20 characters")
def question(val):
    return len(val) >= 20

from flask_app.models.answer_model import Answer
from flask_app.models.user_model import User