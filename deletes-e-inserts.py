import sqlite3

conexao = sqlite3.connect('database.db')
cursor = conexao.cursor()
sql_delete_query = 'DELETE FROM evento WHERE id = 5;'
cursor.execute(sql_delete_query)
conexao.commit()
conexao.close()