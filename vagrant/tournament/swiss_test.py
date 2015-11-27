__author__ = 'mossc'
import psycopg2

conn = psycopg2.connect("dbname=tournament")
cursor = conn.cursor()
cursor.execute("DROP VIEW prime;")
cursor.execute("CREATE VIEW prime AS SELECT count(matches.winner) as matches, players.id, players.name from matches right join players on players.id = matches.winner or players.id = matches.loser group by players.id;")
cursor.execute("SELECT prime.id, prime. name, count(matches.winner) as wins, prime.matches FROM matches RIGHT JOIN prime ON prime.id = matches.winner group by prime.id, prime.matches, prime.name ORDER BY wins DESC;")

count = 0
temp_list = []
pairings = []

for row in cursor.fetchall():
    temp_list.append(str(row[0]))
    temp_list.append(str(row[1]))
    count += 1
    if count > 1 and count%2==0:
        pairings.append(temp_list)
        temp_list = []

conn.commit()
conn.close()
print pairings