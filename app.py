from typing import Literal, TypedDict
from urllib import response
from langgraph.types import interrupt, Command
import uuid
import os
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
#from google.generativeai import genai
from openai import OpenAI
from dotenv import load_dotenv
#import google.generativeai as genai

load_dotenv()
api_key = "apikey"
client = OpenAI(api_key=api_key)


# Define the shared graph state
class State(TypedDict):
    value: dict[str, str]
    llm_output: str
    decision: str

# # Simulate an LLM output node
# def generate_llm_output(state: State) -> State:
#     return {"llm_output": "This is the generated output."}



def claim_details(state: State) -> State:
    print("claim details node")
    value = {
        "claim_id": "12345",
        "user_id": "67890",
        "claim_amount": 1000.0,
        "claim_description": "document lost in transit",
        "claim_date": "2023-10-01"
    }
    return {"value": value}

def business_logic(state: State) -> State:
    print(f"business logic node {state['value']}")
    #print(f"state.type: {type(state['value'])}")
    # claim = state["value"]
    # # If claim is a string, convert to dict
    # if isinstance(claim, str):
    #     import ast
    #     claim = ast.literal_eval(claim)
    # risk = "high" if claim.get("claim_amount", 0) >= 100000 else "low"
    # print(f"Risk assessment: {risk}")
    # # Add risk to state
    # state["risk"] = risk
    # Here you can implement any business logic based on the claim details
    # For simplicity, we will just return the state as is
    return state

def generate_llm_output(state: State) -> State:
    print(f"Generating LLM output...")
    response = client.responses.create(
    model="o4-mini",
    input=f"understand the state value {state} and generate a one line short response for the customer.")
    print(response.output_text)
    return {"llm_output": response.output_text}

# Human approval node
def human_approval(state: State) -> Command[Literal["approved_path", "rejected_path"]]:
    decision = interrupt({
        "question": "Do you approve the following output?",
        "claim_details": state["value"]
    })

    if decision == "approve":
        return Command(goto="approved_path", update={"decision": "approved"})
    else:
        return Command(goto="rejected_path", update={"decision": "rejected"})

# Next steps after approval
def approved_node(state: State) -> State:
    print("✅ Approved path taken.")
    return state

# Alternative path after rejection
def rejected_node(state: State) -> State:
    print("❌ Rejected path taken.")
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("generate_llm_output", generate_llm_output)
builder.add_node("business_logic", business_logic)
builder.add_node("claim_details", claim_details)
builder.add_node("human_approval", human_approval)
builder.add_node("approved_path", approved_node)
builder.add_node("rejected_path", rejected_node)

#builder.set_entry_point("generate_llm_output")
#builder.add_edge("generate_llm_output", "human_approval")
builder.set_entry_point("claim_details")
builder.add_edge("claim_details", "business_logic")
builder.add_edge("business_logic", "human_approval")
# builder.add_edge("claim_details", "human_approval")
builder.add_edge("approved_path", "generate_llm_output")
builder.add_edge("rejected_path", "generate_llm_output")
builder.add_edge("generate_llm_output", END)


checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Run until interrupt
config = {"configurable": {"thread_id": uuid.uuid4()}}
result = graph.invoke({}, config=config)
print(result["__interrupt__"])
# Output:
# Interrupt(value={'question': 'Do you approve the following output?', 'llm_output': 'This is the generated output.'}, ...)

# Simulate resuming with human input
# To test rejection, replace resume="approve" with resume="reject"
final_result = graph.invoke(Command(resume="reject"), config=config)
#final_result = graph.invoke({}, config=config)
print(final_result)
