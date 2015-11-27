__author__ = 'mossc'
import time
import psycopg2

conn = psycopg2.connect('dbname=forum')
cursor = conn.cursor()
cursor.execute('SELECT time, content FROM posts ORDER BY time DESC')

print(cursor.fetchall())
conn.close()
