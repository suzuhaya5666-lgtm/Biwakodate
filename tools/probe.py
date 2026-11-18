import subprocess,re,json
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","60","-A","Mozilla/5.0","-o","/tmp/o.bin","-w","%{http_code}",u],capture_output=True,text=True)
    return r.stdout,open("/tmp/o.bin","rb").read().decode("utf-8","ignore")
c,b=get("https://www.river.go.jp/kawabou/file/system/tmCrntTime.json");t=json.loads(b)["crntObsTime"];d,hm=t.split(" ");print("now",t)
def show(kind,code,name):
    c,b=get(f"https://www.river.go.jp/kawabou/file/files/tmlist/{kind}/{d.replace('/','')}/{hm.replace(':','')}/{code}.json")
    try:
        j=json.loads(b)
    except Exception as e:print(name,kind,code,c,"ERR",b[:100]);return
    def find(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if isinstance(v,list) and v and isinstance(v[0],dict):return v
                r=find(v)
                if r:return r
    arr=find(j) or []
    print(name,kind,code,c,"n=",len(arr),"keys=",list(arr[-1].keys()) if arr else list(j.keys()))
    for x in arr[-2:]:print("   ",json.dumps(x,ensure_ascii=False)[:300])
for code,n in (("2127000600004","湖心自動"),("2127000600005","平山自動"),("2127000600006","麻生沖自動"),("2127000600016","掛馬沖自動"),("2127000600008","安塚自動"),("2127000600017","釜谷沖自動"),("2127000600009","潮来自動"),("2127000600015","波崎下流下層"),("2127000600013","波崎下流上層"),("2127000600010","波崎上流上層")):show("qwtr",code,n)
for code,n in (("2127000400013","出島"),("2127000400023","白浜"),("2127000400005","波崎上"),("2127000400006","波崎下"),("2127000400025","潮来")):show("stg",code,n)
