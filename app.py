from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from IPython.display import Image, display
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage

load_dotenv() 

# Setting the API key
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key,
)


class State(TypedDict):
    comment: str
    input: str
    feedback: str
    value: dict


def claim_details(state: State) -> State:    
    print("claim details node")
    value = {
        "claim_id": "12345",
        "user_id": "67890",
        "claim_amount": 1000.0,
        "claim_description": "document lost in transit",
        "claim_date": "2023-10-01"
    }
    print(f"Agent claim detail fetch: value: {value}")
    state["value"] = value
    return state

def business_logic(state: State) -> str:
    print(f"Business logic processing: value")
    claim_amount = state["value"]["claim_amount"]
    print(claim_amount)  
    if claim_amount > 100:
        return "human_decision"
    return "approved_path" 


#HTIL connected to choose_node
def human_decision_node(state: State) -> State:
    print("human decision node")
    return state  # Return the updated state dictionary


#HITL Approve node
def approved_node(state: State) -> State:
    state["feedback"] = "approved"
    print("claim approved")
    messages = f"Understand the following state and give a two-line response to the user: {state},give a short reson to it with the help of claim_description in state"
    print((llm.invoke(messages).content))
    return state  

#HITL- Reject node
def rejected_node(state: State) -> State: 
    state["feedback"] = "rejected"
    print("claim rejected")
    messages = f"Understand the following state and give a two-line response to the user: {state},give a short reson to it with the help of claim_description in state"
    print((llm.invoke(messages).content))
    return state  

# Define the conditional function to choose the appropriate verdict
def choose_node(state: State) -> str:
    feedback = input("Please provide feedback on the input:(approve/reject) ")
    feedback = feedback.lower()  # Normalize the feedback to lowercase
    return "approved_path" if "approve" in feedback else "rejected_path"

# Initialize the StateGraph
builder = StateGraph(State)
builder.add_node("claim_details", claim_details)
builder.add_node("human_decision", human_decision_node)
builder.add_node("approved_path", approved_node)
builder.add_node("rejected_path", rejected_node)

builder.set_entry_point("claim_details")
builder.add_conditional_edges("claim_details", business_logic, ["approved_path", "human_decision"])
builder.add_conditional_edges("human_decision", choose_node, ["approved_path", "rejected_path"])
builder.add_edge("approved_path", END)
builder.add_edge("rejected_path", END)
graph = builder.compile()

#Display the graph
display(Image(graph.get_graph().draw_mermaid_png()))

# Test with a comment containing "approve" in various forms (e.g., uppercase, mixed case)
result = graph.invoke({})
print(result)  
