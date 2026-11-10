#!/usr/bin/env python3
import json, urllib.request
F = "https://www.river.go.jp/kawabou/file/files/"
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), ""
st, b = get(F + "../system/tmCrntTime.json".replace("files/../", "")) if False else get("https://www.river.go.jp/kawabou/file/system/tmCrntTime.json")
t = json.loads(b)["crntObsTime"]
print("TIME", t)
d, hm = t[:8], t[8:12]
cand = [2,3,127,130,69,70,115,8,121,6,97,119,28,40,41,10,23,24,43,44,46,102,50,54,105,83,78,79]
for n in cand:
    fcd = f"0640100400{n:03d}".replace("0640100400", "06401004") if False else f"06401004{n:05d}"
    s, body = get(F + f"tmlist/stg/{d}/{hm}/{fcd}.json")
    v = None
    try:
        j = json.loads(body)
        v = (str(j)[:160])
    except Exception:
        pass
    print("DATA", fcd, s, v)
