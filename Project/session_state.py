'''
This file contains the logic for initializing the session state.
'''

import streamlit as st


def init_session_state():
    if "df" not in st.session_state:
        st.session_state.df = None

    if "file_path" not in st.session_state:
        st.session_state.file_path = None

