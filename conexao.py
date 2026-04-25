import sqlite3

def get_db_conexao():
    # aumenta timeout e permite uso em threads diferentes (útil para testes/servidor)
    conn = sqlite3.connect('database.db', timeout=30, check_same_thread=False)
    # usar WAL melhora concorrência de leitura/escrita no SQLite
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
    except Exception:
        pass
    return conn