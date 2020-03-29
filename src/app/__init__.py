import os
from flask import Flask, redirect, url_for, render_template
import codecs


app = Flask(__name__, static_folder='static')
adm = False

@app.route("/")
def home_():
    return render_template("index.html", title="Análise de Gastos Públicos")

# Get variable from URL
@app.route("/<name>")
def user(name):
    return F"Hello {name}!"

@app.route("/profile/<id>")
def profile(id):
    return render_template("profile.html", id=id, title="Análise de Gastos Públicos")

@app.route("/admin")
def admin():
    if not adm:
        return redirect(url_for("home_")) # redirect for function name

if __name__ == "__main__":
    app.run(debug=True)