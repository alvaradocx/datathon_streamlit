import streamlit as st
from elasticsearch import Elasticsearch
import pandas as pd

# Elasticsearch connection
ELASTIC_KEY = st.secrets["elasticsearch"]
CLIENT = Elasticsearch(
    ELASTIC_KEY['url'],
    api_key=ELASTIC_KEY['encoded'],
    request_timeout=30
)
INDEX = ELASTIC_KEY["index"]

def query_index(query, search_field="abstract", top_k=10):
    response = CLIENT.search(
        index=INDEX,
        body={
            "query": {
                "match": {
                    search_field: query
                }
            },
            "sort": [
                {"_score": "desc"},
            ],
            "size": top_k,
        }
    )
    return response

# Streamlit UI
st.set_page_config(page_title="NDD Paper + Abstract Search Engine", page_icon="📄", layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 40px;'>NDD Paper + Abstract Search Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 20px;'>Enter a query to search for relevant abstracts and research papers.</p>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton button {
        font-size: 18px;
    }
    .expander-content {
        font-size: 18px;
    }
    .stTextInput label {
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# Create columns for the text input and the dropdown
col1, col2 = st.columns([2, 1], gap="small")

with col1:
    query = st.text_input("Enter your query:")

with col2:
    top_k = st.selectbox("Number of results to view:", options=[10, 20, 30, 40, 50], index=0)

if st.button("Search"):
    if query:
        res = query_index(query, top_k=top_k)
        hits = res['hits']['hits']
        st.markdown(f"<h2>Top {len(hits)} results for '{query}':</h2>", unsafe_allow_html=True)
        
        N_cards_per_row = 2
        for n_row, hit in enumerate(hits):
            source = hit['_source']
            i = n_row % N_cards_per_row
            if i == 0:
                st.write("---")
                cols = st.columns(N_cards_per_row, gap="large")
            
            with cols[n_row % N_cards_per_row]:
                with st.expander(source['title'], expanded=False):
                    st.markdown(f"<p class='expander-content'><b>Abstract:</b> {source['abstract']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='expander-content'><b>Paper ID:</b> {source['paperId']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='expander-content'><b>Corpus ID:</b> {source['corpusId']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='expander-content'><b>DOI:</b> {source['DOI']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='expander-content'><b>PubMed:</b> {source['PubMed']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='expander-content'><b>Disease:</b> {source['Disease']}</p>", unsafe_allow_html=True)
    else:
        st.write("Please enter a query to search.")