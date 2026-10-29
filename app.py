import json
import streamlit as st
from api import users, posts, sessions

SESSION_COOKIE = 'session_token'

def set_session_cookie(token, max_age):
    # Streamlit can only read cookies (st.context.cookies), so set/clear it with a bit of JS
    st.sidebar.html(f"""
        <script>
            document.cookie = "{SESSION_COOKIE}=" + {json.dumps(token)} + "; path=/; max-age={max_age}; SameSite=Strict"
                + (location.protocol === "https:" ? "; Secure" : "");
        </script>
    """, unsafe_allow_javascript=True)

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
            st.session_state.session_token = sessions.create_session(user_id)
            st.rerun()  # rebuild the navbar so the logged-in pages show up
        else:
            st.error('Invalid username or password')

def dashboard_page():
    st.subheader('Dashboard')

    for user in users.list_users():
        st.write(f"ID: {user[0]}, Username: {user[1]}")

@st.cache_resource
def init_tables():
    posts.create_table()
    sessions.create_table()
    return True

@st.dialog('Create Post')
def create_post_dialog():
    title = st.text_input('Title')
    body = st.text_area('Body')

    if st.button('Create', type='primary'):
        if not title.strip() or not body.strip():
            st.error('Title and body are required')
        else:
            posts.create_post(title, body, st.session_state.user_id)
            st.rerun()  # closes the modal and refreshes the list

@st.dialog('Edit Post')
def edit_post_dialog(post_id, title, body):
    new_title = st.text_input('Title', value=title)
    new_body = st.text_area('Body', value=body)

    if st.button('Save', type='primary'):
        if not new_title.strip() or not new_body.strip():
            st.error('Title and body are required')
        elif posts.update_post(post_id, new_title, new_body, st.session_state.user_id):
            st.rerun()
        else:
            st.error('You can only edit your own posts')

def show_post(post):
    post_id, title, body, created_by, updated_by, created_at, updated_at, creator_id = post

    with st.expander(f"{title} — by {created_by or 'deleted user'}"):
        st.write(body)
        st.caption(f"Created by {created_by or 'deleted user'} at {created_at:%Y-%m-%d %H:%M %Z}")
        st.caption(f"Updated by {updated_by or 'deleted user'} at {updated_at:%Y-%m-%d %H:%M %Z}")

        # Only the owner gets Edit / Delete
        if creator_id != st.session_state.user_id:
            return

        edit_col, delete_col = st.columns(2)
        if edit_col.button('Edit', key=f'edit_post_{post_id}'):
            edit_post_dialog(post_id, title, body)
        if delete_col.button('Delete', key=f'delete_post_{post_id}'):
            posts.delete_post(post_id, st.session_state.user_id)
            st.rerun()

def my_posts_page():
    st.subheader('My Posts')

    if st.button('➕ Create Post'):
        create_post_dialog()

    my_posts = posts.list_posts(created_by=st.session_state.user_id)

    if not my_posts:
        st.info("You haven't written any posts yet.")

    for post in my_posts:
        show_post(post)

def all_posts_page():
    st.subheader('All Posts')
    all_posts = posts.list_posts()

    if not all_posts:
        st.info('No posts yet.')

    for post in all_posts:
        show_post(post)

st.title("Mini User Management App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "session_token" not in st.session_state:
    st.session_state.session_token = None

init_tables()

# A refresh starts a fresh session_state, so log back in from the session cookie if it's still valid
if not st.session_state.logged_in:
    cookie_token = st.context.cookies.get(SESSION_COOKIE)
    if cookie_token:
        user_id = sessions.get_user_id(cookie_token)
        if user_id is not None:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.session_token = cookie_token

# Need a user id too, otherwise My Posts can't tell whose posts to show
logged_in = st.session_state.logged_in and st.session_state.user_id is not None

if logged_in:
    pages = [
        st.Page(my_posts_page, title='My Posts', icon='✍️'),
        st.Page(all_posts_page, title='All Posts', icon='📰'),
        st.Page(dashboard_page, title='Dashboard', icon='📊'),
    ]
else:
    pages = [
        st.Page(login_page, title='Login', icon='🔑'),
        st.Page(register_page, title='Register', icon='📝'),
    ]

nav = st.navigation(pages, position='sidebar')

if logged_in and st.sidebar.button('Logout'):
    if st.session_state.session_token:
        sessions.delete_session(st.session_state.session_token)
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.session_token = None
    st.rerun()

# Keep the browser cookie in sync with the login state
if logged_in and st.session_state.session_token:
    set_session_cookie(st.session_state.session_token, sessions.SESSION_DAYS * 24 * 60 * 60)
elif not logged_in and st.context.cookies.get(SESSION_COOKIE):
    set_session_cookie('', 0)

nav.run()
