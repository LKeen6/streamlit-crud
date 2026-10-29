import streamlit as st
from api import users, posts

def register_page():
    st.subheader('Register')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Register'):
        users.create_user(username, password)
        st.success('User Registered!')

def login_page():
    st.subheader('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        user_id = users.authenticate(username, password)

        if user_id is not None:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.rerun()  # rebuild the navbar so the Dashboard page shows up
        else:
            st.error('Invalid username or password')

def dashboard_page():
    st.subheader('Dashboard')

    for user in users.list_users():
        st.write(f"ID: {user[0]}, Username: {user[1]}")

    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

@st.cache_resource
def init_posts_table():
    posts.create_table()
    return True

def posts_page():
    st.subheader('Posts')
    user_id = st.session_state.user_id

    # Create
    with st.form('new_post', clear_on_submit=True):
        title = st.text_input('Title')
        body = st.text_area('Body')

        if st.form_submit_button('Create Post'):
            if not title.strip() or not body.strip():
                st.error('Title and body are required')
            else:
                posts.create_post(title, body, user_id)
                st.success('Post created!')

    # Read
    all_posts = posts.list_posts()

    if not all_posts:
        st.info('No posts yet.')

    for post_id, title, body, created_by, updated_by, created_at, updated_at in all_posts:
        with st.expander(title):
            st.write(body)
            st.caption(f"Created by {created_by or 'deleted user'} at {created_at:%Y-%m-%d %H:%M %Z}")
            st.caption(f"Updated by {updated_by or 'deleted user'} at {updated_at:%Y-%m-%d %H:%M %Z}")

            # Update
            with st.form(f'edit_post_{post_id}'):
                new_title = st.text_input('Title', value=title)
                new_body = st.text_area('Body', value=body)

                if st.form_submit_button('Update'):
                    if not new_title.strip() or not new_body.strip():
                        st.error('Title and body are required')
                    else:
                        posts.update_post(post_id, new_title, new_body, user_id)
                        st.rerun()

            # Delete
            if st.button('Delete', key=f'delete_post_{post_id}'):
                posts.delete_post(post_id)
                st.rerun()

st.title("Mini User Management App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

init_posts_table()

if st.session_state.logged_in:
    pages = [
        st.Page(posts_page, title='Posts', icon='📰'),
        st.Page(dashboard_page, title='Dashboard', icon='📊'),
    ]
else:
    pages = [
        st.Page(login_page, title='Login', icon='🔑'),
        st.Page(register_page, title='Register', icon='📝'),
    ]

nav = st.navigation(pages, position='sidebar')
nav.run()
