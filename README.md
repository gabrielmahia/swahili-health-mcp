# Swahili Health MCP
<!-- mcp-name: io.github.gabrielmahia/swahili-health-mcp -->

Kenya **county-level** maternal health, child immunization and child stunting indicators for AI agents, from the DHS Program's **Kenya Demographic and Health Survey 2022**.
Real survey data, bundled in the package (works offline), with the source, survey year, reference period and sample size on every answer.

[![PyPI version](https://badge.fury.io/py/swahili-health-mcp.svg)](https://badge.fury.io/py/swahili-health-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Tools

| Tool | What it does |
|------|--------------|
| `list_health_indicators` | The 11 indicators held (id, label, population, whether higher or lower is better) and the survey they come from. Call this first. |
| `get_county_health_profile` | Every indicator for one county. |
| `get_maternal_health_indicators` | Antenatal visits (4+), antenatal care from a skilled provider, skilled assistance at delivery, health-facility delivery, no postnatal checkup. |
| `get_immunization_coverage` | Children 12-23 months who received BCG, DPT3, measles, were fully vaccinated (8 basic antigens) or received none. |
| `compare_counties` | Rank the counties on one indicator: where is need greatest, where is coverage best. |

All 47 counties, Nairobi included. An unknown county or vaccine is an **error that lists the valid values**; nothing is guessed or defaulted.

## Install and use

```bash
pip install swahili-health-mcp
claude mcp add swahili-health -- swahili-health-mcp      # or: uvx swahili-health-mcp
```

Then ask: "Which five counties have the lowest DPT3 coverage?", "Compare antenatal care in Turkana and Nairobi."

## What these numbers are, and are not
- **Survey estimates**, not routine facility reporting (KHIS). Each carries sampling error; county samples are small, so close values are not reliably different (the sample size `n` is in every answer).
- The reference period is the DHS-preferred one (the two years before the survey). DHS also publishes a three-year period for the same counties; this server deliberately uses one.
- Data: The DHS Program, Kenya DHS 2022 (KNBS and ICF), retrieved from `api.dhsprogram.com` and bundled as `swahili_health_mcp/data/kdhs2022_counties.json`. Rebuild it with `python scripts/refresh_kdhs.py` (needs network; the server does not).
- Not clinical advice and not an operational record. There is **no facility register, disease surveillance or health-worker data** here: earlier versions advertised some of those and did not deliver them (see below).

## Changes in 0.2.0 (breaking)
- Replaced synthetic demo numbers (identical for every county) with real KDHS 2022 county estimates.
- Removed the demo facility list (unverified details). A real facility register (Kenya Master Health Facility List) is not integrated yet.
- The README previously listed tools that never existed (`get_disease_surveillance`, `get_health_worker_count`, and others); the tool list above is exactly what the server exposes, and a test enforces it.
- Moved from a hand-rolled JSON-RPC loop to FastMCP 4, which serves both the legacy and the stateless 2026-07-28 MCP protocol revisions.

## IP & Collaboration

MIT licensed. Feedback via GitHub Issues only — pull requests are not accepted. Survey estimates are not suitable for clinical or operational decisions. Full policy: [docs/architecture/IP_POLICY.md](docs/architecture/IP_POLICY.md). Security reports: see [SECURITY.md](SECURITY.md).

<!-- interconnect:v1 -->
## Part of the East Africa coordination stack

- **Install & run:** `pip install reli-cli && reli list` — the MCP servers on the [official MCP Registry](https://registry.modelcontextprotocol.io) under `io.github.gabrielmahia`
- **Evaluate any model on Swahili agent tasks:** [kipimo](https://github.com/gabrielmahia/kipimo) · [dataset](https://huggingface.co/datasets/gmahia/kipimo) · [leaderboard](https://huggingface.co/spaces/gmahia/kipimo-leaderboard)
- **Coordinate across servers:** [africa-coord-bus](https://pypi.org/project/africa-coord-bus/) — offline-first event bus with a built-in Kenya routing table
- **Datasets:** [huggingface.co/gmahia](https://huggingface.co/gmahia) · **Docs hub:** [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack)

Model-agnostic by design: closed APIs, open-weight models, and small distilled models are all first-class citizens.
<!-- /interconnect:v1 -->
