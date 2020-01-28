import os
from flask import Flask, redirect, url_for, render_template

app = Flask(__name__, static_folder='static')
adm = False

@app.route("/")
def home():
    return render_template("index.html", Title="Home")

# Get variable from URL
@app.route("/<name>")
def user(name):
    return F"Hello {name}!"

@app.route("/admin")
def admin():
    if not adm:
        return redirect(url_for("home")) # redirect for function name

if __name__ == "__main__":
    app.run()