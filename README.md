# Mini User Management App

A small Streamlit app backed by PostgreSQL. Users can register, log in, and create, edit and delete their own posts.

## Features

### Accounts
- **Register**: create an account with a username and password. Passwords are hashed with bcrypt before they're stored.
- **Login**: log in with your username and password.
- **Staying logged in**: logging in starts a session that lasts 30 days. The session token is kept in a browser cookie (`session_token`), so refreshing the page doesn't log you out. The database stores only a SHA-256 hash of the token.
- **Logout**: the sidebar's Logout button deletes the session from the database and clears the cookie.

### Pages
Before you log in, the sidebar shows **Login** and **Register**. After you log in, it shows these pages:

| Page | What it does |
|------|--------------|
| ✍️ **My Posts** | Lists your posts, newest first. **➕ Create Post** opens a dialog for a title and body. Each post has **Edit** and **Delete** buttons. |
| 📰 **All Posts** | Lists every user's posts, newest first. Edit and Delete appear only on posts you wrote. |
| 📊 **Dashboard** | Shows your user info (ID and username) in a read-only table, and your 5 latest posts with an **Edit** button on each. |

Each post shows who created it, who last updated it, and when. If a user is deleted, their posts stay and show "deleted user" as the author.

### Ownership rules
The database queries enforce ownership as well as the UI: the update and delete queries include `created_by = <your id>`, so you can only change or remove your own posts.

## Project layout

```
app.py            # Streamlit UI: pages, dialogs, navigation, login/session handling
db.py             # PostgreSQL connection (reads .streamlit/secrets.toml)
api/
  users.py        # register, authenticate, get/list users
  posts.py        # posts table + create/list/update/delete
  sessions.py     # sessions table + create/validate/delete session tokens
```

## Setup

### Requirements
- Python 3
- A PostgreSQL database

Install the dependencies:

```bash
pip install streamlit psycopg2-binary bcrypt
```

### Database
When the app starts, it creates the `posts` and `sessions` tables if they don't exist. It does **not** create the `users` table, so create that one yourself first, for example:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL  -- bcrypt hash
);
```

### Credentials
Create `.streamlit/secrets.toml` (git ignores it):

```toml
[postgres]
host = "localhost"
database = "your_database"
user = "your_user"
password = "your_password"
```

### Run

```bash
streamlit run app.py
```
