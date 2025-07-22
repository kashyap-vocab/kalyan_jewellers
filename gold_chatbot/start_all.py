# gold_chatbot/start_all.py
import subprocess
import threading

def run_fastapi():
    subprocess.run(["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "chat_ui.py", "--server.port=8501", "--server.address=0.0.0.0"])

# Start both in threads
threading.Thread(target=run_fastapi).start()
threading.Thread(target=run_streamlit).start()
