import asyncio

from mcp import Client

from telco_agent_lab.server import mcp


def test_tools_are_discoverable_and_auth_metadata_is_redacted():
    async def exercise():
        async with Client(mcp) as client:
            listed = await client.list_tools()
            assert {tool.name for tool in listed.tools} == {
                "list_subscribers", "get_subscriber", "get_network_status",
                "get_auth_status", "provision_service", "suspend_line", "get_audit_log",
            }
            result = await client.call_tool("get_auth_status", {"subscriber_id": "sub-1001"})
            return result.structured_content

    auth_status = asyncio.run(exercise())
    assert auth_status["ok"] is True
    assert auth_status["secrets_returned"] is False
    assert "Ki" not in auth_status
