from flask import redirect, request, render_template, session
from flask_app import app
from flask_app.models.user_model import User
from flask_app.models.question_model import Question

#----------------------Display-------------------------#
@app.get('/dashboard')
def dashboard():
    if "id" in session:
        context = {
            'logged_user' : User.retrieve_one(id=session['id']),
            'answered_questions' : Question.retrieve_all(answered=1),
            'unanswered_questions' : Question.retrieve_all(answered=0)
        }
        return render_template('dashboard.html', **context)
    return redirect('/')

@app.get('/questions/ask')
def ask_question():
    if 'id' in session:
        return render_template('ask_question.html',logged_user=User.retrieve_one(id=session['id']))
    return redirect('/')

@app.get('/questions/<int:id>')
def view_question(id):
    if "id" in session:
        context = {
            'logged_user' : User.retrieve_one(id=session['id']),
            'question' : Question.retrieve_one(id=id)
        }
        return render_template('view_question.html',**context)
    return redirect('/')

@app.get('/questions/<int:id>/edit')
def edit_question(id):
    if 'id' in session:
        question = Question.retrieve_one(id=id)
        if question._asker_id == session['id']:
            context = {
                'logged_user' : User.retrieve_one(id=session['id']),
                'question' : question
            }
            return render_template('edit_question.html',**context)
        return redirect(f'/questions/{id}')
    return redirect('/')
#----------------------Action-------------------------#
@app.post('/questions/create')
def create_question():
    if 'id' in session:
        if Question.validate(**request.form):
            question_id = Question.create(
                question=request.form['question'],
                description=request.form['description'],
                asker_id=session['id']
            )
            return redirect(f'/questions/{question_id}')
        return redirect('/questions/ask')
    return redirect('/')

@app.post('/questions/<int:id>/update')
def update_question(id):
    if 'id' in session:
        question = Question.retrieve_one(id=id)
        if question._asker_id == session['id']:
            if Question.validate(**request.form):
                question.update(**request.form)
                return redirect(f'/questions/{id}')
        return redirect(f'/questions/{id}/edit')
    return redirect('/')

@app.get('/questions/<int:id>/delete')
def delete_question(id):
    if 'id' in session:
        question = Question.retrieve_one(id=id)
        if question._asker_id == session['id']:
            question.delete()
        return redirect('/dashboard')
    return redirect('/')
#------------------------------------------------------#
