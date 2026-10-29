from db import get_connection

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            body TEXT NOT NULL,
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_post(title, body, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO posts (title, body, created_by, updated_by) VALUES (%s, %s, %s, %s)',
        (title, body, user_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def list_posts():
    """Newest first: (id, title, body, created_by, updated_by, created_at, updated_at), usernames for the by-columns."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.title, p.body, creator.username, updater.username, p.created_at, p.updated_at
        FROM posts p
        LEFT JOIN users creator ON creator.id = p.created_by
        LEFT JOIN users updater ON updater.id = p.updated_by
        ORDER BY p.created_at DESC
    """)
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return posts

def update_post(post_id, title, body, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE posts SET title = %s, body = %s, updated_by = %s, updated_at = NOW() WHERE id = %s',
        (title, body, user_id, post_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_post(post_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
    conn.commit()
    cursor.close()
    conn.close()
