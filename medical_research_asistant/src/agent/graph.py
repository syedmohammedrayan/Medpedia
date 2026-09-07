import os
import time
from typing import Any, Dict
from typing_extensions import NotRequired

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt

from langchain_core.messages import AIMessageChunk, ToolMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables from .env file
load_dotenv()

# ── Imports (compatible with LangGraph Studio package resolution) ──────────────
# pyproject.toml maps: "agent" -> src/agent, "tools" -> src/tools
from tools.pubmed import pubmed_to_pmc_full_text_search
from tools.send_email_tool import send_email
from agent.prompts import (
    MED_QUERY_INGESTOR_INSTRUCTION,
    MED_EVIDENCE_BUILDER_INSTRUCTION,
    MED_EMAIL_DISPATCHER_INSTRUCTION,
)

# ── Model ──────────────────────────────────────────────────────────────────────
model = ChatOpenRouter(
    model="google/gemini-2.5-flash",
    temperature=0,
    max_tokens=8192
) 


# ──────────────────────────────────────────────────────────────────────────────
# Custom State
# We extend the basic messages list with two extra fields:
#   recipient_email  — collected via the HITL interrupt
#   email_status     — final result from the dispatcher agent
# ──────────────────────────────────────────────────────────────────────────────
class MedResearchState(MessagesState):
    """Extends MessagesState with email and report fields.
    messages is inherited from MessagesState (uses add_messages reducer).
    """
    recipient_email: NotRequired[str]   # auto-filled by HITL interrupt
    email_status: NotRequired[str]      # auto-filled by email dispatcher
    articles_report: NotRequired[str]   # raw list from ingestor
    evidence_report: NotRequired[str]   # synthesized report from builder


# ──────────────────────────────────────────────────────────────────────────────
# Agent 1 — Med Query Ingestor (ReAct)
# ──────────────────────────────────────────────────────────────────────────────
med_query_react_agent = create_react_agent(
    model,
    tools=[pubmed_to_pmc_full_text_search],
    prompt=MED_QUERY_INGESTOR_INSTRUCTION,
)


async def med_query_ingestor_node(state: MedResearchState) -> Dict[str, Any]:
    """Runs the ingestor and returns a clean text summary for LangSmith."""
    t0 = time.time()
    print(f"\n[TIMING] med_query_ingestor → started")
    result = await med_query_react_agent.ainvoke({"messages": state["messages"]})
    last_msg_content = result["messages"][-1].content
    print(f"[TIMING] med_query_ingestor → done in {time.time() - t0:.2f}s | output chars: {len(last_msg_content)}")
    return {
        "messages": [AIMessage(content=last_msg_content)],
        "articles_report": last_msg_content,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Agent 2 — Med Evidence Builder (direct model call — no tools needed)
# ──────────────────────────────────────────────────────────────────────────────
async def med_evidence_builder_node(state: MedResearchState) -> Dict[str, Any]:
    """
    Transforms ingestor articles into an evidence report.
    Calls the model directly (no ReAct loop) since no tools are required.
    """
    articles_list = state.get("articles_report", "No articles found.")
    t0 = time.time()
    print(f"\n[TIMING] med_evidence_builder → started | input chars: {len(articles_list)}")
    messages = [
        SystemMessage(content=MED_EVIDENCE_BUILDER_INSTRUCTION),
        HumanMessage(content=(
            "Here are the biomedical articles retrieved by the previous agent.\n"
            "Please build an evidence matrix table and narrative synthesis from them:\n\n"
            f"{articles_list}"
        )),
    ]
    result = await model.ainvoke(messages)
    print(f"[TIMING] med_evidence_builder → done in {time.time() - t0:.2f}s | output chars: {len(result.content)}")
    return {
        "messages": [AIMessage(content=result.content)],
        "evidence_report": result.content,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Node 3 — Email Collector  (Human-in-the-Loop INTERRUPT)
# ──────────────────────────────────────────────────────────────────────────────
def email_collector_node(state: MedResearchState) -> Dict[str, Any]:
    """
    Pauses graph execution and asks the human for a recipient email address.

    LangGraph resumes this node once the caller supplies a value via
    `graph.invoke(Command(resume=<email>), config=...)`.
    The returned value from `interrupt()` is the email string provided by
    the human.
    """
    recipient_email: str = interrupt(
        "📧 To whom should I send the literature package? "
        "Please provide the recipient's email address."
    )
    # The value will be whatever string the human types when resuming
    return {
        "recipient_email": recipient_email,
        "messages": AIMessage(
            content=f"✅ Email address received: **{recipient_email}**. Sending the literature package now…"
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Node 4 — Med Email Dispatcher (Direct Tool Execution)
# ──────────────────────────────────────────────────────────────────────────────
def med_email_dispatcher_node(state: MedResearchState) -> Dict[str, Any]:
    """
    Sends the full literature package using dedicated state fields.
    Invokes the tool directly to bypass LLM maximum-output-token limits when
    handling massive payload strings (like 50+ articles).
    """
    evidence_report = state.get("evidence_report", "No evidence report available.")
    articles_list = state.get("articles_report", "No articles list available.")

    recipient_email = state.get("recipient_email", "")

    # Combine them for the email tool
    combined_content = (
        "# 🔬 Medical Research Insights\n\n"
        "## 🧪 Executive Evidence Summary\n\n"
        f"{evidence_report}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "## 📚 Source Articles (Search Results)\n\n"
        f"{articles_list}"
    )

    try:
        # Directly invoke the tool logically
        tool_result = send_email.invoke({
            "evidence_report": combined_content,
            "recipient_email": recipient_email
        })
        reply_message = f"✅ **Email dispatch result:** {tool_result}"
    except Exception as e:
        reply_message = f"❌ **Failed to send email:** {e}"

    return {
        "messages": [AIMessage(content=reply_message)],
        "email_status": reply_message,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Build the Sequential Graph
# ──────────────────────────────────────────────────────────────────────────────
builder = StateGraph(MedResearchState)

builder.add_node("med_query_ingestor",    med_query_ingestor_node)
builder.add_node("med_evidence_builder",  med_evidence_builder_node)
builder.add_node("email_collector",       email_collector_node)       # ← HITL
builder.add_node("med_email_dispatcher",  med_email_dispatcher_node)

builder.add_edge(START,                  "med_query_ingestor")
builder.add_edge("med_query_ingestor",   "med_evidence_builder")
builder.add_edge("med_evidence_builder", "email_collector")            # pause here
builder.add_edge("email_collector",      "med_email_dispatcher")
builder.add_edge("med_email_dispatcher", END)

# Create a memory saver for local persistence (essential for FastAPI and Interrupts)
memory = MemorySaver()

# LangGraph API manages persistence automatically — no custom checkpointer needed.
# interrupt() works because the platform injects its own checkpointer at runtime.
# For local FastAPI, we provide it explicitly.
graph = builder.compile(checkpointer=memory)


# ──────────────────────────────────────────────────────────────────────────────
# Streaming Runner (for local terminal use)
# ──────────────────────────────────────────────────────────────────────────────
def stream_graph(user_input: str, thread_id: str = "default"):
    """
    Runs the graph, streams each agent's token output, then handles the
    Human-in-the-Loop pause for the email address.

    Usage:
        from agent.graph import stream_graph
        stream_graph("What are the latest treatments for diabetes?")
    """
    from langgraph.types import Command

    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [{"role": "user", "content": user_input}],
              "recipient_email": "",
              "email_status": ""}

    current_node = None

    # ── First pass: run until the interrupt ───────────────────────────────────
    for chunk in graph.stream(inputs, config=config, stream_mode="values"):
        # After the interrupt the graph pauses; we get here on each state snapshot
        pass

    # Check whether we hit an interrupt
    state = graph.get_state(config)
    while state.next:                      # graph is paused
        # Print the interrupt question
        for task in state.tasks:
            if hasattr(task, "interrupts") and task.interrupts:
                for intr in task.interrupts:
                    print(f"\n{'='*60}")
                    print(f"  ⏸  HUMAN INPUT REQUIRED")
                    print(f"{'='*60}")
                    print(f"\n{intr.value}\n")

        email = input("Your answer: ").strip()

        # Resume the graph with the provided email
        for chunk in graph.stream(
            Command(resume=email), config=config, stream_mode="messages"
        ):
            message_chunk, metadata = chunk
            node_name = metadata.get("langgraph_node", "unknown")

            if node_name != current_node:
                current_node = node_name
                print(f"\n\n{'='*60}")
                print(f"  Agent: {node_name}")
                print(f"{'='*60}\n")

            if isinstance(message_chunk, AIMessageChunk):
                print(message_chunk.content, end="", flush=True)
            elif isinstance(message_chunk, ToolMessage):
                print(f"\n[Tool '{message_chunk.name}' result]: "
                      f"{message_chunk.content[:300]}…\n")

        state = graph.get_state(config)

    print("\n\n[Pipeline Complete]\n")
