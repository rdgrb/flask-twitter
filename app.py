from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user

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
from models.Tweet import Tweet


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()

    return render_template("pages/index.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user is None:
            return render_template("pages/login.html", invalid_credential = True, form = form)

        login_user(user)

        return redirect(url_for("dashboard"))

    return render_template("pages/login.html", form = form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()

    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

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

@app.route("/home")
def dashboard():
    tweets = Tweet.query.join(User, Tweet.id_user == User.id).add_columns(
        Tweet.id,
        Tweet.tweet,
        Tweet.tweeted_at,
        User.id,
        User.name,
        User.username,
        User.verified,
    ).order_by(Tweet.tweeted_at.desc())

    current_date = datetime.utcnow()

    return render_template(
        "pages/home.html",
        active_page = "home",
        tweets = tweets,
        now = current_date,
        page_title = "Página Inicial"
    )

@app.route("/profile", defaults={ "user_id": -1 })
@app.route("/profile/<user_id>")
def profile(user_id):
    def search_tweets(id):
        return Tweet.query.join(User, Tweet.id_user == User.id).filter(Tweet.id_user == id).add_columns(
            Tweet.id,
            Tweet.tweet,
            Tweet.tweeted_at,
            User.id,
            User.name,
            User.username,
        ).order_by(Tweet.tweeted_at.desc())

    user = {}
    tweets = {}
    active_page = "profile"

    if user_id == -1:
        tweets = search_tweets(current_user.id)
        user = current_user
    else:
        active_page = None

        user = User.query.filter_by(id = user_id).first()
        if user is not None:
            tweets = search_tweets(user_id)
    
    return render_template(
        "pages/profile.html",
        user = user,
        tweets = tweets,
        active_page = active_page,
        page_title = user.name
    )

@app.route("/send_tweet", methods=["POST"])
def send_tweet():
    tweet_form = request.form["inputTweet"]

    tweet = Tweet(
        current_user.id,
        tweet_form,
        datetime.utcnow()
    )

    db.session.add(tweet)
    db.session.commit()

    return redirect(url_for("dashboard"))



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)