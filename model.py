import sqlite3

def autenticar_usuario(login, senha):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, nome, email FROM usuario WHERE nome = ? AND senha = ?', (login, senha))
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

def get_foto(usuario_id):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('SELECT foto FROM usuario WHERE id = ?', (usuario_id,))
        foto = cur.fetchone()[0]
        resultado = f"static/uploads/usuarios/{usuario_id}_{foto}"
        return resultado if resultado else None
    
def editar_perfil(usuario_id, usuario_nome, usuario_email, usuario_foto):
    with sqlite3.connect("database.db") as conn:
        sql_update_query = '''
        UPDATE usuario
        SET nome = ?, email = ?, foto = ?
        WHERE id = ?;
        '''
        dados = (usuario_nome, usuario_email, usuario_foto, usuario_id)
        cur = conn.cursor()
        cur.execute(sql_update_query, dados)