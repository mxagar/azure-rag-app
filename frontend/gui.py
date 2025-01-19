"""Simple Streamlit GUI to interact with the RAG chatbot backend.

Usage:

    # Start backend, e.g., locally
    cd .../azure-rag-app
    docker run --rm --env-file .env -p 8080:8000 azure-rag-backend    
    # Open browser and go to http://localhost:8080/docs
    
    # Start GUI, e.g. locally
    cd .../azure-rag-app
    streamlit run frontend/gui.py
    # Browser should be opened automatically
    # Ctrl+C to stop the Streamlit server first, then close browser

Author: Mikel Sagardia
Date: 2025-01-11 
"""
import os
import pathlib
from dotenv import load_dotenv

import streamlit as st
import requests
import textwrap

# Load environment variables (local execution)
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
ROOT_DIR = CURRENT_DIR.parent
#ENV_FILE = os.path.join(ROOT_DIR, ".env")
ENV_FILE = os.path.join(ROOT_DIR, ".env_terraform")
try:
    _ = load_dotenv(ENV_FILE, override=True)
except Exception:
    pass

# Retrieve variables
RAG_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8080/ask")

# Proxy configuration, if required
#PROXIES = {"http": None, "https": None}  # LOCAL - No proxies...
PROXIES={"http": os.getenv("HTTP_PROXY", None), "https": os.getenv("HTTPS_PROXY", None)}  # AZURE - Use this only if you have any proxies...

# Streamlit page configuration
st.set_page_config(page_title="Chatbot", layout="wide")

# Streamlit app UI
st.title("Interactive Chatbot")
st.markdown("Engage in a conversation!")

# Persistent conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to send a message
def send_message(query):
    if not query.strip():
        return  # Don't send empty queries

    # Add user message to the state
    st.session_state.messages.append({"text": query, "is_user": True})

    # Make request to backend
    headers = {
        "Authorization": f"Bearer {os.getenv('RAG_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    try:
        response = requests.post(RAG_API_URL, json=payload, headers=headers, proxies=PROXIES)
        if response.status_code == 200:
            chatbot_response = response.json().get("response", "No response received.")
            st.session_state.messages.append({"text": chatbot_response, "is_user": False})
        else:
            st.error(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")

# Chat input and SEND button
with st.form("chat_form", clear_on_submit=True):
    query = st.text_input("Your message:", "", key="user_input")
    submitted = st.form_submit_button("SEND")

    if submitted and query.strip():
        send_message(query)

# Display conversation (correct chronological order with paired numbering)
if st.session_state.messages:
    conversation = st.session_state.messages[::-1]  # Reverse the order for display
    user_count, ai_count = 0, 0  # Counters for USER-X and AI-X labels

    for message in conversation:
        wrapped_text = "<br>".join(textwrap.wrap(message["text"], width=120))

        # Assign correct chronological numbering
        if message["is_user"]:
            user_count += 1
            order = f"USER-{user_count}"
            box_style = "text-align: left; background-color: rgba(144, 238, 144, 0.3);"
        else:
            ai_count += 1
            order = f"AI-{ai_count}"
            box_style = "text-align: right; background-color: rgba(211, 211, 211, 0.3);"

        # Style and render the message box
        st.markdown(
            f'<div style="{box_style} padding: 8px 12px; margin: 8px 0; border-radius: 10px; max-width: 100%; word-wrap: break-word;">'
            f'{wrapped_text}'
            f'<div style="text-align: right; font-size: 12px; color: gray;">{order}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
