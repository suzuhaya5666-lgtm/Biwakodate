#!/usr/bin/env python3
"""川の防災情報のデータの場所を調べるための一時的な道具(収集には使わない)。"""
import json
import urllib.request

F = "https://www.river.go.jp/kawabou/file/files/"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)


def show(tag, path, n=900):
    st, body = get(F + path)
    print(tag, path, st, body[:n].replace("\n", " ").replace("  ", ""))
    return st, body


# 1) URLの観測所(0640100400081)の名前・基準水位
show("MASTER", "master/obs/stg/0640100400081.json", 1500)
st, now = get(F + "system/tmCrntTime.json")
d, t = json.loads(now)["crntObsTime"].split(" ")
show("DATA", f"tmlist/stg/{d.replace('/', '')}/{t.replace(':', '')}/0640100400081.json", 500)

# 2) 滋賀県の市町の観測所一覧
twn = ["25201", "25202", "25203", "25204", "25206", "25207", "25208", "25209", "25210", "25211",
       "25212", "25213", "25214", "25383", "25384", "25425", "25441", "25442", "25443"]
for c in twn:
    st, body = get(F + f"obslist/obs/twnlist/{c}.json")
    if st != 200:
        print("TWN", c, st)
        continue
    try:
        j = json.loads(body)
    except Exception:
        print("TWN", c, "json?", body[:200])
        continue
    items = j if isinstance(j, list) else next((v for v in j.values() if isinstance(v, list)), [])
    print("TWN", c, "keys", list(j.keys())[:6] if isinstance(j, dict) else "list", "n", len(items))
    for o in items:
        if isinstance(o, dict):
            nm = o.get("obsNm") or o.get("obsNmS")
            print("OBS", c, o.get("obsFcd"), o.get("obsKnd") or o.get("itmkndCd"), nm, o.get("rvrNm") or o.get("rvrCd"))
