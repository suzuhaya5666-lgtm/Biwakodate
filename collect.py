#!/usr/bin/env python3
"""川の防災情報(国土交通省)から観測値を取得し、data/observations.csv に追記する。

使い方:
  python collect.py                      # 取得して CSV に追記
  python collect.py --dump stg 2203900400009   # 1地点の生データを表示(項目の確認用)
出典: 国土交通省 川の防災情報
"""
import csv
import json
import sys
import urllib.request
from pathlib import Path

BASE = "https://www.river.go.jp/kawabou/file"
OUT = Path("data/observations.csv")
HEADER = ["time", "place", "level", "flow", "temp"]

# (地点名, 種別, 観測所コード, 列名, 値の項目名)
#   種別 stg  = 水位(単位 m、琵琶湖基準水位 B.S.L からの差)
#   種別 qwtr = 水質(wtrtmp が水温 ℃)
# 放水量は、データの場所がわかったらここに1行足す。
STATIONS = [
    ("雄琴沖", "stg", "2203900400009", "level", "stg"),   # 取得を確認済み
    ("鳥居川", "stg", "2203900400003", "level", "stg"),   # 同じ形式のはず(未確認)
    ("琵琶湖(平均)", "stg", "2203900400025", "level", "stg"),  # 同上(未確認)
    ("雄琴沖", "qwtr", "2203900600002", "temp", "wtrtmp"),     # 取得を確認済み(雄琴沖中央)
    ("唐橋(瀬田川)", "qwtr", "2203900600001", "temp", "wtrtmp"),  # 同じ形式のはず(未確認)
    ("安曇川沖", "qwtr", "2203900600006", "temp", "wtrtmp"),   # 安曇川沖中央。観測所は確認済み
]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "biwako-fishing-collector/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def station_url(kind, code):
    now = get_json(f"{BASE}/system/tmCrntTime.json")["crntObsTime"]  # "2026/11/06 21:00"
    d, t = now.split(" ")
    return f"{BASE}/files/tmlist/{kind}/{d.replace('/', '')}/{t.replace(':', '')}/{code}.json"


def to_iso(s):  # "2026/11/06 21:00" -> "2026-11-06T21:00"
    return s.replace("/", "-").replace(" ", "T")


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--dump":
        data = get_json(station_url(sys.argv[2], sys.argv[3]))
        print(json.dumps(data.get("obsValue"), ensure_ascii=False, indent=2))
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if OUT.exists():
        with OUT.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                seen.add((r["time"], r["place"], "level" if r["level"] else "flow" if r["flow"] else "temp"))

    rows = []
    for place, kind, code, col, field in STATIONS:
        try:
            data = get_json(station_url(kind, code))
            # 毎時の値(過去2日ぶん)を取り込む。取りこぼしがあっても次回に補われる。
            for v in data.get("hrValues", []):
                if v.get(field) is None:
                    continue
                t = to_iso(v["obsTime"])
                if (t, place, col) in seen:
                    continue
                row = {"time": t, "place": place, "level": "", "flow": "", "temp": ""}
                row[col] = v[field]
                rows.append(row)
                seen.add((t, place, col))
        except Exception as e:  # 1地点の失敗で全体を止めない
            print(f"取得失敗: {place}: {e}", file=sys.stderr)

    rows.sort(key=lambda r: r["time"])
    new_file = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        if new_file:
            w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} 行を追記しました")


if __name__ == "__main__":
    main()
