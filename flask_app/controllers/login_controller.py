from flask import redirect, request, render_template, session
from flask_app.models.user_model import User
from flask_app import app,bcrypt

#----------------Display-----------------#
@app.get('/')
def index():
    return render_template('index.html')
#----------------Action------------------#
@app.post('/users/register')
def register_user():
    if User.validate(**request.form):
        session['id'] = User.create(
            username=request.form['username'],
            email=request.form['email'],
            password=bcrypt.generate_password_hash(request.form['password'])
        )
        return redirect('/dashboard')
    return redirect('/')

@app.post('/users/login')
def login_user():
    if User.validate(**request.form):
        session['id'] = User.retrieve_one(email=request.form['login_email']).id
        return redirect('/dashboard')
    return redirect('/')

@app.get('/users/logout')
def logout_user():
    session.clear()
    return redirect('/')
#-------------------------------------------#