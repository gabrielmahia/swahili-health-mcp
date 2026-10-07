"""swahili-health-mcp: Kenya county health indicators from the DHS Program's Kenya Demographic and Health Survey 2022.

The data is real and bundled (offline-first): swahili_health_mcp/data/kdhs2022_counties.json, rebuilt by scripts/refresh_kdhs.py from
https://api.dhsprogram.com. These are SURVEY ESTIMATES with sampling error (see "n" and the caveat in every answer), not routine facility reporting (KHIS).
"""
from __future__ import annotations

import json
import re
from importlib import resources

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

DATA = json.loads(resources.files("swahili_health_mcp").joinpath("data/kdhs2022_counties.json").read_text(encoding="utf-8"))
INDICATORS: dict[str, dict] = DATA["indicators"]
COUNTIES: dict[str, dict] = DATA["counties"]
LOWER_IS_BETTER = {"RH_PCMT_W_NON", "CH_VACC_C_NON", "CN_NUTS_C_HA2"}
VACCINES = {"BCG": "CH_VACC_C_BCG", "DPT3": "CH_VACC_C_DP3", "PENTA3": "CH_VACC_C_DP3", "MEASLES": "CH_VACC_C_MSL", "FULL": "CH_VACC_C_BAS", "FULLY_VACCINATED": "CH_VACC_C_BAS", "NONE": "CH_VACC_C_NON"}
CAVEAT = ("Survey estimate with sampling error (county samples are small: see n), for the stated reference period. Not routine facility data (KHIS) and "
          "not a clinical or operational record. Cite: KNBS and ICF, Kenya Demographic and Health Survey 2022, via the DHS Program.")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


_BY_NORM = {_norm(c): c for c in COUNTIES}
_BY_NORM.update({"nairobicity": "Nairobi", "muranga": "Murang'a", "tharakanithi": "Tharaka-Nithi" if "Tharaka-Nithi" in COUNTIES else _BY_NORM.get("tharakanithi", "")})


def resolve_county(name: str) -> str:
    """The canonical county name for a spelling such as "murang'a", "Muranga", "NAIROBI CITY"; raises ToolError listing valid names (never guesses)."""
    key = _norm(name or "")
    if _BY_NORM.get(key):
        return _BY_NORM[key]
    close = [c for c in COUNTIES if key and (key in _norm(c) or _norm(c) in key)]
    raise ToolError(f"Unknown county {name!r}." + (f" Did you mean: {', '.join(close)}?" if close else "") + f" Valid counties ({len(COUNTIES)}): {', '.join(sorted(COUNTIES))}.")


def resolve_indicator(name: str) -> str:
    """An indicator id from an id or a distinctive part of its label; raises ToolError listing the ids when it is not unique."""
    if name in INDICATORS:
        return name
    key = _norm(name or "")
    hits = [i for i, m in INDICATORS.items() if key and (key in _norm(m["label"]) or key == _norm(i))]
    if len(hits) == 1:
        return hits[0]
    raise ToolError(f"{'Ambiguous' if hits else 'Unknown'} indicator {name!r}. Use one of: " + "; ".join(f"{i} ({m['label']})" for i, m in INDICATORS.items()))


def _row(county: str, iid: str) -> dict:
    r, m = COUNTIES[county][iid], INDICATORS[iid]
    return {"indicator_id": iid, "label": m["label"], "value_pct": r["value"], "population": m["population"], "n": r["n"], "period": r["period"],
            "direction": "lower is better" if iid in LOWER_IS_BETTER else "higher is better"}


def _wrap(county: str, rows: list[dict]) -> dict:
    return {"county": county, "survey": "Kenya DHS 2022", "source": DATA["source"], "data_retrieved": DATA["retrieved"], "indicators": rows, "caveat": CAVEAT}


def county_health_profile(county: str) -> dict:
    c = resolve_county(county)
    return _wrap(c, [_row(c, i) for i in INDICATORS if i in COUNTIES[c]])


def maternal_indicators(county: str) -> dict:
    c = resolve_county(county)
    return _wrap(c, [_row(c, i) for i, m in INDICATORS.items() if m["group"] == "maternal" and i in COUNTIES[c]])


def immunization_coverage(county: str, vaccine: str = "DPT3") -> dict:
    c = resolve_county(county)
    v = _norm(vaccine or "")
    key = next((k for k in VACCINES if _norm(k) == v), None)
    if not key:
        raise ToolError(f"Unknown vaccine {vaccine!r}. Use one of: BCG, DPT3 (or PENTA3), MEASLES, FULL (fully vaccinated, 8 basic antigens), NONE (no vaccinations).")
    return _wrap(c, [_row(c, VACCINES[key])])


def compare(indicator: str, n: int = 5, order: str = "lowest") -> dict:
    iid = resolve_indicator(indicator)
    if order not in ("lowest", "highest"):
        raise ToolError("order must be 'lowest' or 'highest' (by numeric value; see each indicator's direction).")
    n = max(1, min(int(n), len(COUNTIES)))
    ranked = sorted(((c, COUNTIES[c][iid]) for c in COUNTIES if iid in COUNTIES[c]), key=lambda kv: kv[1]["value"], reverse=(order == "highest"))[:n]
    return {"indicator_id": iid, "label": INDICATORS[iid]["label"], "population": INDICATORS[iid]["population"], "order": order, "direction": "lower is better" if iid in LOWER_IS_BETTER else "higher is better",
            "counties": [{"county": c, "value_pct": r["value"], "n": r["n"], "period": r["period"]} for c, r in ranked], "survey": "Kenya DHS 2022", "source": DATA["source"], "caveat": CAVEAT}


READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}
mcp = FastMCP(
    "swahili-health-mcp",
    instructions=("Kenya county-level maternal, child immunization and child nutrition indicators from the DHS Program's Kenya Demographic and Health Survey 2022 "
                  "(real survey estimates, bundled offline). Use list_health_indicators first to see what exists. Values are survey estimates with sampling error, "
                  "not routine facility data; always state the survey, year and reference period when quoting them."),
)


@mcp.tool(name="list_health_indicators", annotations=READ_ONLY)
def list_health_indicators() -> dict:
    """List every health indicator this server holds (id, label, population it is measured on, whether higher or lower is better) and the survey it comes from.

    Call this first. All indicators are percentages from the Kenya DHS 2022 with a value for each of the 47 counties. Returns {survey, source, data_retrieved, indicators:[{id,label,population,group,direction}]}.
    """
    return {"survey": "Kenya DHS 2022", "source": DATA["source"], "data_retrieved": DATA["retrieved"], "counties": len(COUNTIES),
            "indicators": [{"id": i, "label": m["label"], "population": m["population"], "group": m["group"], "direction": "lower is better" if i in LOWER_IS_BETTER else "higher is better"} for i, m in INDICATORS.items()]}


@mcp.tool(name="get_county_health_profile", annotations=READ_ONLY)
def get_county_health_profile(county: str) -> dict:
    """Get every held indicator (maternal care, child immunization, child stunting) for one Kenyan county.

    Args:
        county: A county name such as "Mombasa", "Murang'a" or "Nairobi" (case, spaces and apostrophes are ignored). An unknown name returns an error listing the valid counties; nothing is guessed.
    Returns the county's survey estimates with sample size n, reference period, direction (higher/lower is better), source and a sampling-error caveat.
    """
    return county_health_profile(county)


@mcp.tool(name="get_maternal_health_indicators", annotations=READ_ONLY)
def get_maternal_health_indicators(county: str) -> dict:
    """Get a county's maternal health indicators: antenatal visits (4+), antenatal care from a skilled provider, skilled assistance at delivery, health-facility delivery, and mothers with no postnatal checkup.

    Args:
        county: A county name such as "Kisumu" or "Tana River". An unknown name returns an error listing the valid counties.
    Returns survey estimates (percent) with sample size n and reference period (the DHS-preferred two years before the survey), plus source and caveat.
    """
    return maternal_indicators(county)


@mcp.tool(name="get_immunization_coverage", annotations=READ_ONLY)
def get_immunization_coverage(county: str, vaccine: str = "DPT3") -> dict:
    """Get the percentage of children aged 12-23 months in a county who received a vaccine.

    Args:
        county: A county name such as "Turkana". An unknown name returns an error listing the valid counties.
        vaccine: One of BCG, DPT3 (also PENTA3), MEASLES, FULL (fully vaccinated with the 8 basic antigens) or NONE (received no vaccinations). Default DPT3. Anything else is an error: no default value is substituted.
    Returns the survey estimate with sample size n, reference period, source and caveat. For NONE, lower is better.
    """
    return immunization_coverage(county, vaccine)


@mcp.tool(name="compare_counties", annotations=READ_ONLY)
def compare_counties(indicator: str, n: int = 5, order: str = "lowest") -> dict:
    """Rank Kenyan counties on one indicator, to see where need is greatest or coverage is best.

    Args:
        indicator: An indicator id from list_health_indicators (for example "CH_VACC_C_DP3") or a distinctive part of its label (for example "stunted"). Ambiguous or unknown input returns an error listing the ids.
        n: How many counties to return, 1 to 47 (default 5).
        order: "lowest" or "highest" by numeric value. For indicators where lower is better (no vaccinations, stunting, no postnatal checkup) the result states the direction; lowest is then the best, not the worst.
    Returns the ranked counties with value (percent), sample size n and reference period, plus source and caveat. County samples are small: close values are not reliably different.
    """
    return compare(indicator, n, order)


def main() -> None:
    mcp.run()


run_server = main  # the console script's previous name, kept so existing MCP configs keep working


if __name__ == "__main__":
    main()
