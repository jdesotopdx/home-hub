import json
from PIL import Image, ImageDraw, ImageFont
D=json.load(open("data.json"))
W,H=1236,1648
F="/usr/share/fonts/truetype/dejavu/"
f=lambda n,s: ImageFont.truetype(F+n,s)
S=lambda s:f("DejaVuSans.ttf",s); B=lambda s:f("DejaVuSans-Bold.ttf",s)
SB=lambda s:f("DejaVuSerif-Bold.ttf",s); SI=lambda s:f("DejaVuSerif-Italic.ttf",s)
im=Image.new("L",(W,H),255); d=ImageDraw.Draw(im); M=60
def wrap(t,font,w):
    out=[];cur=""
    for word in t.split():
        x=(cur+" "+word).strip()
        if d.textlength(x,font=font)<=w: cur=x
        else: out.append(cur);cur=word
    out.append(cur);return out
def box(x0,y0,x1,y1,wd=3,r=18): d.rounded_rectangle((x0,y0,x1,y1),radius=r,outline=0,width=wd)
w=D["weather"]
d.text((M,50),"Home Base",font=B(34),fill=0)
d.text((W-M,54),D["date"],font=S(30),fill=0,anchor="ra")
d.text((M,120),D["greeting"],font=SB(54),fill=0)
d.text((M,186),"Johnathon and Bee",font=SB(54),fill=0)
y=290; box(M,y,W-M,y+190)
d.text((M+36,y+22),w["temp"]+"°",font=B(120),fill=0)
d.text((M+330,y+40),w["cond"],font=B(42),fill=0)
d.text((M+330,y+100),f'High {w["high"]}   Low {w["low"]}   Rain {w["rain"]}%',font=S(34),fill=0)
d.text((M+330,y+146),"Portland",font=S(26),fill=110)
y=510; cw=(W-2*M-30)//2
for i,(nm,items) in enumerate([("Johnathon today",D["j"]),("Bee today",D["b"])]):
    x=M+i*(cw+30); box(x,y,x+cw,y+250)
    d.text((x+28,y+20),nm,font=B(34),fill=0)
    for k,t in enumerate(items[:3]):
        yy=y+86+k*52
        d.rectangle((x+28,yy+6,x+52,yy+30),outline=0,width=3)
        d.text((x+68,yy),t,font=S(29),fill=0)
y=790; tw=(W-2*M-4*14)//5
for i,(dn,hi,lo) in enumerate(D["days"]):
    x=M+i*(tw+14)
    if i==0: d.rounded_rectangle((x,y,x+tw,y+170),radius=16,fill=0); c=255
    else: box(x,y,x+tw,y+170,r=16); c=0
    d.text((x+tw//2,y+18),dn,font=B(28),fill=c,anchor="ma")
    d.text((x+tw//2,y+62),hi+"°",font=B(60),fill=c,anchor="ma")
    d.text((x+tw//2,y+130),lo+"°",font=S(30),fill=c if i==0 else 90,anchor="ma")
y=980; d.text((M,y),"Coming up",font=B(34),fill=0)
for i,(n,u,t,when) in enumerate(D["events"][:2]):
    yy=y+56+i*118; box(M,yy,W-M,yy+104,r=16)
    d.rounded_rectangle((M,yy,M+170,yy+104),radius=16,fill=0)
    d.text((M+85,yy+10),n,font=B(52),fill=255,anchor="ma"); d.text((M+85,yy+68),u,font=S(26),fill=255,anchor="ma")
    ft=S(32)
    while d.textlength(t,font=ft)>W-2*M-170-50: ft=S(ft.size-2)
    d.text((M+200,yy+16),t,font=ft,fill=0); d.text((M+200,yy+60),when,font=S(28),fill=90)
y=1282; box(M,y,W-M,H-40,wd=4,r=22)
yy=y+34
for l in wrap("“"+D["quote"]+"”",SB(40),W-2*M-80): d.text((W//2,yy),l,font=SB(40),fill=0,anchor="ma"); yy+=52
d.text((W//2,yy+6),D["author"],font=SI(30),fill=0,anchor="ma")
d.line((M+40,yy+54,W-M-40,yy+54),fill=0,width=2)
d.text((W//2,yy+72),"Ask each other",font=B(28),fill=0,anchor="ma")
for k,l in enumerate(wrap(D["question"],SB(38),W-2*M-80)): d.text((W//2,yy+112+k*48),l,font=SB(38),fill=0,anchor="ma")
im.save("dashboard.png",optimize=True)
