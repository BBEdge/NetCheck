import sqlite3


def init_db():
    global dbconn
    ''' init database and connection '''
    DATABASE = 'test.db'

    try:
        dbconn = sqlite3.connect(DATABASE)
        #dbconn.row_factory = sqlite3.Row
        #DATABASE = ":memory:"
        #dbconn = sqlite3.connect(DATABASE)

        with open('static/sql/schema.sql') as f:
            dbconn.executescript(f.read())

    except sqlite3.Error as error:
        print("ERROR: ", str(error))

    return dbconn

if __name__ == '__main__':
    conn = init_db()
    conn.close()
