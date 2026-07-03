"""
swahili-health-mcp — MCP server for Kenya health data
Wraps Kenya DHIS2 public API as MCP tools for AI agents
"""
from __future__ import annotations
import sys
import json

# DHIS2 Kenya public endpoint
DHIS2_BASE = "https://hiskenya.org/api"

# Demo health facility data (DEMO — synthetic, for MCP tool development)
DEMO_FACILITIES = [
    {"name": "Kenyatta National Hospital", "county": "Nairobi", "level": 6, "type": "National Referral",
     "lat": -1.3010, "lon": 36.8066, "beds": 1800, "emergency": True},
    {"name": "Pumwani Maternity Hospital", "county": "Nairobi", "level": 5, "type": "County Referral",
     "lat": -1.2727, "lon": 36.8503, "beds": 620, "emergency": True},
    {"name": "Mbagathi County Hospital", "county": "Nairobi", "level": 4, "type": "County Hospital",
     "lat": -1.3219, "lon": 36.7559, "beds": 250, "emergency": True},
    {"name": "Kiambu County Referral Hospital", "county": "Kiambu", "level": 4, "type": "County Hospital",
     "lat": -1.1714, "lon": 36.8336, "beds": 350, "emergency": True},
    {"name": "Nakuru Level 5 Hospital", "county": "Nakuru", "level": 5, "type": "County Referral",
     "lat": -0.2800, "lon": 36.0667, "beds": 420, "emergency": True},
]

def search_facilities(county: str | None = None, level: int | None = None) -> list[dict]:
    """Search health facilities — uses demo data with note to use KHIS for production."""
    results = DEMO_FACILITIES
    if county:
        results = [f for f in results if county.lower() in f["county"].lower()]
    if level:
        results = [f for f in results if f["level"] == level]
    return results


def get_maternal_indicators(county: str) -> dict:
    """Return maternal health indicators for a county — demo data."""
    return {
        "county": county,
        "data_source": "DEMO — synthetic data for development. Use KHIS (hiskenya.org) for real data.",
        "year": "2023",
        "anc_visits_4plus_pct": 72.4,
        "skilled_birth_attendance_pct": 81.2,
        "postnatal_care_pct": 68.9,
        "maternal_mortality_per_100k": 362,
        "note": "Real data: hiskenya.org/api/analytics"
    }


def get_immunization(county: str, vaccine: str = "DPT3") -> dict:
    """Return immunization coverage — demo data."""
    vaccine_data = {
        "BCG": 97.2, "OPV3": 89.1, "DPT3": 85.6,
        "PCV3": 83.4, "Measles": 78.9, "Rota2": 80.1
    }
    return {
        "county": county,
        "vaccine": vaccine,
        "coverage_pct": vaccine_data.get(vaccine, 80.0),
        "year": "2023",
        "data_source": "DEMO — synthetic. Real data: hiskenya.org",
        "target_pct": 90.0,
        "gap": max(0, 90.0 - vaccine_data.get(vaccine, 80.0))
    }


def mcp_list_tools() -> dict:
    return {
        "tools": [
            {
                "name": "search_health_facilities",
                "description": "Tafuta vituo vya afya Kenya / Search Kenya health facilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "county": {"type": "string", "description": "County name (e.g., Nairobi, Kiambu)"},
                        "level": {"type": "integer", "description": "Facility level (1-6)"}
                    }
                }
            },
            {
                "name": "get_maternal_health_indicators",
                "description": "Pata takwimu za afya ya uzazi / Get maternal health indicators for a county",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "county": {"type": "string", "description": "County name"}
                    },
                    "required": ["county"]
                }
            },
            {
                "name": "get_immunization_coverage",
                "description": "Pata kiwango cha chanjo / Get immunization coverage for a county and vaccine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "county": {"type": "string", "description": "County name"},
                        "vaccine": {"type": "string", "description": "Vaccine name (BCG, DPT3, Measles, etc.)", "default": "DPT3"}
                    },
                    "required": ["county"]
                }
            }
        ]
    }


def mcp_call_tool(name: str, arguments: dict) -> dict:
    if name == "search_health_facilities":
        results = search_facilities(arguments.get("county"), arguments.get("level"))
        return {"content": [{"type": "text", "text": json.dumps(results, ensure_ascii=False, indent=2)}]}
    elif name == "get_maternal_health_indicators":
        data = get_maternal_indicators(arguments["county"])
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]}
    elif name == "get_immunization_coverage":
        data = get_immunization(arguments["county"], arguments.get("vaccine", "DPT3"))
        return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]}
    else:
        return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}


def run_server():
    """Run MCP server over stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            method = msg.get("method", "")
            msg_id = msg.get("id")

            if method == "initialize":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "swahili-health-mcp", "version": "0.1.0"},
                    "capabilities": {"tools": {}}
                }}
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": mcp_list_tools()}
            elif method == "tools/call":
                params = msg.get("params", {})
                result = mcp_call_tool(params.get("name", ""), params.get("arguments", {}))
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            print(json.dumps(resp), flush=True)
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            print(json.dumps(err), flush=True)


if __name__ == "__main__":
    run_server()
