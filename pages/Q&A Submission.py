import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from st_files_connection import FilesConnection
from google.cloud import storage
import pandas as pd
from datetime import datetime
# function to download Q&A template
def get_qatemplate():
    # get table
    df = conn.read("card-ai-v61524/datathon/templates/Q&A Template.csv", input_format='csv')

    # add as session state variable
    st.session_state.qa_template = convert_df(df)

# function to get master files
def get_master_files(_input, _dict):
    # get table
    df = conn.read(_dict[_input], input_format='csv')

    return df.to_dict('records')

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def upload_file_gcs(client, file):
    """Uploads a file to the bucket."""
    
    bucket = client.bucket('card-ai-v61524')
    file_name = file.name
    file_type = file.type
    blob = bucket.blob(f'datathon/user_submitted/QA_uploads/{file_name}')


    # Upload the bytes directly instead of a disk file.
    blob.upload_from_string(file.getvalue(), file_type)

def upload_userfile_gcs(client,sub, df):
    """Uploads a file to the bucket."""
    # get time to add to file name
    now = datetime.now()
    # get date into string
    dt_string = now.strftime("%m%d%Y_%H:%M")
    bucket = client.bucket('card-ai-v61524')
    blob = bucket.blob(f'datathon/user_submitted/QA_uploads/{sub}_{dt_string}.csv')


    # Upload the bytes directly instead of a disk file.
    blob.upload_from_string(df.to_csv(), 'text/csv')

def get_contact(user_contact_method): 
    out = 'N/A'
    #get direct contact info based of preferred method selection
    if user_contact_method == 'NIH Email':
        st.text_input('NIH Email Address', key = 'nihemail')
        if st.session_state.nihemail:
            out = st.session_state.nihemail
    elif user_contact_method == 'Other':
        st.text_input('Please provide preferred method and direct contact information', help = 'Example: Personal email - coolemail@gmail.com', key = 'othercontact')
        if st.session_state.othercontact:
            out = st.session_state.othercontact
    elif user_contact_method == 'Slack' or user_contact_method == 'Basecamp':
        out = 'N/A'

    #set session state_var
    #st.session_state.contact1 = contact
    return out

# session state variables
# var to keep track of all submitted single question
if 'user_q_list' not in st.session_state:
    st.session_state.user_q_list = []

# var to keep track of all submitted single question
if 'user_qa_list' not in st.session_state:
    st.session_state.user_qa_list = []
    
# dictionary with file paths in bucket
master_dict = {'Question only': 'card-ai-v61524/datathon/user_submitted/QA_uploads/User_questions_master.csv',
              'Question and Answer': 'card-ai-v61524/datathon/user_submitted/QA_uploads/User_QA_master.csv'}

st.title('Q&A Submission')

creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = storage.Client(credentials = creds)

# establish connection to google cloud
conn = st.connection('gcs', type=FilesConnection)

# get template in session state var
get_qatemplate()

# load in mster files
#st.session_state.q_only_master_list = get_master_files('Question only', master_dict)
#st.session_state.qa_master_list = get_master_files('Question and Answer', master_dict)
#st.write(st.session_state.q_only_master_list)
with st.container():
# create two columns
    col1, col2 = st.columns(2)

    with col1:
        # provide user with template they can download
        st.header('Download Q&A template') 
        st.write('Template can be used to submit multiple questions at once')

        st.download_button('Download template', data = st.session_state.qa_template, file_name= "Q&A_template.csv", mime="text/csv")

    # location for user to submit their own file
    with col2:
        st.header('Submit Q&A file')
        st.write('Upload your Q&A csv/excel file for us to review. You can use the provided template or submit any csv file you like. Please ensure the file name has your name/username so we can reach out with any questions or any other follow up.')

        # accept file upload
        uploaded_file = st.file_uploader("Choose a file", type = ['csv', 'xlsx'])

        if uploaded_file is not None: # once user uploads file give them the option to upload into our bucket
                file_details = {"Name":uploaded_file.name,"Type":uploaded_file.type}
                st.button('Upload File', on_click = upload_file_gcs(client, uploaded_file))
with st.container():
    st.subheader('Submit Individual Question/Answer')

    # give user option to contribute only question
    q_only = st.toggle('Question only')

    # if user wants to submit only a question then upload master file and add their input
    if q_only:
        with st.container(border = True):
            # text input for question
            st.text_area('Type your question here', key = 'user_q1')

            # get a username or name
            st.text_input('Please provide your name so we can reach out if needed', key = 'user_name1')

            # get user prefered contact method
            st.radio('Preferred Contact Method', ['NIH Email', 'Slack', 'Basecamp', 'Other'], key = 'pref_contact1')
            
            # get direct contct info
            contact1 = get_contact(st.session_state.pref_contact1)

            # create row to add to master df
            new_row = {'Question': st.session_state.user_q1,
                       'Username': st.session_state.user_name1,
                       'Preferred Contact Method': st.session_state.pref_contact1,
                       'Contact': contact1,
                      'Submission Timestamp':''}
            # submit form button
            st.button('Submit Question', key = 'q_only_update')
            # if user has submitted a new question add it to existing df
            if st.session_state.q_only_update:
                # get time of submission
                now = datetime.now()
                # get date into string
                dt_string = now.strftime("%m-%d-%Y %H:%M")
                # add to row 
                new_row['Submission Timestamp'] = dt_string 
                st.session_state.user_q_list.append(new_row)
                
                #upload new df to bucket and then reupload
                #upload_masterfile_gcs(client, master_dict['Question only'].split('/')[-1], pd.DataFrame(st.session_state.q_only_master_list))

                if st.session_state.user_q_list:
                    with st.expander('Submitted Question Progress'):
                        # create df with submitted user feedback
                        user_q_df = pd.DataFrame(st.session_state.user_q_list)
                        st.session_state.userq_df = user_q_df
                        st.table(user_q_df)
                        # allow user to submit their responses to gcp
                        st.button('Upload submitted question(s)', help ='Submitted questions will consist of those shown in progress table', on_click = upload_userfile_gcs(client,'QOnly/SubmittedQuestions', user_q_df))

    q_and_a = st.toggle('Question and Answer')
    if q_and_a:
        with st.container(border = True):
           # text input for question
            st.text_area('Type your question here', key = 'user_q2')

            # text input for answer
            st.text_area('Type your answer here', key = 'user_a')

            # text input for refereneces
            st.text_area("Please provide link(s) to reference data used in formulating answer. E.g. PubMed ID/DOI/link to manuscript/citation", key = 'user_ref')

            # get a username or name
            st.text_input('Please provide your name so we can reach out if needed', key = 'user_name2')

            # get user prefered contact method
            st.radio('Preferred Contact Method', ['NIH Email', 'Slack', 'Basecamp', 'Other'], key = 'pref_contact2')
            
            # get direct contct info
            contact2 = get_contact(st.session_state.pref_contact2)

            # create row to add to master df
            new_row = {'Question': st.session_state.user_q2,
                       'Answer': st.session_state.user_a,
                       'References':st.session_state.user_ref,
                       'Username': st.session_state.user_name2,
                       'Preferred Contact Method': st.session_state.pref_contact2,
                       'Contact': contact2,
                      'Submission Timestamp':''}
            # submit form button
            st.button('Submit Question', key = 'qa_only_update')
            # if user has submitted a new question add it to existing df
            if st.session_state.qa_only_update:
                # get time of submission
                now = datetime.now()
                # get date into string
                dt_string = now.strftime("%m-%d-%Y %H:%M")
                # add to row 
                new_row['Submission Timestamp'] = dt_string 
                st.session_state.user_qa_list.append(new_row)

                if st.session_state.user_qa_list: # if we have some user submitted q&a data, display their progress in expander tab
                    with st.expander('Submitted Question and Answer Progress'):
                        # create df with submitted user feedback
                        user_qa_df = pd.DataFrame(st.session_state.user_qa_list)
                        st.session_state.userqa_df = user_qa_df
                        st.table(user_qa_df)
                        # allow user to submit their responses to gcp
                        st.button('Upload submitted question(s)', help ='Submitted questions will consist of those shown in progress table', on_click = upload_userfile_gcs(client, 'QAndA/SubmittedQuestionsAndAnswers', user_qa_df))
