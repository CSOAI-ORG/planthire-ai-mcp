<!-- mcp-name: CSOAI-ORG/planthire-ai-mcp -->
[![MCP Scorecard: 86/100](https://img.shields.io/badge/proofof.ai-86%2F100-5b21b6)](https://proofof.ai/scorecard/planthire-ai-mcp.html)

# Planthire Ai MCP

[![MEOK AI Labs](https://img.shields.io/badge/MEOK-AI%20Labs-667eea)](https://meok.ai)
[![GSPC](https://img.shields.io/badge/GSPC-UNMEASURED-9ca3af)](https://councilof.ai/api/gspc)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Install-3775a9)](https://pypi.org/project/planthire_ai_mcp/)

> planthire-ai-mcp MCP — AI-powered automation tool

planthire-ai-mcp MCP — AI-powered automation tool. MIT.

---

## 🚀 Quick Start
PlantHire AI is an MCP server for UK construction equipment rental, built by [MEOK AI Labs](https://meok.ai).
It provides intelligent search across a plant hire catalog, rental quote calculation,
real-time availability checking, booking creation, HSE-compliant pre-use safety
checklists, and transport cost estimation for equipment delivery and collection.

**Use cases:** excavator/dumper/roller hire quotation, site equipment availability
checks, LOLER/PUWER safety compliance, transport planning for heavy plant,
and multi-item rental booking workflows.

## Tools

| Tool | Description |
|------|-------------|
| `search_equipment` | Search the construction equipment catalog by type, capacity, or keyword. Returns matching plant with specs and daily/weekly rates. |
| `get_rental_quote` | Calculate rental pricing for a piece of equipment over a given hire period, including delivery and collection costs. |
| `check_availability` | Check whether specific equipment is available for a requested date range across depots. |
| `create_booking` | Create an equipment rental booking with delivery address, hire dates, and contact details. |
| `get_safety_checklist` | Get an HSE-compliant pre-use safety inspection checklist tailored to the equipment type (e.g. excavator, telehandler). |
| `calculate_transport` | Estimate transport costs for delivery and/or collection of hired equipment based on site postcode and equipment dimensions. |

## Installation

```bash
# Install via pip
pip install planthire_ai_mcp

# Or install via Smithery
npx -y @smithery/cli@latest install planthire-ai-mcp --client claude
```

## ✨ Features

- MCP protocol compliant
- Easy installation
- Well-documented API
- Production-ready
- Active maintenance

## 📖 Documentation

- [Full Documentation](https://docs.meok.ai/planthire-ai-mcp)
- [API Reference](https://api.meok.ai)
- [EU AI Act Compliance Guide](https://councilof.ai/compliance)

## 🛡️ Compliance

This MCP server is built with **EU AI Act compliance** built-in:

- ✅ Article 9 — Risk Management System
- ✅ Article 13 — Transparency & Instructions for Use
- ✅ Article 15 — Bias Detection & Testing
- ✅ Article 26 — FRIA Support (where applicable)
- ✅ Article 50 — AI Content Watermarking (where applicable)

Need help getting compliant? **[Book a free 15-min diagnostic →](https://cal.com/csoai/august-audit)**

## How MEOK charges

MEOK has no subscriptions and no tiers. You pay per job, and only when the agreed artifact has been delivered to you. There is no public price list. See <https://meok.ai/pricing>.

This repository's source is MIT-licensed and free to self-host.

## 🤝 Part of the MEOK Ecosystem

This server is part of the **[MEOK AI Labs](https://meok.ai)** ecosystem — 300+ MCP servers for sovereign AI governance.

| Domain | Purpose |
|--------|---------|
| [councilof.ai](https://councilof.ai) | EU AI Act compliance marketplace |
| [safetyof.ai](https://safetyof.ai) | AI safety & monitoring |
| [meok.ai](https://meok.ai) | Sovereign AI platform |
| [cobolbridge.ai](https://cobolbridge.ai) | Legacy modernization |

## 📜 License

MIT © [CSOAI-ORG](https://github.com/CSOAI-ORG)

---

<p align="center">
  <sub>Built with 💜 by <a href="https://meok.ai">MEOK AI Labs</a> · UK Companies House 16939677</sub>
</p>
MIT © [MEOK AI Labs](https://meok.ai)

<!-- meok-moat-footer-v1 -->
---

## Pairs with MEOK Governance Suite

Build something that touches users? You need compliance. MEOK ships 38 governance MCPs that drop in alongside this tool — EU AI Act, DORA, NIS2, CRA, GDPR, ISO 42001, FDA SaMD, MDR, Basel, MiFID II, MiCA, COPPA, and more.

```bash
# One-shot install of the governance pack
npx meok-setup --pack governance
```


→ Full catalogue: [councilof.ai](https://councilof.ai)
→ MEOK AI Labs: [meok.ai](https://meok.ai)




## Configuration

Add to your `claude_desktop_config.json` (Claude Desktop) or your MCP client config:

```json
{
  "mcpServers": {
    "planthire-ai-mcp": {
      "command": "uvx",
      "args": ["planthire-ai-mcp"]
    }
  }
}
```

Or: `pip install planthire-ai-mcp` then run the `planthire-ai-mcp` command (stdio transport).

## Examples

Once configured, ask your assistant, for example:
- "Use `search_equipment` to …"
- "Use `get_rental_quote` to …"
- "Use `check_availability` to …"

<!-- mcp-name: io.github.CSOAI-ORG/planthire-ai-mcp -->
