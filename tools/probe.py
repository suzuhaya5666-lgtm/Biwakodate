import sys
sys.path.insert(0, ".")
import collect as c
cand = [2,3,127,130,69,70,115,8,121,6,97,119,28,40,41,10,23,24,43,44,46,102,50,54,105,83,78,79]
for n in cand:
    fcd = f"06401004{n:05d}"
    try:
        d = c.get_json(c.station_url("stg", fcd))
        h = [v for v in d.get("hrValues", []) if v.get("stg") is not None]
        m = [v for v in d.get("min10Values", []) if v.get("stg") is not None]
        print("DATA", fcd, "hr", len(h), "min10", len(m), "last", (h[-1] if h else None) if False else (h[0] if h else None))
    except Exception as e:
        print("DATA", fcd, "ERR", e)
