"""Single ADK agent with one tool. Own wording. UNTESTED: never executed on the lab droplet.
Import paths for ADK 1.5.0 were not confirmed by running them."""
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def lookup(name: str) -> dict:
    """Look up a record by name for the model. Args: name (str). Returns a dict with 'status'."""
    try:
        rows = run_parameterised_query("MATCH (n {name: $name}) RETURN n", {"name": name})
        return {"status": "success", "rows": rows}
    except Exception as exc:  # errors become data the model can read
        return {"status": "error", "error_message": str(exc)}


def run_parameterised_query(query: str, params: dict) -> list:
    raise NotImplementedError("wire to your database driver")


def final_text(event) -> str:
    parts = (event.content.parts if event.content else None) or []
    return "".join(p.text for p in parts if getattr(p, "text", None))


async def main(model, text: str) -> str:
    agent = Agent(name="x_v1", model=model, description="public role",
                  instruction="when to use the tool; how to react to status=error",
                  tools=[lookup])
    svc = InMemorySessionService()
    await svc.create_session(app_name="x_app", user_id="u", session_id="s1", state=None)
    runner = Runner(agent=agent, app_name="x_app", session_service=svc)
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    async for ev in runner.run_async(user_id="u", session_id="s1", new_message=msg):
        if ev.is_final_response() and ev.author == agent.name:  # root agent's own final event
            return final_text(ev)
    return ""


if __name__ == "__main__":
    raise SystemExit("pass a model object to main(); run with asyncio.run(main(model, 'hi'))")
