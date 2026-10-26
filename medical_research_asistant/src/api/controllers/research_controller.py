# Interacts directly with the LangGraph state machine.
# Responsible for streaming the graph's execution events (tokens, node transitions) to the frontend.
import json
from typing import Any, AsyncGenerator
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from agent.graph import graph

def _extract_text(content: Any) -> str:
    """Safely extracts plain text from model chunk content (which can be str or list of dicts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif hasattr(item, "text"):
                parts.append(getattr(item, "text", ""))
        return "".join(parts)
    return str(content or "")

class ResearchController:
    @staticmethod
    async def astream_research(query: str, thread_id: str) -> AsyncGenerator[str, None]:
        """Streams research events (tokens and state updates) to the frontend."""
        # The thread_id ensures LangGraph can persist and retrieve this specific session's state.
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=query)]}

        try:
            # Use astream_events v2 for granular token-level and node-level events
            async for event in graph.astream_events(inputs, config=config, version="v2"):
                kind = event["event"]

                # 1. Node Start/End Events
                # Lets the frontend know which agent/step is currently running.
                if kind == "on_chain_start":
                    # We can filter for specific node names if needed
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name:
                        yield f"data: {json.dumps({'type': 'node_start', 'node': node_name})}\n\n"

                # 2. Token Streaming (on_chat_model_stream)
                # Sends each token to the UI in real-time as the LLM generates it.
                elif kind == "on_chat_model_stream":
                    content = _extract_text(event["data"]["chunk"].content)
                    if content:
                        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

                # 3. Final State or Intermediate Tool outputs
                elif kind == "on_chain_end":
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name:
                        yield f"data: {json.dumps({'type': 'node_end', 'node': node_name})}\n\n"

            # Check for interrupt at the end of the stream
            # If the graph paused (e.g. waiting for email), retrieve the prompt and send it to the frontend.
            state = await graph.aget_state(config)
            if state.next:
                interrupt_val = state.tasks[0].interrupts[0].value if state.tasks and state.tasks[0].interrupts else None
                yield f"data: {json.dumps({'type': 'interrupt', 'query': interrupt_val})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    @staticmethod
    async def astream_resume(email: str, thread_id: str) -> AsyncGenerator[str, None]:
        """Streams events after resuming from an interrupt."""
        # Re-uses the same thread_id to access the paused graph state.
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Verify that the thread actually exists and is currently paused at an interrupt
            state = await graph.aget_state(config)
            if not state.values or not state.next:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Session expired or server restarted while waiting for email. Please submit your research inquiry again.'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # Passes the provided email back into the graph via Command(resume=...).
            async for event in graph.astream_events(Command(resume=email), config=config, version="v2"):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    content = _extract_text(event["data"]["chunk"].content)
                    if content:
                        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

                elif kind == "on_chain_end":
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name:
                        yield f"data: {json.dumps({'type': 'node_end', 'node': node_name})}\n\n"

                        # Because the dispatcher is now a direct Python function (not an LLM),
                        # it does not fire chat stream tokens. We manually yield its output as a token.
                        if node_name == "med_email_dispatcher":
                            output = event.get("data", {}).get("output", {})
                            if isinstance(output, dict) and "email_status" in output:
                                yield f"data: {json.dumps({'type': 'token', 'content': output['email_status']})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
