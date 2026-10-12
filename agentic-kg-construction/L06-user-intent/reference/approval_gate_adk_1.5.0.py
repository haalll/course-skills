"""Approval gate from two tools, google-adk 1.5.0 (our wording; tested with scripted fake models, no live model).
Plain pair first, then the pair that refuses approval in the same invocation (turn) that wrote the perceived value."""
from google.adk.tools import ToolContext

def set_perceived_user_goal(kind_of_graph: str, graph_description: str, tool_context: ToolContext) -> dict:
    """Record what you think the user wants. kind_of_graph: at most three words. graph_description: a few sentences."""
    tool_context.state["perceived_user_goal"] = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    return {"status": "success"}

def approve_perceived_user_goal(tool_context: ToolContext) -> dict:
    """Call only after the user has confirmed the perceived goal. Takes no arguments."""
    if "perceived_user_goal" not in tool_context.state:
        return {"status": "error", "error_message": "No perceived goal yet. Set it first, or ask the user clarifying questions."}
    tool_context.state["approved_user_goal"] = dict(tool_context.state["perceived_user_goal"])
    return {"status": "success"}

# With a turn boundary: remember which invocation wrote the perceived value.
def set_perceived_h(kind_of_graph: str, graph_description: str, tool_context: ToolContext) -> dict:
    """Record what you think the user wants."""
    tool_context.state["perceived_user_goal"] = {"kind_of_graph": kind_of_graph, "graph_description": graph_description}
    tool_context.state["perceived_in"] = tool_context.invocation_id
    return {"status": "success"}

def approve_h(tool_context: ToolContext) -> dict:
    """Call only after the user has confirmed the perceived goal. Takes no arguments."""
    st = tool_context.state
    if "perceived_user_goal" not in st:
        return {"status": "error", "error_message": "Set the perceived goal first."}
    if st.get("perceived_in") == tool_context.invocation_id:
        return {"status": "error", "error_message": "The user has not seen this goal yet. Show it and wait for their reply."}
    st["approved_user_goal"] = dict(st["perceived_user_goal"])
    return {"status": "success"}
