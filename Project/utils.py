'''
This file contains the utility functions for the project. Just for purpose of keeping the code clean.
'''

import os
import pandas as pd
import streamlit as st


def file_uploader() -> str | None:
    '''
    Function that creates file uploader wizard and processes 
    the file to save it to local file system            
'''
    with st.form("File Uploader Form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Upload file with loan data",
            type=["xlsx", "xls"]
        )
        submit_button = st.form_submit_button("Upload", use_container_width=True)

        if submit_button and uploaded_file is not None:
            upload_dir = "uploaded_files"
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.toast("File uploaded successfully", icon="✅")
            return file_path
        
        elif submit_button and uploaded_file is None:
            st.toast("Please upload a file before submitting", icon="❌")


def file_reader(file_path: str) -> pd.DataFrame:
    '''
        Function that reads the excel file and returns df
    '''
    assert file_path.endswith((".xlsx", ".xls")), "File must be excel"

    df = pd.read_excel(file_path)
    st.write("Preview of the uploaded file")
    st.dataframe(df)
    return df


def ui_handler():
    st.html('''
        <style>
            [data-testid="stApp"]{
                background-color: rgb(229 231 235);
                top: 0;
            }
            [data-testid="stHeader"] {
                background: rgba(0,0,0,0);
            }
        </style>
    ''')

    st.html('''
            <span style="color:skyblue; font-weight:bold; font-size:50px">
                Exaloan
            </span>
            <span style="color:gray; font-weight:bold; font-size:30px; font-style:italic">
                with
            </span>
            <span style="color:black; font-weight:bold; font-size:50px">
                Nimesh-
            </span>
            <span style="color:skyblue; font-weight:bold; font-size:50px">
                <u>Take Home Assignment</u>
            </span>

    ''')
