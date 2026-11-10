#!/usr/bin/env python3
"""川の防災情報のデータの場所を調べるための一時的な道具(収集には使わない)。"""
import json
import urllib.request

BASE = "https://www.river.go.jp/kawabou/file"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)


st, body = get(f"{BASE}/system/tmCrntTime.json")
print("tmCrntTime", st, body[:200])
now = json.loads(body)["crntObsTime"]
d, t = now.split(" ")
d, t = d.replace("/", ""), t.replace(":", "")
# 水位(stg)・雨量(rf など)を、いくつかの形で試す
cands = ["81", "0081", "640100000081", "6401000081", "2203900400009"]
for kind in ("stg", "rf", "rain", "rd", "stgrf"):
    for code in cands:
        url = f"{BASE}/files/tmlist/{kind}/{d}/{t}/{code}.json"
        st, body = get(url)
        print(kind, code, st, body[:160].replace("\n", " "))
# 観測所の一覧がありそうな場所
for path in ("system/obsList.json", "files/master/obs/81.json", "files/obs/6401.json",
             "files/map/stg/6401.json", "files/map/obs/6401.json", "system/tmCrntTime.json"):
    st, body = get(f"{BASE}/{path}")
    print("path", path, st, body[:160].replace("\n", " "))
