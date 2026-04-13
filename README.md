# PlantHire.AI MCP Server

> **By [MEOK AI Labs](https://meok.ai)** — Sovereign AI tools for everyone.

Construction equipment rental intelligence. Search equipment, get rental quotes, check availability, create bookings, access HSE-compliant safety checklists, and calculate transport costs for UK plant hire.

[![MCPize](https://img.shields.io/badge/MCPize-Listed-blue)](https://mcpize.com/mcp/planthire-ai)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-255+_servers-purple)](https://meok.ai)

## Tools

| Tool | Description |
|------|-------------|
| `search_equipment` | Search construction equipment catalog |
| `get_rental_quote` | Calculate tiered rental pricing with insurance and fuel options |
| `check_availability` | Check equipment availability across UK depot locations |
| `create_booking` | Create a confirmed equipment booking with full pricing |
| `get_safety_checklist` | HSE/CPCS-compliant pre-use inspection checklists |
| `calculate_transport` | Estimate delivery/collection costs by equipment class |

## Quick Start

```bash
pip install mcp
git clone https://github.com/CSOAI-ORG/planthire-ai-mcp.git
cd planthire-ai-mcp
python server.py
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "planthire-ai": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/planthire-ai-mcp"
    }
  }
}
```

## Pricing

| Plan | Price | Requests |
|------|-------|----------|
| Free | $0/mo | 50 requests/month |
| Pro | $19/mo | 5,000 requests/month |

[Get on MCPize](https://mcpize.com/mcp/planthire-ai)

## Part of MEOK AI Labs

This is one of 255+ MCP servers by MEOK AI Labs. Browse all at [meok.ai](https://meok.ai) or [GitHub](https://github.com/CSOAI-ORG).

---
**MEOK AI Labs** | [meok.ai](https://meok.ai) | nicholas@meok.ai | United Kingdom
