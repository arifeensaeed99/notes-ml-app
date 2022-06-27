import sqlite3
conn = sqlite3.connect("usersdata.db")
c = conn.cursor()

# Database
# c.execute('DROP TABLE users_table')
    
# Table
def create_users_table():
    c.execute('CREATE TABLE IF NOT EXISTS users_table(username TEXT UNIQUE, password TEXT)') # not null

def add_users_data(username, password):
    c.execute('INSERT INTO users_table(username, password) VALUES (?,?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users_table WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT * FROM users_table')
    data = c.fetchall()
    return data
