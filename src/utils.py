import streamlit as st

USERNAME = "ClientX"
PASSWORD = "stratbomb"

def authenticate(username, password):
    """Authenticates a user."""
    return username == USERNAME and password == PASSWORD

def load_logo(logo_path, width=250):
    """Loads a logo for the app."""
    st.image(logo_path, width=width)
