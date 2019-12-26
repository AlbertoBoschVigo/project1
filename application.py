import os
import requests

from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from conexionDB import conectorDB

app = Flask(__name__)

# Check for environment variable
"""
Nos saltamos esta parte porque tenemos una clase para establecer la conexion
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
"""
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
headline = "Alberto´s Book Store"
# Set up database
"""
Nos saltamos esta parte porque tenemos una clase para establecer la conexion
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
"""
conexion = conectorDB()
query = "select distinct categoria from libros;"
resultado = conexion.consulta(query)
listaCategorias = []
for i in resultado:
    listaCategorias.append(i[0])
API_KEY = 'tNQIRdLGEby2aHaiZXtgQ'
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": "9781632168146"})
#print(res.json())
paginaActual = ''

def generarTabla(modo = 'index', filas = 4):
    if modo == 'index':
        query = f"select *  from libros limit { filas };"
    else:
        query = f"select * from libros where categoria like '{ modo }' limit { filas };"
    #print(query)
    resultado = conexion.consulta(query)
    #print(resultado)
    return resultado

def comprobarUsuario():
    query = f"select * from usuarios where usuario = '{ session['user_id'] }';"
    #print(query)
    resultado = conexion.consulta(query)
    if resultado and session['user_id'] == resultado[0][1] and session['user_pass'] == resultado[0][2]:
        session['logueado'] = True

@app.route("/", methods = ['GET', 'POST'])
def index():
    paginaActual = 'index'
    if session.get('logueado') is None:
        session['logueado'] = False
    resultado = generarTabla()
    if session['logueado']:
        estadoLogin = session['user_id']
    else:
        estadoLogin = False
    return render_template('index.html', headline = headline, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = estadoLogin)

@app.route("/<string:categoria>")
def contenido(categoria):
    paginaActual = categoria
    if session.get('logueado') is None:
        session['logueado'] = False
    
    resultado = generarTabla(modo = categoria, filas = 10)
    if categoria not in listaCategorias:
        return render_template('default_error.html', headline = f'La categoria "{ categoria } no existe')
    return render_template('contenido.html', headline = f'Libros de { categoria }', listaCategorias = listaCategorias, resultado = resultado)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if session.get('logueado') is None:
        session['logueado'] = False
    if request.method == 'POST':
        data = request.json
        if 'inputEmail' in request.form and 'inputPassword' in request.form:
            print('estan')
            print(request.form['inputEmail'])
            print(request.form['inputPassword'])
            
            session['user_id'] = request.form['inputEmail']
            session['user_pass'] = request.form['inputPassword']
        #request.method == 'GET'
        comprobarUsuario()
        return redirect(url_for('index')) 
        #resultado = generarTabla()
        #return render_template('index.html', headline = headline, listaCategorias = listaCategorias, resultado = resultado)

    else:
        paginaActual = 'login'
        if session['logueado']:
           return redirect(url_for('index'))  
        return render_template('login.html')

@app.route('/logout')
def logout():
    print('pre')
    for key, value in session.items():
        print(key,value)
    session.clear()
    print('post')
    for key, value in session.items():
        print(key,value)
    return redirect(url_for('index'))

