from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask_moment import Moment
from datetime import datetime

app = Flask("__name__")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.secret_key = "TWITTER_FLASK_SECRET_KEY"

# Inicialização e configuração do SQL-Alchemy
db = SQLAlchemy(app)

# Inicialização do Moment (pacote de formatação de datas).
moment = Moment(app)

# Inicialização e configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Importação dos módulos responsáveis pelo gerenciamento de dados/login.
from auth.forms import LoginForm, RegisterForm
from models.User import User

@app.route("/")
def index():
    form = RegisterForm()

    return render_template("pages/index.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user is None:
            return render_template("login.html", invalid_credential = True, form = form)

    return render_template("pages/login.html", form = form)

@app.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    errors = {}

    if form.validate_on_submit():
        if not form.validate_email(form.email):
            errors["email"] = True

        if not form.validate_username(form.username):
            errors["username"] = True

        if errors:
            return render_template(
                "pages/register.html",
                error_email = errors["email"],
                error_username = errors["username"],
                form = form
            )

        user = User(
            form.name.data,
            form.username.data,
            form.email.data,
            form.password.data,
            datetime.utcnow(),
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    else:
        return render_template("pages/register.html", form = form)



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)