import json, sys
from pathlib import Path
d = json.loads((Path(__file__).parents[1] / "data" / "mock_gds_response.json").read_text())
assert d["status"] == "success" and len(d["trips"]) == 5 and "search_meta" in d
for t in d["trips"]:
    assert t["from_city_name"] == "Bangalore" and t["to_city_name"] == "Mumbai"
    assert t["booking_token"] and t["schedule"]["departure_date"] == "2026-08-09"
print("dataset OK:", len(d["trips"]), "trips")
