import streamlit as st
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="dpg-dbh875kipgvc73d5ef0g-a.oregon-postgres.render.com",
        database="newdb_tvcp",
        user="newdb_tvcp_user",
        password="Uk35jpYFYtGinDJNctZwHLcVxNh7mzFC"
    )

st.title("Mini User Management App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ['Login', 'Register']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'Register':
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Register'):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username,  password) VALUES (%s, %s)',
            (username, password)   
        )
        conn.commit()
        cursor.close()
        conn.close()
        st.success('User Registered!')

elif choice == 'Login':
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s',
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.success('Loggin Successful!')

if st.session_state.logged_in:
    st.subheader('Dashboard')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    for user in users:
        st.write(f"ID: {user[0]}, Username: {user[1]}")


