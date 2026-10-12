"""Reference sketch, google-adk 1.5.0: fact-type tool checked against approved entity types, failing closed.
Our own wording; checked with scripted fake models only (lab/stage1/tests/l09_facts.py, l09_reference_check.py)."""
import re
from google.adk.tools import ToolContext

def _norm(label: str) -> str:   # case, punctuation and a trailing plural 's' ignored; used only to HINT, never to accept
    return re.sub(r"s$", "", re.sub(r"[^a-z]", "", label.lower()))

def add_proposed_fact(subject_label: str, predicate: str, object_label: str, tool_context: ToolContext) -> dict:
    """Add ONE fact type. Both labels must be approved entity types."""
    approved = tool_context.state.get("approved_entities")
    if not approved:
        return {"status": "error", "error_message": "No approved entity types in state. Approve the entity types before proposing facts."}
    for label in (subject_label, object_label):
        if label not in approved:
            near = [a for a in approved if _norm(a) == _norm(label)]
            hint = f" Did you mean '{near[0]}'?" if near else ""
            return {"status": "error", "error_message": f"Label '{label}' is not an approved entity type.{hint} Approved: {sorted(approved)}."}
    predicate = re.sub(r"[^A-Z0-9]+", "_", predicate.upper()).strip("_")   # one spelling per predicate
    fact = {"subject_label": subject_label, "predicate": predicate, "object_label": object_label}
    facts = list(tool_context.state.get("proposed_facts", []))   # a list of triples, not a dict keyed by predicate
    if fact not in facts: facts.append(fact)
    tool_context.state["proposed_facts"] = facts                  # assign a new list: an in-place change is not tracked
    tool_context.state["proposed_in"] = tool_context.invocation_id
    return {"status": "success"}

def add_proposed_facts(facts: list[str], tool_context: ToolContext) -> dict:
    """Add several fact types in ONE call, each written 'Subject|PREDICATE|Object'. Every item gets its own verdict; good items are kept."""
    approved = tool_context.state.get("approved_entities")
    if not approved:
        return {"status": "error", "error_message": "No approved entity types in state. Approve the entity types before proposing facts."}
    stored = list(tool_context.state.get("proposed_facts", [])); verdicts = []
    for item in facts:
        subject, predicate, obj = (item.split("|") + ["", "", ""])[:3]
        bad = [x for x in (subject, obj) if x not in approved]
        if bad: verdicts.append(f"error: '{bad[0]}' is not an approved entity type (in '{item}')"); continue
        fact = {"subject_label": subject, "predicate": re.sub(r"[^A-Z0-9]+", "_", predicate.upper()).strip("_"), "object_label": obj}
        if fact not in stored: stored.append(fact)
        verdicts.append("ok")
    tool_context.state["proposed_facts"] = stored   # ONE write for the whole call, so a refused item cannot erase the others
    tool_context.state["proposed_in"] = tool_context.invocation_id
    return {"status": "success", "verdicts": verdicts}

def approve_proposed_facts(tool_context: ToolContext) -> dict:
    """Approve the proposed facts. Takes no arguments. Refused when nothing is stored or when they were proposed in this same turn."""
    if not tool_context.state.get("proposed_facts"):
        return {"status": "error", "error_message": "No proposed facts are stored. Propose facts first."}
    if tool_context.state.get("proposed_in") == tool_context.invocation_id:
        # Re-write the stored proposal in THIS call's delta: ADK keeps only the last call's delta in a response (T-020), and a refusal
        # that writes nothing would erase what the earlier add calls of the same response stored.
        tool_context.state["proposed_facts"] = list(tool_context.state["proposed_facts"])
        tool_context.state["proposed_in"] = tool_context.state["proposed_in"]
        return {"status": "error", "error_message": "Facts were proposed in this same turn; the user has not seen them. Ask for confirmation first."}
    tool_context.state["approved_facts"] = list(tool_context.state["proposed_facts"])
    return {"status": "success"}

async def propose_until_stored(run_turn, get_state, max_retries=2):
    """Post-turn guard. run_turn(message) runs one agent turn; get_state() reads the session state afterwards.
    Returns True when facts are stored; False (fail closed, the caller must not approve) after max_retries corrective turns."""
    message = "Propose the fact types."
    for attempt in range(max_retries + 1):
        await run_turn(message)
        if get_state().get("proposed_facts"): return True
        message = "You did not call add_proposed_fact. Call it once per fact type."
    return False
