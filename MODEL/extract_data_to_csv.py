from __future__ import print_function
import pandas as pd
import sqlite3

def main():
    try:
        conn = sqlite3.connect("../crawl_db.db")
        cur = conn.cursor()

        query = cur.execute('''
            SELECT
                a.*
            FROM InstagramPosts a
            ''')

        cols = [column[0] for column in query.description]

        result_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)

        conn.close()

        print(result_df)

        result_df.to_csv("../instagram_data.csv", index=None)

    except Exception as e:
        print(e)

    # temp_df = pd.read_csv("../instagram_data.csv")
    # print(temp_df)

if __name__ == "__main__":
    main()