from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph,MessagesState,START
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END


from tools import gold_price_data
from system_message import cred_system_kalyan_jewelers

from guidelines_context import get_guidelines_context
import os 
from dotenv import load_dotenv
load_dotenv()


llm=ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


tools=[gold_price_data]
llm_bind_tools=llm.bind_tools(tools)



# system message template
sys_message=SystemMessage(
    content=cred_system_kalyan_jewelers.format(
        guidelines=get_guidelines_context()
    )
)

def assistant(state:MessagesState):
    return{
        "messages":
        [llm_bind_tools.invoke([sys_message]+state["messages"])]
    }
    
     


builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition
)
builder.add_edge("tools", "assistant")
graph = builder.compile()

state = {"messages": []}



# while True:
#     user_input = input("You: ")

#     if user_input.lower() in ["exit", "quit"]:
#         print("Assistant: Goodbye!")
#         break

#     state = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
#     response = state["messages"][-1].content
#     print(f"Assistant: {response}")

#     if "Thank you for reaching out to Kalyan Jewellers" in response:
#         break
