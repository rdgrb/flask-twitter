from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired()])
    password = PasswordField('', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    username = StringField('', validators=[DataRequired()])
    email = StringField('', validators=[DataRequired()])
    password = PasswordField('', validators=[DataRequired()])