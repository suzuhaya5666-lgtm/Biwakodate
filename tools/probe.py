import subprocess,re
def get(u):
    r=subprocess.run(["curl","-sS","-L","-m","30","-A","Mozilla/5.0","-o","/tmp/o.bin",u],capture_output=True,text=True)
    b=open("/tmp/o.bin","rb").read().decode("utf-8","ignore");print("GET",u[:100],len(b),r.stderr[:80]);return b
b=get("https://www.river.go.jp/kawabou/pcfull/tm?zm=10&clat=35.95&clon=140.35&elmt=Water&rf=1")
srcs=sorted(set(re.findall(r'src=([^\s>]+\.js[^\s>]*)',b)));print(srcs)
for u in srcs:
    if u.startswith("http"):continue
    if not u.startswith("/"):u="/kawabou/pcfull/"+u
    s=get("https://www.river.go.jp"+u)
    for m in sorted(set(re.findall(r'[\w/\.\-\$\{\}\+ \']*(?:file/|\.json)[\w/\.\-\$\{\}\+\' ]*',s)))[:40]:print("  REF",m[:140])
