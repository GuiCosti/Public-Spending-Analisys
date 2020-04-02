import os
import sqlite3
import yaml
import pandas as pd
from flask import Flask, redirect, url_for, render_template


app = Flask(__name__, static_folder='static')
adm = False

@app.route("/")
def home_():
    suspects = get_suspects('SELECT *, printf("%.2f", TOTAL_GASTO) AS TOTAL FROM SUSPECT LIMIT 10')
    return render_template("index.html", title="Análise de Gastos Públicos", suspects=suspects)

@app.route("/profile/<id>")
def profile(id):
    suspect = get_suspects(F'SELECT *, printf("%.2f", TOTAL_GASTO) AS TOTAL FROM SUSPECT WHERE ID = {id}')[0]
    politic_party = get_politic_party(id)
    print(politic_party)
    return render_template("profile.html", id=id, title="Análise de Gastos Públicos", suspect=suspect, party=politic_party)

@app.route("/admin")
def admin():
    if not adm:
        return redirect(url_for("home_")) # redirect for function name

def __get_db__(configurations):
    db = sqlite3.connect("." + configurations["Database"]["Path"])
    return db

def __get_config__(path=R"../configurations.yml"):
    with open(path) as file:
        configurations = yaml.load(file, Loader=yaml.FullLoader)
    return configurations

def df_to_list_dict(df):
    return list(df.T.to_dict().values())

def get_suspects(query):
    configurations = __get_config__()
    db = __get_db__(configurations)
    suspects = df_to_list_dict(pd.read_sql_query(query, db))
    return suspects

def get_politic_party(id):
    configurations = __get_config__()
    db = __get_db__(configurations)
    politic_party = df_to_list_dict(pd.read_sql_query("""SELECT POLITIC_PARTY.NOME, ATUAL FROM SUSPECT
                                                        INNER JOIN SUSPECT_POLITIC_PARTY ON SUSPECT_ID = SUSPECT.ID
                                                        INNER JOIN POLITIC_PARTY ON POLITIC_PARTY_ID = POLITIC_PARTY.ID
                                                        WHERE SUSPECT.ID = {} ORDER BY 1 DESC""".format(id), db))
    return politic_party
    

if __name__ == "__main__":
    app.run(debug=True)