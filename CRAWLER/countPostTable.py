import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def main():
    conn = create_connection("../crawl_db.db")
    cur = conn.cursor()

    # cur.execute('''CREATE TABLE IF NOT EXISTS Test
    #               (id TEXT NOT NULL UNIQUE, text TEXT NOT NULL, hash_tag TEXT NOT NULL)''')
    #
    # cur.execute("INSERT INTO Test (id, text, hash_tag) VALUES (?, ?, ?)",
    #           ('park', 'park@naver.com', '010-2222-3333'))
    #
    # conn.commit()
    # conn.close()

    # cur.execute("SELECT * FROM InstagramPosts")
    # cur.execute("SELECT COUNT(*) as cnt FROM InstagramPosts")

    cur.execute('''
    SELECT
        a.hash_tag
        , COUNT(*) as cnt 
    FROM InstagramPosts a
    GROUP BY a.hash_tag
    ''')

    rows = cur.fetchall()

    for row in rows:
        print(row)

if __name__ == '__main__':
    main()