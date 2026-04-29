import sqlite3

conexao = sqlite3.connect('database.db')
cursor = conexao.cursor()


sql_delete_column_query = '''
ALTER TABLE lista
DROP COLUMN comprovante;
'''
cursor.execute(sql_delete_column_query)
conexao.commit()
conexao.close()

