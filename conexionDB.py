from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from random import choice

"""
CREATE TABLE libros (
id serial PRIMARY KEY,
isbn VARCHAR (50) NOT NULL,
title VARCHAR (50) NOT NULL,
author VARCHAR (50) NOT NULL,
year smallint NOT NULL
);
"""

class conectorDB():
    def __init__(self, usuario = 'postgres', password = '12345678', servidor = 'localhost', database = 'cursoWebCS50'):
        self.__datos_conexion = f'postgresql://{ usuario }:{ password }@{ servidor }/{ database }'
        self.__engine = create_engine(self.__datos_conexion)
        self.__sesion = scoped_session(sessionmaker(bind=self.__engine))

    def consulta(self, query):
        resultado = self.__sesion.execute(query).fetchall()
        #print(resultado)
        return resultado

    def insertar(self, query):
        #print(query)
        self.__sesion.execute(query)
        self.__sesion.commit()

        """
        try:
            conexion = engine.connect()
        except Exception as e:
            print(e)
            return False
        
        resultado = conexion.execute("select * from usuarios")
        
        #print(resultado)
        for linea in resultado:
            print(f'{ linea.id }, {linea.usuario }, { linea.password }')
        """

if __name__ == '__main__':
    
    #print(conexion.consulta("SELECT * FROM usuarios WHERE usuario = 'juan'"))
    #print(conexion.consulta("SELECT * FROM usuarios"))
    conexion = conectorDB()
    query = "select distinct categoria from libros;"
    """
    query = "UPDATE libros SET categoria = '%s' WHERE id =%d;"
    lista = ['ciencia ficcion', 'fantasia', 'policiaca', 'romantica', 'ensayo', 'historica']
    for i in range(10003,15003):
        #print(query % (choice(lista), i))
        conexion.insertar(query % (choice(lista), i))
    """
    resultado = conexion.consulta(query)
    lista = []
    for i in resultado:
        lista.append(i[0])
    print(lista)