# 🏥 Swahili Health MCP
<!-- mcp-name: io.github.gabrielmahia/swahili-health-mcp -->

Model Context Protocol (MCP) server for Kenya health data. Provides AI agents with tools to query Kenya health facilities, maternal health indicators, immunization coverage, and disease surveillance data via the DHIS2 public API.

[![PyPI version](https://badge.fury.io/py/swahili-health-mcp.svg)](https://badge.fury.io/py/swahili-health-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Tools

| Tool | Description |
|------|-------------|
| `get_health_facility` | Get details of a Kenya health facility by name or code |
| `search_facilities_by_county` | List health facilities in a county with level and services |
| `get_maternal_health` | Maternal health indicators — ANC visits, skilled birth attendance |
| `get_immunization_coverage` | Child immunization coverage by vaccine and county |
| `get_disease_surveillance` | Weekly disease surveillance data (malaria, diarrhea, pneumonia) |
| `get_health_worker_count` | Health worker density by county |

## Usage with Claude

```bash
# Install
pip install swahili-health-mcp

# Add to Claude Code
claude mcp add swahili-health -- swahili-health-mcp

# Or with uvx
claude mcp add swahili-health -- uvx swahili-health-mcp
```

## Data Sources

- Kenya DHIS2 (dhis.moh.go.ke) — Ministry of Health open data
- Kenya Health Facility Registry (kenyaemr.org)
- Kenya Health Information System (KHIS)

All data is publicly available via Kenya's open government data policy.

## Part of the East Africa Civic Tech Portfolio

See also: [mpesa-mcp](https://github.com/gabrielmahia/mpesa-mcp) | [wapimaji-mcp](https://github.com/gabrielmahia/wapimaji-mcp)

## IP & Collaboration

MIT licensed. Feedback via GitHub Issues only — pull requests are not accepted. Demo data is labeled DEMO and is not suitable for operational decisions. Full policy: [docs/architecture/IP_POLICY.md](docs/architecture/IP_POLICY.md). Security reports: see [SECURITY.md](SECURITY.md).

<!-- interconnect:v1 -->
## Part of the East Africa coordination stack

- **Install & run:** `pip install reli-cli && reli list` — 33 MCP servers on the [official MCP Registry](https://registry.modelcontextprotocol.io) under `io.github.gabrielmahia`
- **Evaluate any model on Swahili agent tasks:** [kipimo](https://github.com/gabrielmahia/kipimo) · [dataset](https://huggingface.co/datasets/gmahia/kipimo) · [leaderboard](https://huggingface.co/spaces/gmahia/kipimo-leaderboard)
- **Coordinate across servers:** [africa-coord-bus](https://pypi.org/project/africa-coord-bus/) — offline-first event bus with a built-in Kenya routing table
- **Datasets:** [huggingface.co/gmahia](https://huggingface.co/gmahia) · **Docs hub:** [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack)

Model-agnostic by design: closed APIs, open-weight models, and small distilled models are all first-class citizens.
<!-- /interconnect:v1 -->
