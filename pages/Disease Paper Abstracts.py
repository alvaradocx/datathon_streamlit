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

# function clear username
def clear_user():
    st.session_state['username'] = None

# function to reset row counter
def row_restart():
    # set session state to 0

    st.session_state.paper_i = 0

# function to add 1 row counter
def row_next():
    st.session_state.paper_i += 1

def row_back():
    st.session_state.paper_i -= 1

@st.cache_data
def convert_df_export(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def upload_df_gcs(client):
    """Uploads a dataframe to the bucket."""
    # prepare 
    create_fb_df()
    # get time to add to file name
    now = datetime.now()
    # get date into string
    dt_string = now.strftime("%m%d%Y_%H:%M")
    bucket = client.bucket('card-ai-v61524')
    blob = bucket.blob(f'datathon/user_submitted/paper_feedback/userPaperFeedBack_{dt_string}.csv')

    # Upload the bytes directly instead of a disk file.
    blob.upload_from_string(st.session_state.fb_df, 'text/csv')

# function to update data session state vars
def update_data_vars(current):
    st.session_state.title = current['title']
    st.session_state.abs = current['abstract']
    st.session_state.doi = current['DOI']
    st.session_state.cid = current['corpusId']

    # check if we have a PMID
    if np.isnan(current['PubMed (PMID)']):
        st.session_state.pmid = "None"
    else:
        st.session_state.pmid = int(current['PubMed (PMID)'])
# function to update feedback list
def update_fblist(row):
    st.session_state.feedback_list.append(row)

# function to download fb df
def create_fb_df():
    # create df
    df = pd.DataFrame(st.session_state.feedback_list)

    # remove duplicates
    #df.drop_duplicates(inplace = True)

    # convert df for download
    final = convert_df_export(df)

    st.session_state.fb_df = final
    
# session state variable for Title and Abstract text
if 'paper_i' not in st.session_state:
    st.session_state.paper_i = 0
if 'title' not in st.session_state:
    st.session_state.title = None

if 'abs' not in st.session_state:
    st.session_state.abs = None
    
if 'doi' not in st.session_state:
    st.session_state.doi = None

if 'pmid' not in st.session_state:
    st.session_state.pmid = None
    
if 'cid' not in st.session_state:
    st.session_state.cid = None
    
if 'dx_name_last' not in st.session_state: # var to hold last selected dx 
    st.session_state.dx_name_last = None
    
if 'dx_name' not in st.session_state: # var to hold newest selected dx 
    st.session_state.dx_name = None   

if 'dx_df' not in st.session_state: # var to hold diseases papers df
    st.session_state.dx_df = None   

if 'feedback_list' not in st.session_state: # var to hold feedback from each individual paper
    st.session_state.feedback_list = []  

if 'fb_df' not in st.session_state: # var to hold feedback dataframe
    st.session_state.fb_df = None 
    
# Establish API clients
google_credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
st.session_state.google_client_auth = google_credentials

# gcs bucket client
client = storage.Client(credentials = google_credentials)
# establish connection to google cloud
conn = st.connection('gcs', type=FilesConnection)

with st.sidebar: # get username
    username = st.text_input('**Name/Assigned Username**', key='username')
    st.write(f'Current user: {st.session_state.username}')
    st.button('Clear current user', on_click=clear_user)
    
st.title('Paper Abstracts')
with st.expander('Background Information'):
    st.markdown('On this page you can use provided diseases specific paper abstracts to help you create questions. Below, you may select a specific disease and receive abstracts and additional information to help you in your Q&A creating journey.')
    st.markdown('\n Metadata such DOI and PubMed ID can be used to locate the full manuscript if you need more context. Use the **next** and **back** buttons to move between abstracts and the **restart** button to restart from the very first abstract.')
    st.write("Please use our feedback form to log any feedback regarding paper abstracts, language, additional metadata you think would be helpful.")

# get user to select disease so we can pull up the data
st.selectbox("Disease", ("AD","ALS","FTD", "LBD", "PSP", "PD"), key = 'dx_name')

# dictionary to access files from google
table_dict = {"AD":"card-ai-v61524/datathon/initial_data/AD_abstracts.csv",
             "PD": "card-ai-v61524/datathon/initial_data/PD_abstracts.csv",
             "PSP":"card-ai-v61524/datathon/initial_data/PSP_abstracts.csv",
             "ALS":"card-ai-v61524/datathon/initial_data/ALS_abstracts.csv",
             "FTD":"card-ai-v61524/datathon/initial_data/FTD_abstracts.csv",
             "LBD":"card-ai-v61524/datathon/initial_data/LBD_abstracts.csv"}

# if user has made initial selection
if st.session_state.dx_name:
    st.write(f'Selected disease: {st.session_state.dx_name}')
    # get table
    df = conn.read(table_dict[st.session_state.dx_name], input_format='csv')
    
    # session state var for disease variable
    st.session_state.dx_df = df

    with st.container():
        #if not isinstance(st.session_state.dx_df, type(None)):
        if st.session_state.dx_name != st.session_state.dx_name_last:  # activated when we change to a new dx_df
            st.session_state.paper_i = 0
            st.write(f'New disease selected: {st.session_state.dx_name} from {st.session_state.dx_name_last}')
    
            # update session state var
            st.session_state.dx_name_last = st.session_state.dx_name
            
        # start dispalying data
        if st.session_state.paper_i <= st.session_state.dx_df.shape[0]:
            # get current row
            st.session_state.current = st.session_state.dx_df.iloc[st.session_state.paper_i,:]
            
            # update title and abstract vars
            update_data_vars(st.session_state.current)
    
            st.markdown(f"""#### Title: \n{st.session_state.title}""")
            st.markdown(f"""#### Abstract: \n{st.session_state.abs}""")
            st.markdown(f"""#### Additional paper data: \n""")
            st.markdown(f"""#### DOI: \n{st.session_state.doi}""")
            st.markdown(f"""#### PubMed ID: \n{st.session_state.pmid}""")
    
            st.button('Next Paper', on_click=row_next)
            st.button('Previous Paper', on_click=row_back)

            # offer restart button if paper_i > 0
            if st.session_state.paper_i > 0:
                st.button('Restart', on_click=row_restart)
        elif st.session_state.paper_i == st.session_state.dx_df.shape[0]:
            # get current row
            st.session_state.current = st.session_state.dx_df.iloc[st.session_state.paper_i,:]
            
            # update title and abstract vars
            update_data_vars(st.session_state.current)
    
            st.markdown(f"""#### Title: \n{st.session_state.title}""")
            st.markdown(f"""#### Abstract: \n{st.session_state.abs}""")
            st.markdown(f"""#### Additional paper data: \n""")
            st.markdown(f"""#### DOI: \n{st.session_state.doi}""")
            st.markdown(f"""#### PubMed ID: \n{st.session_state.pmid}""")
    
            st.button('Previous Paper', on_click=row_back)
            st.button('Restart', on_click=row_restart)
        else:
            st.write('An error has occured')
    
    #with st.expander("Data Feedback", expanded = True):
    with st.container():
        st.subheader('Data Feedback')
        # dictionary to serve as row in feedback df
        feedback_row = {'CorpusId': st.session_state.cid, 'Title': st.session_state.title, 'Language':'', 'Categories':'', "Notes": '','Username': st.session_state.username}
    
    
        # Abstract Language
        p_lang = st.selectbox('What language is abstract in?', ('English', 'Spanish', 'French', 'German', 'Russian', 'Other'))
        # if user selects other give them option to type in
        if p_lang == 'Other':
            # give text box for user to type in
            other_lang = st.text_input('Other Language - if known')
        
            # If user provides, update value in row dictionary
            if other_lang:
                    feedback_row['Language'] =  other_lang
            else:
                # if user doesn't know or doesn't provide value just keep value as "Other"
                feedback_row['Language'] =  p_lang
        else:
            feedback_row['Language'] =  p_lang
        
        # Abstract classification
        p_class = st.multiselect('What category/categories would you place this paper under?', ['Genomics', 'Transcriptomics', 'Single Cell', 'Healthcare/Social Support', 'Unrelated', 'Other'])
        # if user selects other give them option to type in
        
        if 'Other' in p_class:
            other_cat = st.text_input('Other categories seperated by comma')
            # format input
            if other_cat:
                # convert string into list
                other_list = other_cat.replace(" ", "").split(",")
        
                # append to existing selections
                p_class = list(set(p_class + other_list))
        
                # drop "Other"
                p_class.remove('Other')
        
                # add to row
                feedback_row['Categories'] = p_class
        else: # otherwise append to row
            feedback_row['Categories'] = p_class
            
    
        # give user section to provide notes
        p_notes = st.text_area('Please provide an additional feedback here')
        feedback_row['Notes'] = p_notes
        
        # button to update feedback
        st.button('Save feedback for this paper', on_click = update_fblist(feedback_row))
        
        # Download feedback provided up to this point
        st.button('Prepare copy of my feedback', on_click = create_fb_df, key = 'fb_df_prep')
        
        
        if st.session_state.fb_df_prep:
            # allow user to see their up to date feedback
            # show_fb = st.toggle('View progress')
            # if show_fb:
            #     st.table(pd.DataFrame(st.session_state.feedback_list))
            st.download_button('Download my feedback', data = st.session_state.fb_df, file_name = 'copyAbstractFeedback.csv', mime = 'text/csv')
        
        # button to submit all feedback into gcs bucket
        st.button('Upload all feedback', on_click = upload_df_gcs(client))
