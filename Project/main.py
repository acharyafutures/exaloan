'''
This is the landing page for the loan anomaly detection project.
Every content are called from this file.
'''


import time
import streamlit as st
from utils import file_uploader, file_reader, ui_handler
from session_state import init_session_state
from detect_anomaly import detect_loan_anomalies
from detect_anomaly_vector import detect_loan_anomalies_vectorized

st.set_page_config(page_title="Loan Anomaly", layout="wide")
ui_handler()
init_session_state()


with st.expander("Expand to upload file and detect loan anomaly"):
    
    file_path = file_uploader()

    if file_path:
        st.session_state.file_path = file_path
    dict_val = None

    if st.session_state.file_path is not None:
        df = file_reader(st.session_state.file_path)
        
        if df is not None and not df.empty:
            st.session_state.df = df
        else:
            st.toast("File is empty", icon="❌")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Detect anomaly", 
                use_container_width=True, 
                disabled=st.session_state.df is None or st.session_state.df.empty
            ):
                start_time = time.time()
                dict_val = detect_loan_anomalies(st.session_state.df)
                end_time = time.time()

                st.write(f"Time taken: {end_time - start_time} seconds")
                dict_val = {k: ", ".join(v) if v else "Normal" for k, v in dict_val.items() }
                st.dataframe(dict_val, use_container_width=True)
        
        with col2:
            if st.button(
                "Detect anomaly vectorized", 
                use_container_width=True, 
                disabled=st.session_state.df is None or st.session_state.df.empty
            ):
                start_time = time.time()
                dict_val = detect_loan_anomalies_vectorized(st.session_state.df)
                end_time = time.time()

                st.write(f"Time taken: {end_time - start_time} seconds")
                dict_val = {k: ", ".join(v) if v else "Normal" for k, v in dict_val.items() }
                st.dataframe(dict_val, use_container_width=True)

