"""Glama scores tool definitions (server score = 60% mean + 40% worst tool). FastMCP keeps only a docstring's first line as the description, so the useful
detail (when to use it, what it returns, limits) must be in the explicit description. Every tool needs it and every parameter needs a description."""
import asyncio

from fastmcp import Client

from swahili_health_mcp import server


def _tools():
    async def go():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    return asyncio.run(go())


def test_every_tool_description_says_when_to_use_it_what_it_returns_and_that_it_is_read_only():
    for t in _tools():
        d = t.description or ""
        assert len(d) >= 300, (t.name, len(d))
        assert "Use when" in d or "Takes no arguments" in d, t.name
        assert "Returns" in d and "Read-only" in d, t.name


def test_every_parameter_has_a_description():
    for t in _tools():
        for name, prop in (t.inputSchema.get("properties") or {}).items():
            assert prop.get("description"), (t.name, name)
