from flask_app import app
from flask_app.controllers import  login_controller, question_controller, answer_controller

if __name__=="__main__":
    app.run(debug=True)