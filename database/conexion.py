import psycopg2
from config import Config

def conectar():

    conexion = psycopg2.connect(Config.DATABASE_URL)

    return conexion

