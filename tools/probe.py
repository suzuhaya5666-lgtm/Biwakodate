import subprocess,re,json
F="https://www.river.go.jp/kawabou/file/files/"
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","60","-A","Mozilla/5.0","-o","/tmp/o.bin","-w","%{http_code}",u],capture_output=True,text=True)
    b=open("/tmp/o.bin","rb").read().decode("utf-8","ignore");print("GET",u[-80:],r.stdout,len(b));return b
for rv in ("83028008","83028958","83028016","83028108"):
    b=get(F+f"obslist/obs/rvrlist/{rv}.json")
    print(b[:200].replace("\n"," "))
    try:
        j=json.loads(b)
        def walk(o):
            if isinstance(o,dict):
                if "obsFcd" in o:print("  OBS",{k:o.get(k) for k in ("obsKnd","itmkndCd","obsFcd","obsNm","rvrNm","kpExpl") if k in o})
                for v in o.values():walk(v)
            elif isinstance(o,list):
                for v in o:walk(v)
        walk(j)
    except Exception as e:print("ERR",e)
# current time and data for 出島
t=json.loads(get("https://www.river.go.jp/kawabou/file/system/tmCrntTime.json"))["crntObsTime"];d,hm=t.split(" ")
for kind,code in (("stg","2127000400013"),("stg","2127000400023")):
    print(get(f"https://www.river.go.jp/kawabou/file/files/tmlist/{kind}/{d.replace('/','')}/{hm.replace(':','')}/{code}.json")[:500].replace("\n"," "))
