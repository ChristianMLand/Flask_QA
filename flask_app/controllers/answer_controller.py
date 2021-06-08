from flask import redirect, request, render_template, session
from flask_app import app
from flask_app.models.question_model import Question
from flask_app.models.answer_model import Answer

#----------------------Action-------------------------#
@app.post('/questions/<int:id>/answer')
def create_answer(id):
    if 'id' in session:
        if Answer.validate(**request.form):
            Answer.create(
                answer=request.form['answer'],
                answerer_id=session['id'],
                question_id=id
            )
        return redirect(f'/questions/{id}')
    return redirect('/')

@app.get('/questions/<int:qid>/approve-answer/<int:aid>')
def approve_answer(qid,aid):
    if 'id' in session:
        question = Question.retrieve_one(id=qid)
        if session['id'] == question._asker_id and not question.answered:
            question.update(answered=True)
            Answer.retrieve_one(id=aid).update(selected=True)
        return redirect(f'/questions/{qid}')
    return redirect('/')

@app.get('/questions/<int:qid>/delete-answer/<int:aid>')
def delete_answer(qid,aid):
    if 'id' in session:
        answer = Answer.retrieve_one(id=aid)
        if answer._answerer_id == session['id'] and not answer.selected:
            answer.delete()
        return redirect(f'/questions/{qid}')
    return redirect('/')
#------------------------------------------------------#