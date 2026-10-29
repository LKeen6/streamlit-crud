import bcrypt
from db import get_connection

def create_user(username, password):
    # bcrypt = Blowfish-based password hash, salted automatically
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (username,  password) VALUES (%s, %s)',
        (username, hashed)
    )
    conn.commit()
    cursor.close()
    conn.close()

def authenticate(username, password):
    """Return the user's id if the username/password are valid, otherwise None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, password FROM users WHERE username = %s',
        (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        return user[0]
    return None

def get_user(user_id):
    """Return (id, username) for the user, or None if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users
