import os, re
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

def generarTabla(modo = 'index', filas = 100, buscar = False , columna = 'title'):
    if modo == 'index':
        if buscar:
            query = f"select *  from libros where { columna } LIKE '%{ buscar }%' limit { filas };"
        else:
            query = f"select *  from libros limit { filas };"
    elif modo == 'isbn':
        query = f"select * from libros where isbn = '{ buscar }' limit { filas };"

    elif modo == 'opinion':
        query = f"select contenido from reviews where book_id = (select id from libros where isbn = '{ buscar }');"
    else:
        if buscar:
            query = f"select *  from libros where categoria like '{ modo }' and { columna } LIKE '%{ buscar }%' limit { filas };"
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

def insertarUsuario(user, passwd):
    #insert into usuarios (usuario, password) values ('iria', '1234');
    query = f"insert into usuarios (usuario, password) values ('{ user }', '{ passwd }');"
    conexion.insertar(query)

def insertarOpinion(isbn, usuario, opinion):
    queryC = f"select id from libros where isbn = '{ isbn }';"
    resultado = conexion.consulta(queryC)
    idLibro = resultado[0][0]
    queryC = f"select id from usuarios where usuario = '{ usuario }';"
    resultado = conexion.consulta(queryC)
    idUsuario = resultado[0][0]
    queryI = f"insert into reviews (book_id, usuario_id, contenido) values ({ idLibro }, { idUsuario }, '{ opinion }');"
    conexion.insertar(queryI)

@app.route("/", methods = ['GET', 'POST'])
def index():
    gestionSesion('index')
    numPaginas = []
    if session.get('cadenaBusqueda') is None:
        resultado = generarTabla()
        if resultado:
            for i in range(1,round(len(resultado)/10)):
                numPaginas.append(i)
    else:
        resultado = generarTabla(modo = 'index', filas = 5, buscar = session['cadenaBusqueda'], columna = session['eleccion'])
        session.pop('cadenaBusqueda', None)
    #print(session.get('nuevoUsuario'))
    #print(session.get('nuevoNuevoUsuario'))
    #print('#################')
    if session.get('nuevoUsuario'):
        if session.get('nuevoNuevoUsuario') and session.get('nuevoNuevoNuevoUsuario'):
            session.pop('nuevoUsuario', None)
            session.pop('nuevoNuevoUsuario', None)
            session.pop('nuevoNuevoNuevoUsuario', None)
        else:
            session['nuevoNuevoUsuario'] = True
    nuevoUsuario = session.get('nuevoUsuario')
    nuevoNuevoUsuario = session.get('nuevoNuevoUsuario')
    #print(nuevoUsuario)
    #nuevoUsuario = True
    
    return render_template('index.html', headline = headline, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = session['user_id'], numPaginas = numPaginas, nuevoUsuario = [nuevoNuevoUsuario, nuevoUsuario])

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
        elif 'email' in request.form and 'userPassword' in request.form:
            session['user_id'] = request.form['email']
            session['user_pass'] = request.form['userPassword']
            insertarUsuario(session['user_id'], session['user_pass'])
            session['nuevoUsuario'] = session['user_id']
            session['logueado'] = False
            session['user_id'] = False
        return redirect(url_for('index')) 
    else:
        if session['logueado']:
           return redirect(url_for('index'))  
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/detalle/<string:isbn>', methods = ['GET', 'POST'])
def detalle(isbn):
    if not session['logueado']:
        return render_template('default_error.html', headline = 'Acceso no autorizado')
    else:
        if request.method == 'POST':
            print(isbn)
            isbn = request.form['isbn']
            print(isbn)
            insertarOpinion(request.form['isbn'], session['user_id'], request.form['opinion'])
            #return redirect(url_for('detalle', isbn = request.form['isbn']))
        if True:
            rating = '0'
            #print(isbn)
            resultado = generarTabla('isbn', 1, isbn)
            reviews = generarTabla(modo = 'opinion', buscar = isbn)
            #print(reviews)
            if resultado:
                resultado = resultado[0]
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": "%s" % isbn})
                if res.status_code == 200:
                    try:
                        resultadoJson = res.json()['books'][0]
                        rating = resultadoJson['average_rating']
                    except Exception as e:
                        print(e)
                """
                    {'id': 16204, 'isbn': '1592243002', 'isbn13': '9781592243006', 'ratings_count': 20497, 'reviews_count': 36044, 'text_reviews_count': 1048, 'work_ratings_count': 25450, 'work_reviews_count': 44682, 'work_text_reviews_count': 1578, 'average_rating': '3.37'}
                """
                return render_template('detalle.html', isbn = isbn, headline = headline, listaCategorias = listaCategorias, resultado = resultado, estadoLogin = session['user_id'], rating = rating, reviews = reviews)
            else:
                return render_template('default_error.html', headline = 'Isbn no encontrado')

@app.route('/api/<string:isbn>')
def api(isbn):
    [(10020, '000723368X', 'Thanks for the Memories', 'Cecelia Ahern', 2008, 'fantasia')]
    if re.search('\d{8}', isbn):
        resultado = generarTabla('isbn', 1, isbn)
        if not resultado:
            return render_template('default_error.html', headline = 'Isbn no encontrado')
        return jsonify({'isbn':resultado[0][1], 'titulo':resultado[0][2], 'autor':resultado[0][3], 'fecha publicacion':resultado[0][4], 'genero':resultado[0][5]})
    else:
        return render_template('default_error.html', headline = 'Isbn no valido')
    

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