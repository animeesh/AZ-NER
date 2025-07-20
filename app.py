from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from IPython.display import Image, display

# Define the state structure
# class GreetingState(TypedDict):
#     greeting: str

class State(TypedDict):
    comment: str
    input: str
    user_feedback: str
    value: dict

# Define a reasoning step for the agent
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
    
    # Update and return new state
    state["value"] = value
    return state

def business_logic(state: State) -> str:
    print("business logic node")
    # Here you can implement any business logic you need
    # For example, you might want to check the claim amount or description
    # For now, we'll just return the state unchanged
    value = state.get("value", {})
    print(f"Business logic processing: value: {value}")
    claim_amount = state["value"]["claim_amount"]
    print(claim_amount)  # Output: 1000.0
    if claim_amount > 100:
        return "human_decision"
    return "approved_path" 


# Define a preprocessing node to normalize the comment
def human_decision_node(state: State) -> State:
    # Transform the comment to lowercase
    print("human decision node")
    #state["comment"] = state["comment"].lower()
    return state  # Return the updated state dictionary

# Define a node for the "Hi" greeting
def approved_node(state: State) -> State:
    #state["greeting"] = "Hi there, " + state["greeting"]
    print("claim approved")
    return state  # Return the updated state dictionary

# Define a node for a standard greeting
def rejected_node(state: State) -> State:
    #state["greeting"] = "Hello, " + state["greeting"]
    print("claim rejected")
    return state  # Return the updated state dictionary

# Define the conditional function to choose the appropriate verdict
def choose_node(state: State) -> str:
    # Choose the node based on whether "hi" is in the normalized greeting
    feedback = input("Please provide feedback on the input:(approve/reject) ")
    feedback = feedback.lower()  # Normalize the feedback to lowercase
    return "approved_path" if "approve" in feedback else "rejected_path"

# Initialize the StateGraph
builder = StateGraph(State)
builder.add_node("claim_details", claim_details)
builder.add_node("human_decision", human_decision_node)
builder.add_node("approved_path", approved_node)
builder.add_node("rejected_path", rejected_node)

# Add the START to normalization node, then conditionally branch based on the transformed greeting
builder.set_entry_point("claim_details")
#builder.add_edge("claim_details", "business_logic")
builder.add_conditional_edges(
    "claim_details", business_logic, ["approved_path", "human_decision"]
)
builder.add_conditional_edges(
    "human_decision", choose_node, ["approved_path", "rejected_path"]
)
builder.add_edge("approved_path", END)
builder.add_edge("rejected_path", END)

# Compile and run the graph
graph = builder.compile()

#Display the graph
display(Image(graph.get_graph().draw_mermaid_png()))

# Test with a comment containing "approve" in various forms (e.g., uppercase, mixed case)
result = graph.invoke({})
print(result)  
