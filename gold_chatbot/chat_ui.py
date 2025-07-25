import streamlit as st
import requests
import base64
from io import BytesIO

# ---- Page Setup ----
st.set_page_config(page_title="Kalyan Jewellers Assistant", page_icon="💍")
st.title("💍 Kalyan Jewellers Assistant")

# ---- Configuration Variables ----
server_url = "https://kalyan-jewellers-fastapi.onrender.com"
# tts_url = "http://27.111.72.55:5052/synthesize"
tts_url="http://27.111.72.55:5006/google_tts"

# ---- Session State Init ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Chat History Display ----
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat Input ----
user_input = st.chat_input("Ask me about gold rates, offers, or stores...")

if user_input:
    # Show user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ---- Get LLM response ----
    try:
        response = requests.post(f"{server_url}/chat", json={"message": user_input})
        response.raise_for_status()
        reply = response.json()["response"]
    except Exception as e:
        reply = f"Error connecting to server: {e}"

    # ---- Get TTS audio in parallel ----
    audio_bytes = None
    try:
        tts_response = requests.post(
            tts_url,
            json={"text": reply},
            headers={"Content-Type": "application/json"},
        )
        tts_response.raise_for_status()
        audio_base64 = tts_response.json().get("audio")

        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)
        else:
            st.warning("TTS API did not return audio data.")

    except Exception as e:
        st.error(f"🔊 TTS error: {e}")

    # ---- Show assistant reply + audio TOGETHER ----
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
        if audio_bytes:
            import uuid
            audio_id = str(uuid.uuid4())
            audio_b64 = base64.b64encode(audio_bytes).decode()

            audio_html = f"""
            <audio id="{audio_id}" autoplay hidden>
                <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
            </audio>
            <script>
                var audio = document.getElementById("{audio_id}");
                if (audio) {{
                    audio.play();
                }}
            </script>
            """

            st.components.v1.html(audio_html, height=0)
