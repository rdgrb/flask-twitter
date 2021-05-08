from flask import Flask, render_template, request, redirect, url_for 
from flask_moment import Moment

# Inicialização do Flask
app = Flask("__name__")

# Inicialização do Moment (pacote de formatação de datas).
moment = Moment(app)

@app.route("/")
def index():
    return render_template("pages/index.html")

if __name__ == "__main__":
    app.run(debug=True)