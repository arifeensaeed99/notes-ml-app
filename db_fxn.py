import sqlite3
conn = sqlite3.connect("data.db")
c = conn.cursor()

# Database

# c.execute('DROP TABLE note_table')

# Table
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS note_table(username TEXT, note TEXT, is_task BOOL, note_status TEXT, note_due_date DATE, pred_category TEXT, CONSTRAINT user_note_pk PRIMARY KEY (username, note))')

def add_data(username, note, is_task, note_status, note_due_date, pred_category):
    c.execute('INSERT INTO note_table(username, note, is_task, note_status, note_due_date, pred_category) VALUES (?,?,?,?,?,?)', (username, note, is_task, note_status, note_due_date, pred_category))
    conn.commit()

def view_all_data(username):
    c.execute('SELECT note, is_task, note_status, note_due_date, pred_category FROM note_table WHERE username = "{}"'.format(username))
    data = c.fetchall()
    return data

def view_unique_data(username):
    c.execute('SELECT DISTINCT note FROM note_table WHERE username = ?', (username,))
    data = c.fetchall()
    return data

def view_all_category(username):
    c.execute('SELECT DISTINCT pred_category FROM note_table WHERE username = ?', (username,))
    data = c.fetchall()
    return data

def view_all_statuses(username):
    c.execute('SELECT DISTINCT note_status FROM note_table WHERE username = ? AND is_task = True', (username,))
    data = c.fetchall()
    return data

def get_category_notes(pred_category, username):
    c.execute('SELECT note, is_task, note_status, note_due_date, pred_category FROM note_table WHERE pred_category  = "{}" AND username = "{}"'.format(pred_category, username))
    data = c.fetchall()
    return data

def get_status_task_notes(note_status, username):
    c.execute('SELECT note, is_task, note_status, note_due_date, pred_category FROM note_table WHERE note_status  = "{}" AND username = "{}"'.format(note_status, username))
    data = c.fetchall()
    return data

def get_note(note, username):
    c.execute('SELECT note, is_task, note_status, note_due_date, pred_category FROM note_table WHERE note = ? AND username = ?', (note, username, ))
    data = c.fetchall()
    return data

def update_note_data(username, new_note, new_is_task, new_note_status, new_note_due_date, new_pred_category, note, is_task, note_status, note_due_date, pred_category):
    c.execute('UPDATE note_table SET username = ?, note = ?, is_task = ?, note_status = ?, note_due_date = ?, pred_category = ? WHERE username = ? and note = ? and is_task = ? and note_status = ? and note_due_date = ? and pred_category = ?', (username, new_note, new_is_task, new_note_status, new_note_due_date, new_pred_category, username, note, is_task, note_status, note_due_date, pred_category))
    conn.commit()
    data = c.fetchall()
    return data

def delete_note(note, username):
    c.execute('DELETE FROM note_table WHERE note = ? AND username = ?', (note, username, ))

    conn.commit()