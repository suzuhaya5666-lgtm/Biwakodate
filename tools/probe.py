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
st, now = get("https://www.river.go.jp/kawabou/file/system/tmCrntTime.json")
d, t = json.loads(now)["crntObsTime"].split(" ")
show("DATA", f"tmlist/stg/{d.replace('/', '')}/{t.replace(':', '')}/0640100400081.json", 500)

# データの形(キー)を確認
st, body = get(F + f"tmlist/stg/{d.replace('/', '')}/{t.replace(':', '')}/0640100400081.json")
j = json.loads(body)
for k, v in j.items():
    print("KEY", k, type(v).__name__, (len(v) if isinstance(v, (list, dict)) else v))
for k in ("hrValues", "min10Values"):
    v = j.get(k) or []
    print("VAL", k, len(v), json.dumps(v[-3:], ensure_ascii=False)[:700])

# 川ごと・市ごとの観測所一覧
def lst(tag, path):
    st, body = get(F + path)
    if st != 200:
        print(tag, path, st)
        return
    try:
        jj = json.loads(body)
    except Exception:
        print(tag, path, "json?", body[:150])
        return
    items = jj if isinstance(jj, list) else next((v for v in jj.values() if isinstance(v, list)), [])
    print(tag, path, "keys", list(jj.keys())[:6] if isinstance(jj, dict) else "list", "n", len(items))
    for o in items:
        if isinstance(o, dict):
            print("OBS", o.get("obsFcd"), o.get("obsKnd") or o.get("itmkndCd"), o.get("obsNm") or o.get("obsNmS"), o.get("rvrNm"), o.get("twnNm"))


lst("RVR", "obslist/obs/rvrlist/86061442.json")
for c in range(2501201, 2501215):
    lst("TWN", f"obslist/obs/twnlist/{c}.json")
