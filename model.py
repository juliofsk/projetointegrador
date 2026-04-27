import sqlite3
import conexao as c
from datetime import datetime
from werkzeug.security import check_password_hash


# === USUÁRIO ===

def autenticar_usuario(login, senha):
    """Busca usuário pelo nome e verifica a senha. Retorna (id, nome, email) ou None."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT id, nome, email, senha FROM usuario WHERE nome = ?', (login,))
    usuario = cur.fetchone()
    conn.close()
    if usuario and check_password_hash(usuario[3], senha):
        return (usuario[0], usuario[1], usuario[2])
    return None

def criar_usuario(nome, email, senha):
    """Insere um novo usuário no banco. A senha deve ser passada já com hash."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?);',
        (nome, email, senha)
    )
    conn.commit()
    conn.close()

def get_foto(usuario_id):
    """Retorna o caminho da foto do usuário ou None se não tiver foto cadastrada."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT foto FROM usuario WHERE id = ?', (usuario_id,))
    resultado = cur.fetchone()
    conn.close()
    if resultado and resultado[0]:
        return f"static/uploads/usuarios/{usuario_id}.png"
    return None

def editar_perfil(usuario_id, nome, email, foto):
    """Atualiza nome, email e foto do usuário."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'UPDATE usuario SET nome = ?, email = ?, foto = ? WHERE id = ?;',
        (nome, email, foto, usuario_id)
    )
    conn.commit()
    conn.close()


# === EVENTO ===

def criar_evento(id_administrador, nome, local, data, hora, limite, token):
    """
    Insere um novo evento no banco e adiciona o administrador como participante confirmado.
    Retorna o id do evento criado.
    """
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO evento (id_administrador, nome, local, data, hora, limite, token) VALUES (?, ?, ?, ?, ?, ?, ?);',
        (id_administrador, nome, local, data, hora, limite, token)
    )
    conn.commit()
    evento_id = cur.lastrowid
    conn.close()
    entrar_na_lista(evento_id, id_administrador)
    return evento_id

def editar_evento(evento_id, nome, local, data, hora, limite):
    """Atualiza os dados de um evento existente."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'UPDATE evento SET nome = ?, local = ?, data = ?, hora = ?, limite = ? WHERE id = ?;',
        (nome, local, data, hora, limite, evento_id)
    )
    conn.commit()
    conn.close()

def deletar_evento(evento_id):
    """Remove o evento e todos os registros de lista associados."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('DELETE FROM lista WHERE evento_id = ?', (evento_id,))
    cur.execute('DELETE FROM evento WHERE id = ?', (evento_id,))
    conn.commit()
    conn.close()

def get_evento(evento_id):
    """Retorna todos os dados de um evento pelo id, ou None se não encontrado."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT * FROM evento WHERE id = ?', (evento_id,))
    resultado = cur.fetchone()
    conn.close()
    return resultado

def get_id_evento(token):
    """Retorna o id do evento correspondente ao token, ou None."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT id FROM evento WHERE token = ?', (token,))
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def get_token_evento(evento_id):
    """Retorna o token do evento pelo id, ou None."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT token FROM evento WHERE id = ?', (evento_id,))
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def is_admin_evento(evento_id, usuario_id):
    """Retorna True se o usuário for o administrador do evento."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT id_administrador FROM evento WHERE id = ?', (evento_id,))
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] == usuario_id if resultado else False

def evento_ja_passou(evento_id):
    """Retorna True se a data do evento já passou."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT data FROM evento WHERE id = ?', (evento_id,))
    resultado = cur.fetchone()
    conn.close()
    if resultado:
        data_evento = datetime.strptime(resultado[0], '%Y-%m-%d').date()
        return data_evento < datetime.now().date()
    return False

def get_num_participantes(evento_id):
    """Retorna o número de participantes confirmados (status=2) de um evento."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM lista WHERE evento_id = ? AND status = 2', (evento_id,))
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] if resultado else 0

def get_eventos_usuario(usuario_id, data_corte, futuros=True):
    """
    Retorna eventos do usuário confirmados (status=2).
    Se futuros=True, traz eventos a partir de data_corte em ordem crescente.
    Se futuros=False, traz eventos anteriores a data_corte em ordem decrescente.
    """
    conn = c.get_db_conexao()
    cur = conn.cursor()
    operador = '>=' if futuros else '<'
    ordem = 'ASC' if futuros else 'DESC'
    cur.execute(f'''
        SELECT evento.*
        FROM evento
        JOIN lista ON evento.id = lista.evento_id
        WHERE lista.usuario_id = ? AND lista.status = 2 AND evento.data {operador} ?
        ORDER BY evento.data {ordem}
    ''', (usuario_id, data_corte))
    eventos = cur.fetchall()
    conn.close()
    return eventos

def get_tres_proximos_eventos(usuario_id):
    """Retorna até 3 eventos mais próximos do usuário para exibir na home."""
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
    conn.close()
    return eventos


# === LISTA ===

def entrar_na_lista(evento_id, usuario_id):
    """Insere o usuário na lista do evento com status confirmado (2)."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO lista (status, usuario_id, evento_id) VALUES (?, ?, ?);',
        (2, usuario_id, evento_id)
    )
    conn.commit()
    conn.close()

def get_participantes(evento_id):
    """Retorna lista de (id, nome, email) dos participantes confirmados (status=2)."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('''
        SELECT usuario.id, usuario.nome, usuario.email
        FROM usuario
        JOIN lista ON usuario.id = lista.usuario_id
        WHERE lista.evento_id = ? AND lista.status = 2
    ''', (evento_id,))
    resultado = cur.fetchall()
    conn.close()
    return resultado

def get_solicitacoes(evento_id):
    """Retorna lista de (id, nome, email) dos usuários com solicitação pendente (status=1)."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute('''
        SELECT usuario.id, usuario.nome, usuario.email
        FROM usuario
        JOIN lista ON usuario.id = lista.usuario_id
        WHERE lista.evento_id = ? AND lista.status = 1
    ''', (evento_id,))
    resultado = cur.fetchall()
    conn.close()
    return resultado

def get_status_usuario(evento_id, usuario_id):
    """Retorna o status do usuário no evento (1=pendente, 2=confirmado) ou None."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'SELECT status FROM lista WHERE usuario_id = ? AND evento_id = ?',
        (usuario_id, evento_id)
    )
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def solicitar_participacao(evento_id, usuario_id):
    """Cria uma solicitação de participação pendente (status=1)."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO lista (evento_id, usuario_id, status) VALUES (?, ?, 1);',
        (evento_id, usuario_id)
    )
    conn.commit()
    conn.close()

def aceitar_solicitacao(evento_id, usuario_id):
    """Aprova a solicitação do usuário, mudando status para confirmado (2)."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'UPDATE lista SET status = 2 WHERE evento_id = ? AND usuario_id = ?',
        (evento_id, usuario_id)
    )
    conn.commit()
    conn.close()

def recusar_solicitacao(evento_id, usuario_id):
    """Remove a solicitação do usuário do evento."""
    conn = c.get_db_conexao()
    cur = conn.cursor()
    cur.execute(
        'DELETE FROM lista WHERE evento_id = ? AND usuario_id = ?',
        (evento_id, usuario_id)
    )
    conn.commit()
    conn.close()