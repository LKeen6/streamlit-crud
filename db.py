import psycopg2
import streamlit as st

def get_connection():
    # Credentials come from .streamlit/secrets.toml (git-ignored)
    creds = st.secrets["postgres"]
    return psycopg2.connect(
        host=creds["host"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"]
    )
