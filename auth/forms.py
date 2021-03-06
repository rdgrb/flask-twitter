from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError

from models.User import User

class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired()])
    password = PasswordField('', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    username = StringField('', validators=[DataRequired()])
    email = StringField('', validators=[DataRequired()])
    birth_date = DateField('', validators=[DataRequired()])
    password = PasswordField('', validators=[DataRequired()])

    def validate_email(self, email):
        if User.query.filter_by(email = email.data).first():
            return False

        return True
    
    def validate_username(self, username):
        if User.query.filter_by(username = username.data).first():
            return False
            
        return True

class EditForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    bio = TextAreaField('', validators=[])
