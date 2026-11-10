#!/usr/bin/env python3
"""川の防災情報のデータの場所を調べるための一時的な道具(収集には使わない)。"""
import json
import re
import urllib.request

F = "https://www.river.go.jp/kawabou/file/files/"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)


# サイトのプログラムから、obsCd(短い番号)の扱いを調べる
st, js = get("https://www.river.go.jp/kawabou/js/app.4d7d8c61.js")
n = 0
for m in re.finditer(r"obsCd", js):
    seg = js[max(0, m.start() - 90): m.start() + 130].replace("\n", " ")
    if "obsFcd" in seg or "tmlist" in seg or "master" in seg:
        print("CTX", seg)
        n += 1
        if n >= 12:
            break

# 滋賀県の観測所の一覧を探す
for path in ("map/pref/prefarea.json", "obslist/idx/pref/twn/25.json", "obslist/idx/rsys/pref/25.json",
             "obslist/idx/pref/twn/2500.json"):
    st, body = get(F + path)
    print("LIST", path, st, body[:500].replace("\n", " "))
