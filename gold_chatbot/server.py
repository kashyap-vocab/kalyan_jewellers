from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import graph

import time

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]

)

class ChatRequest(BaseModel):
    message: str

session_state = {"messages": []}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = {"role": "user", "content": request.message}
    session_state["messages"].append(user_message)
    start_time=time.time()
    try:
        result = graph.invoke({"messages": session_state["messages"]})
        response = result["messages"][-1].content
        session_state["messages"] = result["messages"] 
    except Exception as e:
        response = f"Error: {str(e)}"
    end_time=time.time()
    latency=end_time-start_time
    return {
        "response": response,
        "latency":latency
        }

