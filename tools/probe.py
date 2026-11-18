import subprocess
b="https://www.jma.go.jp/bosai/jmatile/data/nowc/"
r=subprocess.run(["curl","-sS","-m","20","-D","-","-H","Origin: https://suzuhaya5666-lgtm.github.io",b+"targetTimes_N1.json"],capture_output=True,text=True)
print(r.stdout[:1200],r.stderr[:200])
import json,re
body=r.stdout.split("\r\n\r\n",1)[-1]
try:
    j=json.loads(body);print(j[:3],len(j));t=j[0]
    u=f"{b}{t['basetime']}/none/{t['validtime']}/surf/hrpns/9/{ (135.9+180)/360*512:.0f}/0.png"
except Exception as e:print("ERR",e)
import math
z=9;lat,lon=35.25,136.05
x=int((lon+180)/360*2**z);y=int((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*2**z);print("tile",z,x,y)
u=f"{b}{t['basetime']}/none/{t['validtime']}/surf/hrpns/{z}/{x}/{y}.png"
r=subprocess.run(["curl","-sS","-m","20","-D","-","-o","/tmp/t.png","-H","Origin: https://suzuhaya5666-lgtm.github.io",u],capture_output=True,text=True);print(r.stdout[:600])
import os;print(os.path.getsize("/tmp/t.png"))
