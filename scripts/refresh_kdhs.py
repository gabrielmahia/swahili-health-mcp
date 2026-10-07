"""Rebuild swahili_health_mcp/data/kdhs2022_counties.json from the DHS Program's open API (https://api.dhsprogram.com). Needs network; the server does not.

    python scripts/refresh_kdhs.py

Rules that matter (learned from the data, 2026-10-07):
- every county has two rows per indicator, for two reference periods; DHS marks one IsPreferred=1, and only that one is kept
- Nairobi has NO county row: DHS reports it as a region row (no '..' prefix), so the 8 regions are scanned for it
- an indicator with no county-level rows is dropped, never filled in
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import urllib.request

API = "https://api.dhsprogram.com/rest/dhs/data"
SURVEY = "KE2022DHS"
INDICATORS = {
    "RH_ANCN_W_N4P": ("Antenatal care: 4 or more visits", "women with a live birth", "maternal"),
    "RH_ANCP_W_SKP": ("Antenatal care from a skilled provider", "women with a live birth", "maternal"),
    "RH_DELA_C_SKP": ("Assistance during delivery from a skilled provider", "live births", "maternal"),
    "RH_DELP_C_DHF": ("Delivery in a health facility", "live births", "maternal"),
    "RH_PCMT_W_NON": ("No postnatal checkup for the mother", "women with a live birth", "maternal"),
    "CH_VACC_C_BCG": ("BCG vaccination received", "children 12-23 months", "immunization"),
    "CH_VACC_C_DP3": ("DPT 3 (pentavalent) vaccination received", "children 12-23 months", "immunization"),
    "CH_VACC_C_MSL": ("Measles vaccination received", "children 12-23 months", "immunization"),
    "CH_VACC_C_BAS": ("Fully vaccinated (8 basic antigens)", "children 12-23 months", "immunization"),
    "CH_VACC_C_NON": ("Received no vaccinations", "children 12-23 months", "immunization"),
    "CN_NUTS_C_HA2": ("Children stunted (height-for-age below -2 SD)", "children under 5", "nutrition"),
}


def fetch(indicator: str) -> list[dict]:
    url = f"{API}?countryIds=KE&surveyIds={SURVEY}&breakdown=subnational&indicatorIds={indicator}&perpage=500&f=json"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "swahili-health-mcp-refresh"}), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))["Data"]


def county_rows(rows: list[dict]) -> dict[str, dict]:
    """County -> value record, from the preferred-period rows only."""
    out = {}
    for r in rows:
        if r.get("IsPreferred") != 1:
            continue
        label = r["CharacteristicLabel"]
        name = label[2:] if label.startswith("..") else ("Nairobi" if label == "Nairobi" else None)
        if not name or r.get("Value") in (None, ""):
            continue
        out[name] = {"value": float(r["Value"]), "n": r.get("DenominatorUnweighted"), "ci_low": r.get("CILow") or None, "ci_high": r.get("CIHigh") or None, "period": r.get("ByVariableLabel")}
    return out


def build() -> dict:
    indicators, counties = {}, {}
    for iid, (label, base, group) in INDICATORS.items():
        rows = county_rows(fetch(iid))
        if not rows:
            print(f"dropped {iid}: no county-level rows")
            continue
        indicators[iid] = {"label": label, "unit": "percent", "population": base, "group": group, "counties_covered": len(rows)}
        for name, rec in rows.items():
            counties.setdefault(name, {})[iid] = rec
    return {"source": "The DHS Program, Kenya Demographic and Health Survey 2022 (KE2022DHS), subnational estimates", "licence_note": "DHS Program open data: cite 'KNBS and ICF. Kenya Demographic and Health Survey 2022' and the DHS Program",
            "api": API, "survey": SURVEY, "retrieved": dt.datetime.now(dt.timezone.utc).date().isoformat(), "preferred_period_only": True, "indicators": indicators, "counties": dict(sorted(counties.items()))}


if __name__ == "__main__":
    data = build()
    dest = pathlib.Path(__file__).resolve().parents[1] / "swahili_health_mcp" / "data" / "kdhs2022_counties.json"
    dest.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {dest} | {len(data['counties'])} counties, {len(data['indicators'])} indicators")
