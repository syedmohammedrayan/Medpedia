import json
from typing import AsyncGenerator
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from agent.graph import graph

class ResearchController:
    @staticmethod
    async def astream_research(query: str, thread_id: str) -> AsyncGenerator[str, None]:
        """Streams research events (tokens and state updates) to the frontend."""
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=query)]}

        # Use astream_events v2 for granular token-level and node-level events
        async for event in graph.astream_events(inputs, config=config, version="v2"):
            kind = event["event"]

            # 1. Node Start/End Events
            if kind == "on_chain_start":
                # We can filter for specific node names if needed
                node_name = event.get("metadata", {}).get("langgraph_node")
                if node_name:
                    yield f"data: {json.dumps({'type': 'node_start', 'node': node_name})}\n\n"

            # 2. Token Streaming (on_chat_model_stream)
            elif kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

            # 3. Final State or Intermediate Tool outputs
            elif kind == "on_chain_end":
                node_name = event.get("metadata", {}).get("langgraph_node")
                if node_name:
                    yield f"data: {json.dumps({'type': 'node_end', 'node': node_name})}\n\n"

        # Check for interrupt at the end of the stream
        state = await graph.aget_state(config)
        if state.next:
            interrupt_val = state.tasks[0].interrupts[0].value if state.tasks and state.tasks[0].interrupts else None
            yield f"data: {json.dumps({'type': 'interrupt', 'query': interrupt_val})}\n\n"

        yield "data: [DONE]\n\n"

    @staticmethod
    async def astream_resume(email: str, thread_id: str) -> AsyncGenerator[str, None]:
        """Streams events after resuming from an interrupt."""
        config = {"configurable": {"thread_id": thread_id}}

        async for event in graph.astream_events(Command(resume=email), config=config, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
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
