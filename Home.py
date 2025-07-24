import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from st_files_connection import FilesConnection
from google.cloud import storage

# # function clear username
# def clear_user():
#     st.session_state['username'] = None

# # function to proceed to next row in df/next paper
# def next_paper(df, next = False):

#     # increase row counter
#     row_next()

#     row = st.session_state.paper_i

#     # update current row
#     st.session_state.current = df.iloc[row,:]

# # function to reset row counter
# def row_restart():
#     # set session state to 0

#     st.session_state.paper_i = 0

# # function to add 1 row counter
# def row_next():
#     # increase row counter
#     st.session_state.paper_i += 1


# # function to update data session state vars
# def update_data_vars(current):
#     st.session_state.title = current['title']
#     st.session_state.abs = current['abstract']
#     st.session_state.doi = current['DOI']
#     st.session_state.pmid = current['PubMed (PMID)']

# # session state variable for Title and Abstract text
# if 'paper_i' not in st.session_state:
#     st.session_state.paper_i = 0
# if 'title' not in st.session_state:
#     st.session_state.title = None

# if 'abs' not in st.session_state:
#     st.session_state.abs = None
    
# if 'doi' not in st.session_state:
#     st.session_state.doi = None

# if 'pmid' not in st.session_state:
#     st.session_state.pmid = None
    
# if 'dx_name_last' not in st.session_state: # var to hold last selected dx 
#     st.session_state.dx_name_last = None
    
# if 'dx_name' not in st.session_state: # var to hold newest selected dx 
#     st.session_state.dx_name = None    
    
# Establish API clients
google_credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
st.session_state.google_client_auth = google_credentials
st.session_state.google_storage_client = storage.Client(credentials = st.session_state.google_client_auth)
# establish connection to google cloud
#conn = st.connection('gcs', type=FilesConnection)

st.title('CARD.AI Hackathon')
st.header('Welcome!')
st.write('Thank you for taking your time to help us create questions & answers related to AD and other neurodegenerative diseases.')

# with st.sidebar: # get username
#     username = st.text_input('**Name/Assigned Username**', key='username')
#     st.write(f'Current user: {st.session_state.username}')
#     st.button('Clear current user', on_click=clear_user)

#     # get user to select disease so we can pull up the data
#     st.selectbox("Below, you may select a specific disease and receive abstracts and additional information to help you in your Q&A creating journey.", ("AD","ALS","FTD", "LBD", "PSP", "PD"), key = 'dx_name')
#     st.write(f'Selected disease: {st.session_state.dx_name}')

# # dictionary to access files from google
# table_dict = {"AD":"card-ai-v61524/datathon/initial_data/AD_abstracts.csv",
#              "PD": "card-ai-v61524/datathon/initial_data/PD_abstracts.csv",
#              "PSP":"card-ai-v61524/datathon/initial_data/PSP_abstracts.csv",
#              "ALS":"card-ai-v61524/datathon/initial_data/ALS_abstracts.csv",
#              "FTD":"card-ai-v61524/datathon/initial_data/FTD_abstracts.csv",
#              "LBD":"card-ai-v61524/datathon/initial_data/LBD_abstracts.csv"}
    
# with st.container():
#     # get table
#     df = conn.read(table_dict[st.session_state.dx_name], input_format='csv')
    
#     # session state var for disease variable
#     st.session_state.dx_df = df
    
#     if st.session_state.dx_name != st.session_state.dx_name_last:  # activated when we change to a new dx_df
#         st.session_state.paper_i = 0
#         st.write(f'New disease selected: {st.session_state.dx_name} from {st.session_state.dx_name_last}')

#         # update session state var
#         st.session_state.dx_name_last = st.session_state.dx_name
        
#     # start dispalying data
#     if st.session_state.paper_i <= st.session_state.dx_df.shape[0]:
#         # get current row
#         st.session_state.current = st.session_state.dx_df.iloc[st.session_state.paper_i,:]
        
#         # update title and abstract vars
#         update_data_vars(st.session_state.current)

#         st.markdown(f"""#### Title: \n{st.session_state.title}""")
#         st.markdown(f"""#### Abstract: \n{st.session_state.abs}""")
#         st.markdown(f"""#### Additional paper data: \n""")
#         st.markdown(f"""#### DOI: \n{st.session_state.doi}""")
#         st.markdown(f"""#### PubMed ID: \n{st.session_state.pmid}""")
#     else:
#         st.write('End reached or an error has occured')

#     st.button('Next Paper', on_click=row_next)
    
#     st.button('Restart', on_click=row_restart)

    #st.write(f'Current row: {st.session_state.paper_i}')