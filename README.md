<div align="center">

# Planthire Ai MCP

**PlantHire.AI MCP Server - Construction Equipment AI**

[![PyPI](https://img.shields.io/pypi/v/meok-planthire-ai-mcp)](https://pypi.org/project/meok-planthire-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

PlantHire.AI MCP Server - Construction Equipment AI
Built by MEOK AI Labs | https://planthire.ai

Intelligent construction equipment search, rental quoting,
availability checking, booking, safety, and transport costing.

## Tools

| Tool | Description |
|------|-------------|
| `search_equipment` | Search the construction equipment catalog. |
| `get_rental_quote` | Calculate rental pricing for equipment. |
| `check_availability` | Check equipment availability for a date range. |
| `create_booking` | Create an equipment booking. |
| `get_safety_checklist` | Get pre-use safety inspection checklist for equipment type. |
| `calculate_transport` | Estimate transport costs for equipment delivery/collection. |

## Installation

```bash
pip install meok-planthire-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "planthire-ai": {
      "command": "python",
      "args": ["-m", "meok_planthire_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 6 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
