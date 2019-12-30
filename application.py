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


def generarTabla(modo = 'index', filas = 12, buscar = False , columna = 'title'):
    if modo == 'index':
        if buscar:
            query = f"select *  from libros where { columna } LIKE '%{ buscar }%' limit { filas };"
        else:
            query = f"select *  from libros limit { filas };"
    elif modo == 'isbn':
        query = f"select * from libros where isbn = '{ buscar }' limit { filas };"
    else:
        if buscar:
            query = f"select *  from libros where categoria like '{ modo }' and { columna } LIKE '%{ buscar }%' limit { filas };"
        else:
            query = f"select * from libros where categoria like '{ modo }' limit { filas };"

    print(query)
    resultado = conexion.consulta(query)
    #print(resultado)
    return resultado

def comprobarUsuario():
    query = f"select * from usuarios where usuario = '{ session['user_id'] }';"
    #print(query)
    resultado = conexion.consulta(query)
    if resultado and session['user_id'] == resultado[0][1] and session['user_pass'] == resultado[0][2]:
        session['logueado'] = True
    else:
        session['logueado'] = False
        session['user_id'] = False

def gestionSesion(pagina):
    if session.get('logueado') is None:
        session['logueado'] = False
        session['user_id'] = False
    session['paginaActual']= pagina
    if pagina == 'index':
        session.pop('categoria', None)
    

@app.route("/", methods = ['GET', 'POST'])
def index():
    gestionSesion('index')
    if session.get('cadenaBusqueda') is None:
        resultado = generarTabla()
    else:
        resultado = generarTabla(modo = 'index', filas = 5, buscar = session['cadenaBusqueda'], columna = session['eleccion'])
        session.pop('cadenaBusqueda', None)
    return render_template('index.html', headline = headline, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = session['user_id'])

@app.route("/<string:categoria>")
def contenido(categoria):
    gestionSesion('contenido')
    if session.get('cadenaBusqueda') is None:
        resultado = generarTabla(modo = categoria, filas = 10)
    else:
        resultado = generarTabla(modo = categoria, filas = 10, buscar = session['cadenaBusqueda'], columna = session['eleccion'])
    if categoria not in listaCategorias:
        return render_template('default_error.html', headline = f'La categoria "{ categoria } no existe')
        session.pop('cadenaBusqueda', None)
    session['categoria'] = categoria
    return render_template('contenido.html', headline = categoria, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = session['user_id'])

@app.route("/login", methods = ['GET', 'POST'])
def login():
    session['paginaActual']= 'login'
    if session.get('logueado') is None:
        session['logueado'] = False
    if request.method == 'POST':
        if 'inputEmail' in request.form and 'inputPassword' in request.form:            
            session['user_id'] = request.form['inputEmail']
            session['user_pass'] = request.form['inputPassword']
        comprobarUsuario()
        return redirect(url_for('index')) 
    else:
        if session['logueado']:
           return redirect(url_for('index'))  
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/detalle/<string:isbn>')
def detalle(isbn):
    if not session['logueado']:
        return render_template('default_error.html', headline = 'Acceso no autorizado')
    else:
        resultado = generarTabla('isbn', 1, isbn)
        print(resultado[0])
        resultado = resultado[0]
        return render_template('detalle.html', isbn = isbn, headline = headline, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = session['user_id'])


@app.route('/buscar', methods = ['POST'])
def buscar():
    #print(session['paginaActual'])
    if 'inputBuscar' in request.form: 
        eleccion = request.form['inlineRadioOptions']
        #print(eleccion)
        session['eleccion'] = eleccion
        cadena = request.form['inputBuscar']
        #print(cadena)
        session['cadenaBusqueda'] = cadena
        if session['paginaActual'] == 'index':
            return redirect(url_for(session['paginaActual']))
        else:
            return redirect(url_for('contenido', categoria = session['categoria']))