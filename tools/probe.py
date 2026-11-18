import subprocess,re,json
F="https://www.river.go.jp/kawabou/file/files/"
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","60","-A","Mozilla/5.0","-o","/tmp/o.bin","-w","%{http_code}",u],capture_output=True,text=True)
    b=open("/tmp/o.bin","rb").read().decode("utf-8","ignore");print("GET",u[-90:],r.stdout,len(b));return b
b=get(F+"master/sect/sect-all.json")
print(b[:600])
try:
    j=json.loads(b)
    def walk(o,p=""):
        if isinstance(o,dict):
            if any(isinstance(v,str) and re.search("霞ヶ浦|北浦|常陸利根|外浪逆|鰐川|西浦",v) for v in o.values()):print("HIT",json.dumps(o,ensure_ascii=False)[:300])
            for k,v in o.items():walk(v,p+"/"+k)
        elif isinstance(o,list):
            for v in o:walk(v,p)
    walk(j)
except Exception as e:print("ERR",e)
