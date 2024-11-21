import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
from src.utils import authenticate, load_logo

# Path to assets
LOGO_PATH = Campaign-Prioritizer_Logo.png

# Streamlit app
def main():

    # User session for login state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    if not st.session_state.logged_in:
        st.image(LOGO_PATH,width=225)
        st.title("Login to Prioritizer App")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password.")
    else:
        st.image(LOGO_PATH, width=225)
        st.title("Prioritizer Tool")
        st.write("Optimize precincts for your campaign.")
        # Remaining app logic remains similar
        # ...
        
if __name__ == "__main__":
    main()
