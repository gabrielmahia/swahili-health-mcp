# AGENTS.md — swahili-health-mcp

<!-- coverage-adaptive-reasoning:v2 -->

## What this is
MCP server for Kenya county health indicators: maternal care, immunization and child stunting from the Kenya DHS 2022.

## Read first
- README.md
- agent-context.json
- Portfolio reasoning standard: https://github.com/gabrielmahia/nairobi-stack/blob/main/docs/COVERAGE_ADAPTIVE_REASONING.md

## Critical rules
- Truth labels: never present synthetic, simulated, demo or hand-compiled data as real or verified. Mark it in the data itself (`synthetic: true`, a `source` that says so) and in the README. If a real source cannot be cited with an as-of date, the output must say so.
- Any number a user might act on (tax rates and limits, phone numbers, emergency lines) needs a primary source or two independent listings, with the date checked in the `source` field. Unverifiable entries are removed, never labelled 'DEMO - verified'.
- The README tool table must list exactly the tools the server exposes; do not hard-code server counts. Keep `<!-- mcp-name: io.github.gabrielmahia/swahili-health-mcp -->` in the README: the MCP registry refuses a release without it.
- Every tool declares MCP annotations (`readOnlyHint`, `idempotentHint`, `openWorldHint`; `destructiveHint` for anything that sends money or messages, or writes). Read-only means no side effects.
- CI installs this repository's code (never the published package) on Python 3.10-3.14; lint failures are real (no `|| true`). Python 3.10 reaches end of life on 2026-10-31: drop it then.
- Releases are tag-driven and tokenless: bump `version` in pyproject.toml and server.json together, merge to main, push tag `vX.Y.Z`; the Publish workflow (test, PyPI Trusted Publisher, MCP registry) does the rest. PyPI releases are immutable. After a release run `scripts/glama_sync.py --apply` from nature-ai-evolution-lab to regenerate glama.json from the running server (a weekly audit flags drift).
- The pyproject `description` must be a complete sentence naming what the tools do: it is what PyPI, the MCP registry and Glama show (six were once cut off mid-word at 80 characters). Do not hard-code tool counts in it.
- Prefer a bundled, dated, sourced snapshot (offline-first) over live calls that can hang; never call an endpoint that has not been verified to exist.
- At the tool boundary return errors to the model as data instead of crashing the server; a broad `except` needs `# noqa: BLE001` and a reason.
- The data is the DHS Program's Kenya DHS 2022, bundled in swahili_health_mcp/data/kdhs2022_counties.json; rebuild with scripts/refresh_kdhs.py. Use the DHS-preferred reference period only, and read Nairobi from its region row (it has no county row).
- Answers must carry source, survey, period and sample size; unknown counties or vaccines are errors, never defaults.

## Coverage-Adaptive Reasoning v2

For consequential research, recommendations, investigations, analogy searches, forecasting, opportunity discovery, and canon building:

- A correct ranking inside an incomplete universe is still a failed answer.
- Separate candidate generation from candidate ranking.
- Materiality-gate the search: use the minimum useful set of orthogonal retrieval routes that could change the answer.
- Before closure ask what correct answer the current search method would be structurally incapable of finding.
- Treat aliases, language/geography, era, source class, format, genealogy, taxonomy, legal identity vs operational control/economic benefit, intermediaries, schema categories, null/failure cases, and negative space as potential blind spots when material.
- Maintain leading + competing + null explanations.
- Distinguish answer confidence from coverage confidence.
- “Nothing found” is not evidence of absence when coverage is low.
- Stop when additional independent search routes no longer materially change the candidate universe, hypotheses, decision, or next test.
- When an important miss occurs, repair the retrieval architecture via MISS → SENSOR REDESIGN; do not merely append the missed example.

## Multi-agent protocol
- Git is the memory bus.
- Read Issues and open/draft PRs before starting.
- Work from an Issue.
- Branch: `agent/<agent>/<issue>-<slug>`
- Open a draft PR immediately to claim scope.
- If another PR overlaps, review/subdivide rather than duplicate.
- Leave tests + handoff in Git.

## Commands
```bash
# install
pip install -e . pytest ruff
# test
python -m pytest tests -q
# lint
ruff check . --ignore E501 --ignore F401
```

## Never autonomously
- change licensing
- expose credentials
- perform irreversible external actions
