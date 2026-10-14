import json, os, datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
d.text((M,44),D["date"],font=SB(50),fill=0)
# weather
y=124; box(M,y,W-M,y+160)
d.text((M+36,y+14),w["temp"]+"°",font=B(104),fill=0)
d.text((M+330,y+28),w["cond"],font=B(40),fill=0)
d.text((M+330,y+82),f'High {w["high"]}   Low {w["low"]}   Rain {w["rain"]}%',font=S(32),fill=0)
d.text((M+330,y+122),"Portland",font=S(24),fill=110)
# forecast
y=304; tw=(W-2*M-4*14)//5
for i,(dn,hi,lo) in enumerate(D["days"]):
    x=M+i*(tw+14)
    if i==0: d.rounded_rectangle((x,y,x+tw,y+136),radius=16,fill=0); c=255
    else: box(x,y,x+tw,y+136,r=16); c=0
    d.text((x+tw//2,y+10),dn,font=B(24),fill=c,anchor="ma")
    d.text((x+tw//2,y+44),hi+"°",font=B(52),fill=c,anchor="ma")
    d.text((x+tw//2,y+100),lo+"°",font=S(28),fill=c if i==0 else 90,anchor="ma")
# photo (4:5) + coming up column
py=462; pw,ph=640,800
def pick():
    fs=sorted(x for x in os.listdir("photos") if x.lower().endswith((".jpg",".jpeg",".png"))) if os.path.isdir("photos") else []
    return os.path.join("photos",fs[datetime.date.today().toordinal()%len(fs)]) if fs else None
p=pick()
if p:
    pi=ImageOps.exif_transpose(Image.open(p)).convert("L")
    pi=ImageOps.autocontrast(ImageOps.fit(pi,(pw,ph),Image.LANCZOS,centering=(0.5,0.4)),cutoff=1)
    mask=Image.new("L",(pw,ph),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,pw-1,ph-1),radius=18,fill=255)
    im.paste(pi,(M,py),mask); box(M,py,M+pw,py+ph)
cx=M+pw+24 if p else M
cwid=W-M-cx
d.text((cx,py-2),"Coming up",font=B(32),fill=0)
ev=D["events"][:2]; top=py+50; ch=(ph-50-20)//2
for i,(n,u,t,when) in enumerate(ev):
    yy=top+i*(ch+20)
    box(cx,yy,cx+cwid,yy+ch,r=16)
    d.rounded_rectangle((cx,yy,cx+cwid,yy+78),radius=16,fill=0)
    d.rectangle((cx,yy+40,cx+cwid,yy+78),fill=0)
    d.text((cx+28,yy+8),n,font=B(56),fill=255)
    d.text((cx+28+d.textlength(n,font=B(56))+14,yy+36),u,font=S(28),fill=255)
    ft=S(34); ls=wrap(t,ft,cwid-56)
    for k,l in enumerate(ls[:3]): d.text((cx+28,yy+98+k*46),l,font=ft,fill=0)
    d.text((cx+28,yy+ch-52),when,font=S(30),fill=90)
# quote
y=py+ph+24
box(M,y,W-M,H-30,wd=4,r=22)
yy=y+26
for l in wrap("“"+D["quote"]+"”",SB(36),W-2*M-80): d.text((W//2,yy),l,font=SB(36),fill=0,anchor="ma"); yy+=46
d.text((W//2,yy+2),D["author"],font=SI(28),fill=0,anchor="ma")
d.line((M+40,yy+44,W-M-40,yy+44),fill=0,width=2)
d.text((W//2,yy+58),"Ask each other",font=B(26),fill=0,anchor="ma")
for k,l in enumerate(wrap(D["question"],SB(34),W-2*M-80)): d.text((W//2,yy+98+k*44),l,font=SB(34),fill=0,anchor="ma")
im.save("dashboard.png",optimize=True)
