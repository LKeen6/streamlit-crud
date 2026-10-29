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

def list_posts(created_by=None):
    """Newest first: (id, title, body, created_by, updated_by, created_at, updated_at, creator_id),
    usernames for the by-columns. Pass created_by (a user id) to only get that user's posts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.title, p.body, creator.username, updater.username, p.created_at, p.updated_at, p.created_by
        FROM posts p
        LEFT JOIN users creator ON creator.id = p.created_by
        LEFT JOIN users updater ON updater.id = p.updated_by
        WHERE %(created_by)s IS NULL OR p.created_by = %(created_by)s
        ORDER BY p.created_at DESC
    """, {'created_by': created_by})
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return posts

def update_post(post_id, title, body, user_id):
    """Only the post's owner can update it. Returns True if a post was updated."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE posts SET title = %s, body = %s, updated_by = %s, updated_at = NOW() WHERE id = %s AND created_by = %s',
        (title, body, user_id, post_id, user_id)
    )
    updated = cursor.rowcount == 1
    conn.commit()
    cursor.close()
    conn.close()
    return updated

def delete_post(post_id, user_id):
    """Only the post's owner can delete it. Returns True if a post was deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s AND created_by = %s', (post_id, user_id))
    deleted = cursor.rowcount == 1
    conn.commit()
    cursor.close()
    conn.close()
    return deleted
