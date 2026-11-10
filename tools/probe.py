#!/usr/bin/env python3
"""川の防災情報の観測所を探すための一時的な道具(収集には使わない)。"""
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

F = "https://www.river.go.jp/kawabou/file/files/"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 biwako-fishing-collector/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", "ERR"), ""


def one(args):
    ofc, n = args
    fcd = f"{ofc:05d}004{n:05d}"
    st, body = get(F + f"master/obs/stg/{fcd}.json")
    if st != 200:
        return None
    try:
        o = json.loads(body)["obsInfo"]
    except Exception:
        return None
    return (fcd, o.get("obsNm"), o.get("rvrNm"), o.get("twnNm"), o.get("rsrvStg"), o.get("warnStg"),
            o.get("spclWarnStg"), o.get("dngStg"))


jobs = [(22039, n) for n in range(1, 80)] + [(6401, n) for n in range(1, 160)]
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(one, jobs):
        if r:
            print("STN", *r)
