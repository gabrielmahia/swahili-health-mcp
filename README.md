# 🏥 Swahili Health MCP

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
