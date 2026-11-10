# Telco Agent Lab

A small, fully synthetic telecom sandbox for exploring AI agents and the Model Context Protocol (MCP). It exposes subscriber, network-registration and authentication-status tools, plus guarded demo operations for service provisioning and line suspension.

The project is designed for local experiments, demos and agent-evaluation suites. It has no carrier integrations, external services, API keys, subscriber data, authentication secrets or cryptographic vectors.

## Why this exists

Telecom workflows combine structured operational data, sensitive customer context and actions with real-world consequences. This lab makes those boundaries tangible: customer case notes are explicitly marked untrusted, authentication tools expose status metadata only, and write tools require an explicit confirmation string and emit audit events.

The confirmation mechanism is a **demo guard, not production authorization**. A real deployment must obtain approval through an independent, authenticated control plane and enforce identity, authorization, idempotency, rate limits and durable auditing outside the model.

## Run it

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run telco-agent-lab
```

The server speaks MCP over stdio. Configure your MCP-compatible client to launch `uv run telco-agent-lab` from this repository. The simulator starts fresh each time.

## Tools

| Tool | Purpose |
| --- | --- |
| `list_subscribers` | List synthetic IDs, plans and status |
| `get_subscriber` | Read a profile; case notes are labeled untrusted |
| `get_network_status` | Read synthetic registration metadata |
| `get_auth_status` | Read profile state without returning credentials or vectors |
| `provision_service` | Add a supported service after the demo confirmation flow |
| `suspend_line` | Suspend a synthetic line after the demo confirmation flow |
| `get_audit_log` | Inspect attempted and completed write operations |

Sample subscriber IDs are `sub-1001`, `sub-1002` and `sub-1003`. All phone numbers and IMSIs are reserved-looking synthetic values for this sandbox; do not use them for network operations.

## Test

```bash
uv run pytest
```

## Scope

This is a teaching and prototyping project, not a carrier emulator or production-ready agent. It models a few HLR/HSS/AuC-inspired concepts in memory and intentionally omits protocol stacks, real subscriber credentials, persistence and external connectivity.

## License

MIT. See [LICENSE](LICENSE).
