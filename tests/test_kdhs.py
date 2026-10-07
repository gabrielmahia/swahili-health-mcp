"""The bundled data, the tools through a real FastMCP client, and the refresh rules. No network."""
import asyncio
import importlib.util
import pathlib

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from swahili_health_mcp import server as s

REFRESH = importlib.util.spec_from_file_location("refresh", pathlib.Path(__file__).resolve().parents[1] / "scripts" / "refresh_kdhs.py")
refresh = importlib.util.module_from_spec(REFRESH)
REFRESH.loader.exec_module(refresh)


def call(name, **args):
    async def go():
        async with Client(s.mcp) as c:
            r = await c.call_tool(name, args)
            return r.structured_content if r.structured_content is not None else r.data
    return asyncio.run(go())


def test_the_snapshot_covers_all_47_counties_with_every_indicator():
    assert len(s.COUNTIES) == 47 and "Nairobi" in s.COUNTIES
    for county, rec in s.COUNTIES.items():
        assert set(rec) == set(s.INDICATORS), county
        assert all(0 <= v["value"] <= 100 for v in rec.values()), county


def test_the_preferred_reference_period_is_used_not_the_other_row():
    """DHS gives each county two rows (two and three years before the survey). Mombasa ANC 4+ is 65.3 for the preferred two-year period, 70.1 for three years."""
    assert s.COUNTIES["Mombasa"]["RH_ANCN_W_N4P"]["value"] == 65.3
    assert s.COUNTIES["Mombasa"]["RH_ANCN_W_N4P"]["period"] == "Two years preceding the survey"


def test_the_server_lists_exactly_the_tools_the_readme_documents():
    async def names():
        async with Client(s.mcp) as c:
            return sorted(t.name for t in await c.list_tools())
    tools = asyncio.run(names())
    assert tools == ["compare_counties", "get_county_health_profile", "get_immunization_coverage", "get_maternal_health_indicators", "list_health_indicators"]
    readme = (pathlib.Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    assert all(f"`{t}`" in readme for t in tools), "README must document every tool"
    import re
    assert not re.search(r"^\|\s*`(get_disease_surveillance|get_health_worker_count|get_health_facility|search_facilities_by_county)`", readme, re.MULTILINE), "the tool table must not advertise tools that do not exist"


def test_counties_resolve_from_common_spellings_and_unknowns_error_without_guessing():
    assert s.resolve_county("murang'a") == "Murang'a" and s.resolve_county("MURANGA") == "Murang'a" and s.resolve_county("Nairobi City") == "Nairobi"
    with pytest.raises(ToolError) as e:
        s.resolve_county("Atlantis")
    assert "Valid counties" in str(e.value)


def test_values_differ_between_counties_unlike_the_old_synthetic_numbers():
    """The previous version returned the same demo numbers for every county."""
    a, b = call("get_immunization_coverage", county="Nairobi", vaccine="DPT3"), call("get_immunization_coverage", county="Turkana", vaccine="DPT3")
    assert a["indicators"][0]["value_pct"] != b["indicators"][0]["value_pct"]


def test_an_unknown_vaccine_is_an_error_not_a_made_up_80_percent():
    with pytest.raises(ToolError):
        call("get_immunization_coverage", county="Nairobi", vaccine="Smallpox")


def test_every_answer_carries_its_provenance():
    r = call("get_maternal_health_indicators", county="Kisumu")
    assert r["survey"] == "Kenya DHS 2022" and "DHS Program" in r["source"] and r["data_retrieved"] and "sampling error" in r["caveat"]
    assert all({"value_pct", "n", "period", "direction"} <= set(i) for i in r["indicators"]) and len(r["indicators"]) == 5


def test_compare_counties_orders_correctly_and_states_direction():
    low = call("compare_counties", indicator="CH_VACC_C_DP3", n=3, order="lowest")
    high = call("compare_counties", indicator="CH_VACC_C_DP3", n=3, order="highest")
    assert low["counties"][0]["value_pct"] <= low["counties"][1]["value_pct"] and high["counties"][0]["value_pct"] >= high["counties"][1]["value_pct"]
    assert call("compare_counties", indicator="stunted", n=2)["direction"] == "lower is better"
    with pytest.raises(ToolError):
        call("compare_counties", indicator="no such thing")


def test_refresh_keeps_preferred_rows_only_and_finds_nairobi_as_a_region_row():
    rows = [{"IsPreferred": 0, "CharacteristicLabel": "..Mombasa", "Value": 70.1, "DenominatorUnweighted": 186, "ByVariableLabel": "Three years"},
            {"IsPreferred": 1, "CharacteristicLabel": "..Mombasa", "Value": 65.3, "DenominatorUnweighted": 134, "ByVariableLabel": "Two years"},
            {"IsPreferred": 1, "CharacteristicLabel": "Nairobi", "Value": 80.5, "DenominatorUnweighted": 300, "ByVariableLabel": "Two years"},
            {"IsPreferred": 1, "CharacteristicLabel": "Coast", "Value": 69.9, "DenominatorUnweighted": 900, "ByVariableLabel": "Two years"},
            {"IsPreferred": 1, "CharacteristicLabel": "..Kwale", "Value": "", "DenominatorUnweighted": 1, "ByVariableLabel": "Two years"}]
    out = refresh.county_rows(rows)
    assert out["Mombasa"]["value"] == 65.3 and out["Nairobi"]["value"] == 80.5 and "Coast" not in out and "Kwale" not in out
