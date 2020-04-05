import os
import sys
import sqlite3
import yaml
import pandas as pd
import math
from flask import Flask, redirect, url_for, render_template

app = Flask(__name__, static_folder='static')

### Routes ###

@app.route("/")
def home_():
    suspects = get_suspects('SELECT *, printf("%.2f", TOTAL_GASTO) AS TOTAL FROM SUSPECT LIMIT 10')
    return render_template("index.html", title="Análise de Gastos Públicos", suspects=suspects)

@app.route("/profile/<id>")
def profile(id):
    spending = list_spending(id)
    suspect = get_suspects('SELECT *, printf("%.2f", TOTAL_GASTO) AS TOTAL FROM SUSPECT WHERE ID = {}'.format(id))[0]
    politic_party = get_politic_party(id)
    return render_template("profile.html", id=id, title="Análise de Gastos Públicos", suspect=suspect, party=politic_party, spending=spending)

@app.route("/shap/<id>")
def shap(id):
    shap_image = "/shap/{}_shap.html".format(id)
    spending = get_spending(id)
    p_anomaly, p_normal = percentage_spending(id)
    p_anomaly = 100 - p_normal
    print(p_anomaly)
    p_repr = spending_representativeness(id, spending[0]["VALOR"])
    return render_template("shap_viewer.html",
                                id=id,
                                title="Análise de Gastos Públicos",
                                shap_image=shap_image,
                                spending=spending,
                                p_anomaly= p_anomaly,
                                p_normal =p_normal,
                                p_repr=p_repr)

@app.route("/message")
def message():
    return "Obrigado!"

### Functions ###

def __get_db__(configurations):
    db = sqlite3.connect("." + configurations["Database"]["Path"])
    return db

def __get_config__(path=R"../configurations.yml"):
    with open(path) as file:
        configurations = yaml.load(file, Loader=yaml.FullLoader)
    return configurations

def df_to_list_dict(df):
    return list(df.T.to_dict().values())

def set_db():
    configurations = __get_config__()
    return __get_db__(configurations)

def get_suspects(query):
    db = set_db()
    suspects = df_to_list_dict(pd.read_sql_query(query, db))
    return suspects

def get_politic_party(id):
    db = set_db()
    politic_party = df_to_list_dict(pd.read_sql_query("""SELECT POLITIC_PARTY.NOME, ATUAL FROM SUSPECT
                                                        INNER JOIN SUSPECT_POLITIC_PARTY ON SUSPECT_ID = SUSPECT.ID
                                                        INNER JOIN POLITIC_PARTY ON POLITIC_PARTY_ID = POLITIC_PARTY.ID
                                                        WHERE SUSPECT.ID = {} ORDER BY 1 DESC""".format(id), db))
    return politic_party

def list_spending(suspect_id):
    db = set_db()
    query = """SELECT *, printf("%.2f", VALOR) AS VAL,  printf("%.2f", PROBABILIDADE) AS PROB 
                FROM SPENDING WHERE SUSPECT_ID =    {} AND RESULTADO = {}
                ORDER BY PROBABILIDADE DESC LIMIT 10 """
    anomaly = df_to_list_dict(pd.read_sql_query(query.format(suspect_id, -1), db))
    normal = df_to_list_dict(pd.read_sql_query(query.format(suspect_id, 1), db))
    return { "anomaly": anomaly, "normal": normal }

def get_spending(id):
    db = set_db()
    query = """SELECT *, printf("%.2f", VALOR) AS VAL, printf("%.2f", PROBABILIDADE) AS PROB 
            FROM SPENDING WHERE SPENDING_ID = {} LIMIT 1"""
    spending = df_to_list_dict(pd.read_sql_query(query.format(id), db))
    return spending

def count_spending(spending_id):
    db = set_db()
    query = """SELECT COUNT(1) FROM SPENDING WHERE SUSPECT_ID = (SELECT SUSPECT_ID FROM SPENDING WHERE SPENDING_ID = {} LIMIT 1) AND RESULTADO = {}"""
    anomaly = int(df_to_list_dict(pd.read_sql_query(query.format(spending_id, -1), db))[0]["COUNT(1)"])
    normal = int(df_to_list_dict(pd.read_sql_query(query.format(spending_id, 1), db))[0]["COUNT(1)"])
    return anomaly, normal

def percentage_spending(spending_id):
    n_anomaly, n_normal = count_spending(spending_id)
    total = n_normal + n_anomaly
    p_anomaly = math.ceil(n_anomaly/total * 100)
    p_normal = math.ceil(n_normal/total * 100)

    return p_anomaly, p_normal

def spending_representativeness(spending_id, spending_value):
    db = set_db()
    query = """SELECT SUM(VALOR) FROM SPENDING WHERE SUSPECT_ID = (SELECT SUSPECT_ID FROM SPENDING WHERE SPENDING_ID = {} LIMIT 1)"""
    total = df_to_list_dict(pd.read_sql_query(query.format(spending_id), db))[0]["SUM(VALOR)"]
    return math.ceil(spending_value / total * 100)
 

### Startup ###

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
        host = '0.0.0.0'
    except Exception as e:
        port = 5000
        host = '127.0.0.1'
    
    app.run(host=host, port=port, debug=True)