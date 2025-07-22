import streamlit as st
import requests

# ---- Page Setup ----
st.set_page_config(page_title="Kalyan Jewellers Assistant", page_icon="💍")
st.title("💍 Kalyan Jewellers Assistant")

# ---- Server URL (Fixed) ----
server_url = "https://kalyan-jewellers-fastapi.onrender.com"

# ---- Initialize chat history ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Display chat history ----
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat input ----
user_input = st.chat_input("Ask me about gold rates, offers, or stores...")

if user_input:
    # Show user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to FastAPI backend
    try:
        response = requests.post(f"{server_url}/chat", json={"message": user_input})
        response.raise_for_status()
        reply = response.json()["response"]
    except Exception as e:
        reply = f"Error connecting to server: {e}"

    # Show assistant response
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
