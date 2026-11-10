#!/usr/bin/env python3
"""川の防災情報のデータの場所を調べるための一時的な道具(収集には使わない)。"""
import re
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)


PAGE = "https://www.river.go.jp/kawabou/pc/tm?zm=15&clat=35.342&clon=136.023&fld=0&mapType=0&ofcCd=6401&itmkndCd=4&obsCd=81"
st, html = get(PAGE)
print("page", st, len(html))
for ln in html.splitlines():
    if re.search(r"script|\.js|src=|href=.*(css|js)", ln, re.I):
        print("HTML", ln.strip()[:240])
srcs = re.findall(r"""src=["']([^"']+\.js[^"']*)["']""", html)
print("scripts", srcs)
seen = set()
for s in srcs:
    url = s if s.startswith("http") else "https://www.river.go.jp" + (s if s.startswith("/") else "/kawabou/pc/" + s)
    st, js = get(url)
    print("JS", url, st, len(js))
    for m in sorted(set(re.findall(r'[\w\-./{}$+\' "]*(?:tmlist|/files/|\.json|file/files|master)[\w\-./{}$+\' "]*', js))):
        m = m.strip()
        if 6 < len(m) < 160 and m not in seen:
            seen.add(m)
            print("  HIT", m)
