import sqlite3
import json

DATABASE_FILE = 'database.db'

conn = sqlite3.connect(DATABASE_FILE, isolation_level = None)
conn.row_factory = sqlite3.Row



def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Work")
    rows = cur.fetchall() 
    rows = [ dict(rec) for rec in rows ]
    rows_json = json.dumps(rows)
    print(rows_json)


select_all_tasks(conn)



 
