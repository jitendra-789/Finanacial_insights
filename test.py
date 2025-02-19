import streamlit as st
import pandas as pd
import os
import uuid
from mistralai import Mistral
from unstructured.partition.pdf import partition_pdf


# Authentication system
USER_CREDENTIALS = {"jitendra789": "@jitendra789"}  # Replace with a secure method later
def login():
    st.markdown("<h2 style='text-align: center;'>🔐 Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# Table extraction function (using unstructured package)
def extract_tables_from_pdf(filename, strategy='hi_res'):
    elements = partition_pdf(
        filename=filename,
        infer_table_structure=True,
        strategy=strategy,
    )
    tables = [el for el in elements if el.category == "Table"]
    if not tables:
        return [], []
    tables_html = [table.metadata.text_as_html for table in tables]
    dfs = [pd.read_html(html)[0] for html in tables_html if html]
    return dfs, tables_html

# Summarization function
def summarize_table(table_text):
    api_key = "MMNlnPxuMxBfeIGG4pIGIfSwBdIgjlVA" 
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": f"Summarize the following table data:\n{table_text}"}]
    )
    return chat_response.choices[0].message.content

def main():
    st.set_page_config(page_title="📄 PDF Table Extraction & Summarization", layout="wide", page_icon="📈")
    # Custom CSS for additional styling
    st.markdown("""
        <style>
            .header-container {
                background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .section {
                background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .header {
                font-size: 2.5em;
                font-weight: 800;
                text-align: center;
                background: linear-gradient(120deg, #0D6EFD 0%, #0B5ED7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                padding: 10px;
                letter-spacing: 1px;
            }

            .subheader {
                font-size: 1.8em;
                font-weight: 600;
                background: linear-gradient(120deg, #0D6EFD 0%, #0B5ED7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-top: 20px;
                margin-bottom: 10px;
                text-align: left;
            }

            .table-container {
                background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            @media (prefers-color-scheme: dark) {
                .header-container {
                    background: linear-gradient(135deg, #212529 0%, #343A40 100%);
                }
                
                .section {
                    background: linear-gradient(135deg, #212529 0%, #2B3035 100%);
                }
                
                .table-container {
                    background: linear-gradient(135deg, #212529 0%, #2B3035 100%);
                }
                
                .header {
                    background: linear-gradient(120deg, #6EA8FE 0%, #9EC5FE 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                .subheader {
                    background: linear-gradient(120deg, #6EA8FE 0%, #9EC5FE 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
            }

            .stButton > button {
                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                transition: all 0.3s ease;
            }

            .stButton > button:hover {
                background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header-container"><h1 class="header">📄 PDF Table Extraction and Summarization</h1></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<h2>Upload Your PDF</h2>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            st.session_state.temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
            with open(st.session_state.temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())

    if uploaded_file is not None:
        try:
            dfs, html_tables = extract_tables_from_pdf(st.session_state.temp_filename)
            if not dfs:
                st.warning("No tables found in the PDF.")
            else:
                for idx, df in enumerate(dfs):
                    st.markdown(f"### Table {idx+1}")
                    st.dataframe(df)
                    summary = summarize_table(df.to_string())
                    st.markdown(f"**Summary:** {summary}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()