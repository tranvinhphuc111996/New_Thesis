import sqlite3


DATABASE_FILE = 'database.db'

conn = sqlite3.connect(DATABASE_FILE, isolation_level = None)


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Work")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)


select_all_tasks(conn)

a = 111
b = 222
v = (a,b).tuple()

print("haha")
print(v)



 
