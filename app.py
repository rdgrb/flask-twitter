from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user

from flask_moment import Moment
from datetime import datetime
from pytz import timezone

app = Flask("__name__")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "TWITTER_FLASK_SECRET_KEY"

local_timezone = timezone("America/Sao_Paulo")

# Inicialização e configuração do SQL-Alchemy
db = SQLAlchemy(app)

# Inicialização do Moment (pacote de formatação de datas).
moment = Moment(app)

# Inicialização e configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Importação dos módulos responsáveis pelo gerenciamento de dados/login.
from auth.forms import LoginForm, RegisterForm, EditForm
from models.User import User
from models.Tweet import Tweet

# Rotas de erros de requisição
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorhandlers/404.html'), 404

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegisterForm()

    return render_template(
        "pages/index.html", 
        form = form,
        page_title = "Twitter. É o que está acontecendo"
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    register_form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user is None:
            return render_template(
                "pages/login.html", 
                invalid_credential = True, 
                form = form, 
                register_form = register_form,
                page_title = "Entrar no Twitter"
            )

        login_user(user)

        return redirect(url_for("dashboard"))

    return render_template(
        "pages/login.html", 
        form = form, 
        register_form = register_form,
        page_title = "Entrar no Twitter"
    )

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
                form = form,
                page_title = "Inscrever-se no Twitter"
            )

        user = User(
            form.name.data,
            form.username.data,
            form.email.data,
            form.password.data,
            form.birth_date.data,
            local_timezone.localize(datetime.now()),
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    else:
        return render_template(
            "pages/register.html", 
            form = form,
            page_title = "Inscrever-se no Twitter"
        )

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

    current_date = local_timezone.localize(datetime.now())

    return render_template(
        "pages/home.html",
        active_page = "home",
        tweets = tweets,
        now = current_date,
        page_title = "Página Inicial"
    )

@app.route("/profile", defaults={ "username": -1 })
@app.route("/profile/<username>")
def profile(username):
    def search_tweets(id):
        return Tweet.query.join(User, Tweet.id_user == User.id).filter(Tweet.id_user == id).add_columns(
            Tweet.id,
            Tweet.tweet,
            Tweet.tweeted_at,
            User.id,
            User.name,
            User.username,
            User.verified,
        ).order_by(Tweet.tweeted_at.desc())

    user = {}
    tweets = {}
    active_page = "profile"

    if username == current_user.username or username == -1:
        tweets = search_tweets(current_user.id)
        user = current_user
    else:
        active_page = None

        user = User.query.filter_by(username = username).first()
        if user is not None:
            tweets = search_tweets(user.id)
    
    current_date = local_timezone.localize(datetime.now())
    form = EditForm()

    if user is None:
        return render_template(
            "pages/profile_empty.html",
            page_title = "Perfil",
            username = username
        )
    else:
        return render_template(
            "pages/profile.html",
            user = user,
            tweets = tweets,
            now = current_date,
            active_page = active_page,
            page_title = user.name,
            form = form
        )


@app.route("/send_tweet", methods=["POST"])
def send_tweet():
    tweet_form = request.form["inputTweet"]

    tweet = Tweet(
        current_user.id,
        tweet_form,
        local_timezone.localize(datetime.now())
    )

    db.session.add(tweet)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/save_edit", methods=["POST"])
def save_edit():
    form = EditForm()

    if form.validate_on_submit():
        user = User.query.filter_by(id = current_user.id).first()
        user.name = form.name.data
        user.bio = form.bio.data

        db.session.commit()
        login_user(user)

        return redirect(url_for("profile"))
    else:
        return redirect(url_for("profile"), error_while_editing = True)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)