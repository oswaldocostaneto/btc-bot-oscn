import sqlite3

def db_connect():
    conn = sqlite3.connect('btc-bot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transaction_hashes (
            hash TEXT PRIMARY KEY
        )
    ''')
    conn.commit()

    return conn, c