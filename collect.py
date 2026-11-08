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
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://www.river.go.jp/kawabou/file"
OUT = Path("data/observations.csv")
HEADER = ["time", "place", "level", "flow", "temp"]

# (地点名, 種別, 観測所コード, 列名, 値の項目名)
#   種別 stg  = 水位(単位 m、琵琶湖基準水位 B.S.L からの差)
#   種別 qwtr = 水質(wtrtmp が水温 ℃)
# 放水量・安曇川沖の水温は、データの場所がわかったらここに1行ずつ足す。
STATIONS = [
    ("雄琴沖", "stg", "2203900400009", "level", "stg"),   # 取得を確認済み
    ("鳥居川", "stg", "2203900400003", "level", "stg"),   # 同じ形式のはず(未確認)
    ("琵琶湖(平均)", "stg", "2203900400025", "level", "stg"),  # 同上(未確認)
    ("雄琴沖", "qwtr", "2203900600002", "temp", "wtrtmp"),     # 取得を確認済み(雄琴沖中央)
    ("唐橋(瀬田川)", "qwtr", "2203900600001", "temp", "wtrtmp"),  # 同じ形式のはず(未確認)
    ("安曇川沖", "qwtr", "2203900600006", "temp", "wtrtmp"),   # 安曇川沖中央。観測所は確認済み
]


# 天気の記録(日ごとの天気コード・降水量の合計など)。出典: Open-Meteo
W_OUT = Path("data/weather_daily.csv")
W_HEAD = ["date", "place", "code", "precip", "wmax", "tmax", "tmin"]
W_PLACES = [("海津大崎", 35.435, 136.045), ("安曇川町", 35.32, 136.02), ("彦根市", 35.275, 136.22), ("沖島", 35.2, 136.08),
            ("志賀", 35.17, 135.925), ("烏丸半島", 35.045, 135.945), ("唐崎", 35.035, 135.91), ("膳所", 34.995, 135.905)]
W_VARS = "weather_code,precipitation_sum,wind_speed_10m_max,temperature_2m_max,temperature_2m_min"


def collect_weather():
    """日ごとの天気を data/weather_daily.csv にためる。
    毎回、直近3日ぶんを取り直して上書きする(その日の最終値に確定していく)。
    ファイルが新しいときは、過去90日ぶんも一度にさかのぼって取り込む。"""
    rows = {}
    if W_OUT.exists():
        with W_OUT.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows[(r["date"], r["place"])] = r
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).date()
    lat = ",".join(str(p[1]) for p in W_PLACES)
    lon = ",".join(str(p[2]) for p in W_PLACES)
    common = f"latitude={lat}&longitude={lon}&daily={W_VARS}&timezone=Asia%2FTokyo&wind_speed_unit=ms"
    urls = []
    if len({d for d, _ in rows}) < 30:  # 初回は過去にさかのぼる(確定値・数日おくれ)
        a, b = today - timedelta(days=90), today - timedelta(days=3)
        urls.append(f"https://archive-api.open-meteo.com/v1/archive?{common}&start_date={a}&end_date={b}")
    urls.append(f"https://api.open-meteo.com/v1/forecast?{common}&past_days=2&forecast_days=1")  # 後のものが優先
    for u in urls:
        try:
            data = get_json(u)
            data = data if isinstance(data, list) else [data]
            for (place, _, _), loc in zip(W_PLACES, data):
                d = loc["daily"]
                for k, day in enumerate(d["time"]):
                    code = d["weather_code"][k]
                    pr = d["precipitation_sum"][k]
                    if code is None and pr is None:
                        continue
                    g = lambda key: "" if d[key][k] is None else d[key][k]
                    rows[(day, place)] = {"date": day, "place": place, "code": g("weather_code"), "precip": g("precipitation_sum"),
                                          "wmax": g("wind_speed_10m_max"), "tmax": g("temperature_2m_max"), "tmin": g("temperature_2m_min")}
        except Exception as e:  # 失敗しても水温の取得は止めない
            print(f"天気の取得失敗: {e}", file=sys.stderr)
    if not rows:
        return
    W_OUT.parent.mkdir(parents=True, exist_ok=True)
    with W_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=W_HEAD)
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])
    print(f"天気: {len(rows)} 行(日×地点)")


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
    try:
        collect_weather()
    except Exception as e:
        print(f"天気の記録に失敗: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
