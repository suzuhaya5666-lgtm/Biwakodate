import subprocess,json,os
b="https://www.jma.go.jp/bosai/jmatile/data/nowc/"
def get(u,o="/tmp/x"):
    subprocess.run(["curl","-sS","-m","20","-o",o,u]);return o
j=json.load(open(get(b+"targetTimes_N1.json")))
print("latest",j[0]["validtime"],"oldest",j[-1]["validtime"],len(j))
for k in (0,6,12,24,36):
    t=j[k];out=[]
    for x in (449,450):
        for y in (202,203):
            get(f"{b}{t['basetime']}/none/{t['validtime']}/surf/hrpns/9/{x}/{y}.png","/tmp/t.png");out.append((x,y,os.path.getsize("/tmp/t.png")))
    print(t["validtime"],out)
