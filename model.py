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
        resultado = f"static/uploads/usuarios/{usuario_id}.png"
        return resultado if foto != None else None
    
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

def criar_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite):
    with sqlite3.connect("rese.db") as conn:
        sql_insert_query = '''
        INSERT INTO evento (id_administrador, nome, local, data, hora, limite, pago, link_pagamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''
        dados = (administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite)
        conn.execute(sql_insert_query, dados)

def insert_lista(evento_id, usuario_id):
    with sqlite3.connect("rese.db") as conn:
        sql_insert_query = '''
        INSERT INTO lista (status, usuario_id, evento_id)
        VALUES (?, ?, ?);
        '''
        dados = (0, usuario_id, evento_id)
        conn.execute(sql_insert_query, dados)