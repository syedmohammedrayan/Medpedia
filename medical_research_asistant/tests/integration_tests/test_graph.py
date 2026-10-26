import pytest

from agent import graph

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_agent_simple_passthrough() -> None:
    inputs = {"messages": [{"role": "user", "content": "hi"}]}
    config = {"configurable": {"thread_id": "test_thread_123"}}
    res = await graph.ainvoke(inputs, config=config)
    assert res is not None
