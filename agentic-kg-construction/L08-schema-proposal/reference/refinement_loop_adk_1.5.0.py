"""Reference sketch, google-adk 1.5.0: proposer -> critic -> checker in a bounded LoopAgent, failing closed.
Our own wording; checked with scripted fake models only (lab/stage1/tests/l08_loop.py, l08_reference_check.py)."""
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types

APPROVE = "valid"   # the critic's whole reply when it approves; anything else means "not approved"

def propose_node(label: str, source_file: str, tool_context: ToolContext) -> dict:
    """Record the node rule for a label. A label already taken by another file is refused (a revision from the same file is allowed)."""
    nodes = dict(tool_context.state.get("nodes", {}))
    if label in nodes and nodes[label] != source_file:
        return {"status": "error", "error_message": f"Label {label} is already defined from {nodes[label]}. Use another label or remove it first."}
    nodes[label] = source_file
    tool_context.state["nodes"] = nodes   # assign a new dict: an in-place change is not tracked as a state delta
    return {"status": "success"}

class Checker(BaseAgent):
    """Escalate only on an exact approval AND a stored plan that covers every expected source file (the caller's set, not the model's);
    record the outcome in state and in a text event (so a tool caller sees it)."""
    expected_files: frozenset
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        st = ctx.session.state; fb = st.get("feedback"); n = st.get("rounds", 0) + 1
        approved = isinstance(fb, str) and fb.strip().lower() == APPROVE
        # A critic can approve while nothing was stored (refused last call, gotcha d): test the plan, not only the verdict. ctx.session.state is the LIVE
        # dict, which still holds writes ADK later drops (State.__setitem__ writes it directly, state.py:44), so read the persisted copy from the service.
        saved = await ctx.session_service.get_session(app_name=ctx.session.app_name, user_id=ctx.session.user_id, session_id=ctx.session.id)
        nodes = (saved.state.get("nodes") if saved else None) or {}
        missing = sorted(self.expected_files - set(nodes.values()))   # completeness: a plan that exists can still leave a file unplanned (T-037)
        ok = approved and bool(nodes) and not missing
        why = "no plan is stored" if not nodes else f"plan leaves {missing} unplanned"
        text = "APPROVED" if ok else (f"NOT_CONVERGED after {n} round(s): critic approved but {why}" if approved else f"NOT_CONVERGED after {n} round(s)")
        yield Event(invocation_id=ctx.invocation_id, author=self.name,
                    content=types.Content(role="model", parts=[types.Part(text=text)]),
                    actions=EventActions(escalate=ok, state_delta={"rounds": n, "converged": ok}))

def reset_state(callback_context):
    """LoopAgent before_agent_callback: a new run starts with no old verdict (also makes {feedback} resolvable on the first pass)."""
    s = callback_context.state; s["feedback"] = ""; s["rounds"] = 0; s["converged"] = False

def build_loop(proposer_model, critic_model, expected_files, max_iterations=3, name="refine"):
    """expected_files: the source files the caller knows must each get a node rule. Required on purpose: an empty set would turn the completeness test off."""
    if not expected_files: raise ValueError("expected_files must be a non-empty set")
    proposer = LlmAgent(name="proposer", model=proposer_model, tools=[FunctionTool(propose_node)],
                        instruction="Propose the plan with the tools. Reviewer notes, if any: [{feedback}]")
    critic = LlmAgent(name="critic", model=critic_model, output_key="feedback",
                      instruction=f"Check the plan against the data. Reply with exactly '{APPROVE}' if it is acceptable, otherwise 'revise: <reason>'.")
    return LoopAgent(name=name, sub_agents=[proposer, critic, Checker(name="checker", expected_files=frozenset(expected_files))],
                     max_iterations=max_iterations, before_agent_callback=reset_state)
# The caller must read state["converged"] (or the loop tool's text result) and hand a False to a human.
