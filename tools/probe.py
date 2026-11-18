import subprocess,re
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","60","-A","Mozilla/5.0","-o","/tmp/o.bin",u],capture_output=True,text=True)
    b=open("/tmp/o.bin","rb").read().decode("utf-8","ignore");print("GET",u[:110],len(b),r.stderr[:80]);return b
s=get("https://www.river.go.jp/kawabou/js/app.4d7d8c61.js")
seen=set()
for key in ("master/obs","master/sect","files/map","/obs/","tmlist","stg","qwtr"):
    for m in re.finditer(re.escape(key),s):
        c=s[max(0,m.start()-90):m.end()+110].replace("\n"," ")
        k=c[60:130]
        if k in seen:continue
        seen.add(k);print(key,"::",c);
        if len([x for x in seen])>60:break
