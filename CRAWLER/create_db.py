import sqlite3

connection = sqlite3.connect('../crawl_db.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS InstagramPosts
              (id TEXT NOT NULL UNIQUE, text TEXT NOT NULL, hash_tag TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS InstagramPostsIDOnly
              (id TEXT NOT NULL UNIQUE, hash_tag TEXT NOT NULL)''')

connection.commit()
connection.close()