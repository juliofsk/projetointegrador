import sqlite3

conexao = sqlite3.connect('database.db')
cursor = conexao.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_administrador INTEGER NOT NULL,
	nome TEXT NOT NULL,
	local TEXT NOT NULL,
	data NUMERIC NOT NULL,
	hora NUMERIC NOT NULL,
	limite INTEGER NOT NULL,
	pago INTEGER DEFAULT 1,
	link_pagamento TEXT,
	FOREIGN KEY (id_administrador) REFERENCES usuario (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	nome TEXT NOT NULL,
	email TEXT,
	senha NUMERIC DEFAULT 1,
    foto TEXT 
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS lista (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	comprovante TEXT,
	status INTEGER,
    usuario_id INTEGER,
    evento_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuario (id),
    FOREIGN KEY (evento_id) REFERENCES evento (id)
)
''')

conexao.commit()
cursor.close()
conexao.close()