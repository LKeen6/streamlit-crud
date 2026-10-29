import hashlib
import secrets
from db import get_connection

SESSION_DAYS = 30

def _hash(token):
    # Only the hash is stored, so a leaked sessions table can't be used to log in
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash CHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_session(user_id):
    """Start a session for the user and return its token (goes in the browser cookie)."""
    token = secrets.token_urlsafe(32)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE expires_at < NOW()')
    cursor.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (%s, %s, NOW() + %s * INTERVAL '1 day')",
        (_hash(token), user_id, SESSION_DAYS)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return token

def get_user_id(token):
    """Return the user id for a valid, unexpired token, otherwise None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT user_id FROM sessions WHERE token_hash = %s AND expires_at > NOW()',
        (_hash(token),)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def delete_session(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE token_hash = %s', (_hash(token),))
    conn.commit()
    cursor.close()
    conn.close()
