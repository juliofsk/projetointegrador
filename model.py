import sqlite3

def autenticar_usuario(login, senha):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, nome FROM usuario WHERE nome = ? AND senha = ?', (login, senha))
        usuario = cur.fetchone()
        print(usuario)
        return usuario  # Retorna (id, nome) ou None

def criar_usuario(nome, email, senha):
    with sqlite3.connect("database.db") as conn:
        sql_insert_query = '''
        INSERT INTO usuario (nome, email, senha)
        VALUES (?, ?, ?);
        '''
        dados = (nome, email, senha)
        conn.execute(sql_insert_query, dados)