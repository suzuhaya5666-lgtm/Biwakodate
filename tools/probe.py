import subprocess,json,math,os
b="https://www.jma.go.jp/bosai/jmatile/data/nowc/"
O="Origin: https://suzuhaya5666-lgtm.github.io"
def get(u,out):
    subprocess.run(["curl","-sS","-m","20","-D","/tmp/h.txt","-o",out,"-H",O,u])
    print(u[-60:],[l.strip() for l in open("/tmp/h.txt") if l.lower().startswith(("http","access-control","content-type"))])
get(b+"targetTimes_N1.json","/tmp/n1.json")
j=json.load(open("/tmp/n1.json"));print(len(j),j[:2],j[-2:])
get(b+"targetTimes_N2.json","/tmp/n2.json")
j2=json.load(open("/tmp/n2.json"));print(len(j2),j2[:2],j2[-2:])
t=j[0]
z=9;lat,lon=35.25,136.05
x=int((lon+180)/360*2**z);y=int((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*2**z);print("tile",z,x,y)
for tt in (t,j2[0]):
    get(f"{b}{tt['basetime']}/{tt['member']}/{tt['validtime']}/surf/hrpns/{z}/{x}/{y}.png","/tmp/t.png");print(os.path.getsize("/tmp/t.png"))
