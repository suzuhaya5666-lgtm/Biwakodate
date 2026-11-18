import subprocess,re
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","25","-A","Mozilla/5.0","-w","\n#HTTP %{http_code} %{size_download}","-o","/tmp/o.bin",u],capture_output=True,text=True)
    b=open("/tmp/o.bin","rb").read().decode("utf-8","ignore");print("GET",u,r.stdout.strip()[-30:],r.stderr[:80]);return b
b=get("https://www.river.go.jp/kawabou/pcfull/tm?zm=10&clat=35.95&clon=140.35&elmt=Water&rf=1&suiikey=&rvrkey=&obsrvId=")
print(b[:300].replace("\n"," "))
js=set(re.findall(r'["\']([^"\']+\.js[^"\']*)["\']',b));print(js)
for m in set(re.findall(r'["\']([^"\']*file/[^"\']*)["\']',b)):print("FILE",m)
for u in sorted(js)[:12]:
    if not u.startswith("http"):u="https://www.river.go.jp"+(u if u.startswith("/") else "/kawabou/pcfull/"+u)
    s=get(u)
    for m in sorted(set(re.findall(r'["\'`]([^"\'`\s]*(?:files?|tmlist|master|obs)[^"\'`\s]*\.json[^"\'`\s]*)["\'`]',s)))[:15]:print("  JSONREF",m)
