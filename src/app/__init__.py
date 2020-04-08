import os
import sys
import sqlite3
import yaml
import pandas as pd
import math
from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__, static_folder='static')

### Swagger ###

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # Our API url (can of course be a local resource)
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL,config={  'app_name': "API - Análise de Gastos Públicos"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
    p_anomaly, p_normal, p_repr = get_spending_statistics(id, spending[0]["VALOR"])
    has_file = os.path.exists("./templates" + shap_image)
    return render_template("shap_viewer.html",
                                id=id,
                                title="Análise de Gastos Públicos",
                                shap_image=shap_image,
                                spending=spending,
                                p_anomaly= p_anomaly,
                                p_normal =p_normal,
                                p_repr=p_repr,
                                has_file=has_file)

@app.route("/message")
def message():
    return "Obrigado!"

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "API - Análise de Gastos Públicos"
    return jsonify(swag) # Route to generate swagger.json documentation based on methods docstrings


@app.route('/api/list', methods=["GET"])
def list_spendings(offset=1, limit=100):
    """
        Lista todos gastos com score
        ---
        tags:
          - List
        parameters:
          - in: query
            name: offset
            schema:
              type: integer
          - in: query
            name: limit
            schema:
              type: integer
        responses:
          200:
            description: Lista com os gastos
        """
    db = set_db()

    try:
        offset = request.args.get('offset')
        limit = request.args.get('limit')
    except:
        offset = 0
        limit = 4
    
    offset = int(offset) - 1
    limit = int(limit) - 1
    
    query = """SELECT * FROM CARTOES C 
                INNER JOIN RESULTS R
                ON R.id = C.id
                LIMIT {} OFFSET {}""".format(limit, offset)

    json_ = jsonify(df_to_list_dict(pd.read_sql_query(query, db)))
    
    return json_

@app.route('/api/get', methods=["POST"])
def get_spendings():
    """
        Lista todos gastos a partir do nome do portador
        ---
        tags:
          - GetByName
        parameters:
          - in: body
            name: body
            required:
              - name
            schema:
              properties:
                name:
                  type: string
                  description: name for user
        responses:
          200:
            description: Lista com os gastos
        """
    db = set_db()

    try:
        req_data = request.get_json()
        nome = req_data["name"]
    except:
        nome = ""
    
    query = """SELECT * FROM CARTOES C 
                INNER JOIN RESULTS R
                ON R.id = C.id
                WHERE nome_portador = '{}'""".format(nome.upper())

    json_ = jsonify(df_to_list_dict(pd.read_sql_query(query, db)))
    
    return json_

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

def get_spending_statistics(id, value):
    p_anomaly, p_normal = percentage_spending(id)
    p_anomaly = 100 - p_normal
    p_repr = spending_representativeness(id, value)
    return p_anomaly, p_normal, p_repr
 

### Startup ###

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
        host = '0.0.0.0'
    except Exception as e:
        port = 5000
        host = '127.0.0.1'
    
    app.run(host=host, port=port, debug=True)