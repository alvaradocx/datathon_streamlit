import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from st_files_connection import FilesConnection
import pandas as pd
from google.cloud import storage
import numpy as np
from datetime import datetime
import random

# function clear username
def clear_user():
    st.session_state['username'] = None

@st.cache_data
def convert_df_export(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

# function that stores contents of users current question and answer pair
def update_userqa():
    # update session state var holding question
    st.session_state.currentqa_user['Question'] = st.session_state.currentqa

    # update session state var holding question
    st.session_state.currentqa_user['Answer'] = st.session_state.currentqa_answer

# function that saves users completed Q&A input
def save_qa(row):
    # append user input to submitted list
    st.session_state.completed_qa.append(row)
# function to upload user input into bucket
def upload_qadf_gcs(client):
    """Uploads a dataframe to the bucket."""
    # get time to add to file name
    now = datetime.now()
    # get date into string
    dt_string = now.strftime("%m%d%Y_%H:%M")
    bucket = client.bucket('card-ai-v61524')
    blob = bucket.blob(f'datathon/user_submitted/unanswered_questions/userUnansweredQA_{dt_string}.csv')

    # Upload the bytes directly instead of a disk file.
    blob.upload_from_string(st.session_state.userqa_df.to_csv(), 'text/csv')

# function to randomly select a question from list
def rand_q():
    st.session_state.currentqa = random.choice(st.session_state.uaqa)
    
# session state variables
# var to save current selected question
if 'currentqa' not in st.session_state:
    st.session_state.currentqa = None
    
# var to save user current work in a dictionary
if 'currentqa_user' not in st.session_state:
    st.session_state.currentqa_user = {'Question':'', 'Answer':''}

# var to save users submitted work
if 'completed_qa' not in st.session_state:
    st.session_state.completed_qa = []

# Establish API clients
google_credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
st.session_state.google_client_auth = google_credentials

# gcs bucket client
client = storage.Client(credentials = google_credentials)

# establish connection to google cloud
conn = st.connection('gcs', type=FilesConnection)

# preload main papers dataframe
# get table
df = conn.read("card-ai-v61524/datathon/initial_data/Unanswered_Questions.csv", input_format='csv')

# session state var for unanswered questions list from loaded file
st.session_state.uaqa = df.iloc[:,0]

st.title("Unanswered Questions Bank")
st.markdown("Just want to answer questions that have already been asked? Use our tools below to pull existing unanswered questions and provide your expert answers.")

# create a two containers/columns one container will generate a random unanswered question and the second will allow the user to browse a list of questions

with st.container():
    # create two columns
    col1, col2 = st.columns(2)
    with col1: # allow user to browse questions and select
        st.subheader('Select Question')
        st.selectbox("Select a question", st.session_state.uaqa, key = 'currentqa', index=None)
        
    with col2: # generate random question
        st.subheader('Random Question')
        st.button('Give me a random question', on_click = rand_q)

    st.markdown(f'''<u>**Selected question:**</u>
    \n{st.session_state.currentqa}''', unsafe_allow_html = True)

    # if user has selected a question allow input box to show up
    if st.session_state.currentqa:
        qa_row = {'Question' : st.session_state.currentqa, 'Answer':'', 'References':''}
        # input box for users answer
        st.text_area("Insert your answer", key = 'currentqa_answer')

        # input box for any references
        st.text_area("Please provide link(s) to reference data used in formulating answer. E.g. PubMed ID/DOI/link to manuscript/citation", key = 'currentqa_ref')
    
        # allow user to submit and add to list holding user responses for output dataframe
        st.button('Save Question and Answer', key = 'saveqa')
        if st.session_state.saveqa:
            # add user answer to row
            qa_row['Answer'] = st.session_state.currentqa_answer
            # add user answer to row
            qa_row['References'] = st.session_state.currentqa_ref
            # add user input to list
            save_qa(qa_row)
# add expander that shows user progress is there is at least one submitted Q&A response
if st.session_state.completed_qa:
    with st.expander('Q&A Progress'):
        # create df with submitted user feedback
        user_df = pd.DataFrame(st.session_state.completed_qa)
        st.session_state.userqa_df = user_df
        st.table(user_df)
    
    # allow user to submit their responses to gcp
    st.button('Upload Q&A Responses', on_click = upload_qadf_gcs(client))