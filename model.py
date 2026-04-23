import sqlite3
import conexao as c

#FUNÇÕES USUÁRIO
def autenticar_usuario(login, senha):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT id, nome, email FROM usuario WHERE nome = ? AND senha = ?', (login, senha))
        usuario = cur.fetchone()
        print(usuario)
        return usuario  # Retorna (id, nome) ou None

def criar_usuario(nome, email, senha):
        conn = c.get_db_conexao()
        sql_insert_query = '''
        INSERT INTO usuario (nome, email, senha)
        VALUES (?, ?, ?);
        '''
        dados = (nome, email, senha)
        conn.execute(sql_insert_query, dados)

def get_foto(usuario_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT foto FROM usuario WHERE id = ?', (usuario_id,))
        foto = cur.fetchone()[0]
        resultado = f"static/uploads/usuarios/{usuario_id}.png"
        return resultado if foto != None else None
    
def editar_perfil(usuario_id, usuario_nome, usuario_email, usuario_foto):
        conn = c.get_db_conexao()
        sql_update_query = '''
        UPDATE usuario
        SET nome = ?, email = ?, foto = ?
        WHERE id = ?;
        '''
        dados = (usuario_nome, usuario_email, usuario_foto, usuario_id)
        cur = conn.cursor()
        cur.execute(sql_update_query, dados)



#FUNÇÕES EVENTO
def config_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token):
    criar_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token)
    entralista(get_id_evento(evento_token), administrador_id)

def criar_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token):
        conn = c.get_db_conexao()        
        sql_insert_query = '''
        INSERT INTO evento (id_administrador, nome, local, data, hora, limite, token)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        '''
        dados = (administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token)
        conn.execute(sql_insert_query, dados)

def editar_evento(evento_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite):
        conn = c.get_db_conexao()
        sql_update_query = '''
        UPDATE evento
        SET nome = ?, local = ?, data = ?, hora = ?, limite = ?
        WHERE id = ?;
        '''
        dados = (evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_id)
        cur = conn.cursor()
        cur.execute(sql_update_query, dados)

def insert_lista(evento_id, usuario_id):
        conn = c.get_db_conexao()
        sql_insert_query = '''
        INSERT INTO lista (status, usuario_id, evento_id)
        VALUES (?, ?, ?);
        '''
        dados = (0, usuario_id, evento_id)
        conn.execute(sql_insert_query, dados)

def entralista(evento_id, usuario_id):
        conn = c.get_db_conexao()
        sql_insert_query = '''
        INSERT INTO lista (evento_id, usuario_id, status)
        VALUES (?, ?, ?);
        '''
        cur = conn.cursor()
        dados = (evento_id, usuario_id, 2)
        cur.execute(sql_insert_query, dados)

def get_token_evento(evento_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT token FROM evento WHERE id = ?', (evento_id,))
        resultado = cur.fetchone()
        return resultado[0] if resultado else None

def get_id_evento(evento_token):
        conn = c.get_db_conexao()
        pegar_id_evento = '''
        SELECT id 
        FROM evento 
        WHERE token = ?
        '''
        cur = conn.cursor()
        cur.execute(pegar_id_evento, (evento_token,))
        evento = cur.fetchone()
        return evento[0] if evento else None
    
def get_evento(evento_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT * FROM evento WHERE id = ?', (evento_id,))
        return cur.fetchone()

def usuarios_lista(evento_id):
    """Busca usuários com status=2 (confirmados) de um evento específico"""
    conn = c.get_db_conexao()
    pesquisar_usuarios_participantes = '''
    SELECT usuario.id, usuario.nome, usuario.email
    FROM usuario
    JOIN lista ON usuario.id = lista.usuario_id
    WHERE lista.evento_id = ?
    AND lista.status = 2
    '''
    cur = conn.cursor()
    cur.execute(pesquisar_usuarios_participantes, (evento_id,))
    usuarios = cur.fetchall()
    return usuarios  # Retorna lista de tuplas (id, nome, email)

def usuarios_solicitacoes(evento_id):
    """Busca usuários com status=1 (solicitações) de um evento específico"""
    conn = c.get_db_conexao()
    pesquisar_usuarios_solicitacoes = '''
    SELECT usuario.id, usuario.nome, usuario.email
    FROM usuario
    JOIN lista ON usuario.id = lista.usuario_id
    WHERE lista.evento_id = ?
    AND lista.status = 1
    '''
    cur = conn.cursor()
    cur.execute(pesquisar_usuarios_solicitacoes, (evento_id,))
    usuarios = cur.fetchall()
    return usuarios  # Retorna lista de tuplas (id, nome, email)

def is_evento_admin(evento_id, usuario_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT id_administrador FROM evento WHERE id = ?', (evento_id,))
        resultado = cur.fetchone()
        return resultado[0] == usuario_id if resultado else False
    
def get_num_participantes(evento_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM lista WHERE evento_id = ? AND status = 2', (evento_id,))
        resultado = cur.fetchone()
        return resultado[0] if resultado else 0

def get_status(evento_id, usuario_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('''
        SELECT status
        FROM lista
        WHERE usuario_id = ? AND evento_id = ?
        ''', (usuario_id ,evento_id))
        status = cur.fetchone()
        return status

def filtrar_proximos_eventos(id_usuario, data):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('''
        SELECT evento.*
        FROM evento
        JOIN lista ON evento.id = lista.evento_id
        WHERE lista.usuario_id = ? AND lista.status = 2 AND evento.data >= ?
        ORDER BY evento.data ASC
        ''', (id_usuario, data))
        proximos = cur.fetchall()
        return proximos
    
def filtrar_anteriores_eventos(id_usuario, data):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('''
        SELECT evento.*
        FROM evento
        JOIN lista ON evento.id = lista.evento_id
        WHERE lista.usuario_id = ? AND lista.status = 2 AND evento.data < ?
        ORDER BY evento.data DESC
        ''', (id_usuario, data))
        anteriores = cur.fetchall()
        return anteriores
    
def filtrar_eventos_proximos(session_id):
    usuario_id = session_id
    if not usuario_id:
        return []  # Retorna uma lista vazia se o usuário não estiver logado
    
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('''
        SELECT evento.*
        FROM evento
        JOIN lista ON evento.id = lista.evento_id
        WHERE lista.usuario_id = ? AND lista.status = 2
        ORDER BY evento.data ASC
        LIMIT 3
        ''', (usuario_id,))
        eventos = cur.fetchall()
        return eventos  # Retorna lista de eventos futuros do usuário

def solicitar_participacao(evento_id, usuario_id):
        conn = c.get_db_conexao()
        sql_insert_query = '''
        INSERT INTO lista (evento_id, usuario_id, status)
        VALUES (?, ?, 1);
        '''
        cur = conn.cursor()
        dados = (evento_id, usuario_id)
        cur.execute(sql_insert_query, dados)

def aceitar_solicitacao(evento_id, usuario_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('UPDATE lista SET status = 2 WHERE evento_id = ? AND usuario_id = ?', (evento_id, usuario_id))

def recusar_solicitacao(evento_id, usuario_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('DELETE FROM lista WHERE evento_id = ? AND usuario_id = ?', (evento_id, usuario_id))

def deletar_evento(evento_id,):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        # Deleta as entradas relacionadas na tabela lista
        cur.execute('DELETE FROM lista WHERE evento_id = ?', (evento_id,))
        # Deleta o evento
        cur.execute('DELETE FROM evento WHERE id = ?', (evento_id,))

def evento_ja_passou(evento_id):
        conn = c.get_db_conexao()
        cur = conn.cursor()
        cur.execute('SELECT data FROM evento WHERE id = ?', (evento_id,))
        resultado = cur.fetchone()

        if resultado:
            from datetime import datetime

            data_evento = datetime.strptime(resultado[0], '%Y-%m-%d').date()
            data_atual = datetime.now().date()

            return data_evento < data_atual

        return False