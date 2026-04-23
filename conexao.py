import sqlite3

def get_db_conexao():
    conn = sqlite3.connect('database.db')
    return conn