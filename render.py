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
# photo of the day (4:5) on the left, five day outlook on the right
py=462; pw,ph=640,800
import base64, io
def load_photo(path):
    try:
        if path.lower().endswith(".b64"):
            raw=base64.b64decode("".join(open(path).read().split()))
            im0=Image.open(io.BytesIO(raw)); im0.load()
            return ImageOps.exif_transpose(im0)
        im0=Image.open(path); im0.load()
        return ImageOps.exif_transpose(im0)
    except Exception:
        return None
def pick():
    exts=(".jpg",".jpeg",".png",".jpg.b64",".jpeg.b64",".png.b64")
    fs=sorted(x for x in os.listdir("photos") if x.lower().endswith(exts)) if os.path.isdir("photos") else []
    if not fs: return None
    start=datetime.date.today().toordinal()%len(fs)
    for k in range(len(fs)):
        pi=load_photo(os.path.join("photos",fs[(start+k)%len(fs)]))
        if pi is not None: return pi
    return None
pi=pick(); p=pi is not None
if p:
    pi=pi.convert("L")
    pi=ImageOps.autocontrast(ImageOps.fit(pi,(pw,ph),Image.LANCZOS,centering=(0.5,0.4)),cutoff=1)
    mask=Image.new("L",(pw,ph),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,pw-1,ph-1),radius=18,fill=255)
    im.paste(pi,(M,py),mask); box(M,py,M+pw,py+ph)
cx=M+pw+24 if p else M
def agenda_rows():
    if "agenda" in D: return D["agenda"][:5]
    # fallback for the older events format: [count, unit, title, when]
    return [[e[3].split(" ")[0] if i else "TODAY",[[" ".join(e[3].split(" ")[1:]),e[2]]]] for i,e in enumerate(D.get("events",[])[:5])]
rows=agenda_rows()
rh=ph//max(len(rows),1)
for i,(label,evs) in enumerate(rows):
    yy=py+i*rh
    if i: d.line((cx,yy,W-M,yy),fill=170,width=2)
    lf=B(26); lw=d.textlength(label,font=lf)+28
    if i==0:
        d.rounded_rectangle((cx,yy+12,cx+lw,yy+50),radius=10,fill=0); d.text((cx+14,yy+17),label,font=lf,fill=255)
    else: d.text((cx,yy+17),label,font=lf,fill=0)
    if not evs:
        d.text((cx,yy+64),"Nothing on the calendar",font=S(24),fill=150); continue
    maxl=2 if len(evs)<=2 else 1
    ey=yy+62
    for k,(when,title) in enumerate(evs[:3]):
        tf=S(22); tw_=d.textlength(when,font=tf) if when else 0
        d.text((cx,ey+4),when,font=tf,fill=110)
        x0=cx+tw_+(12 if when else 0); avail=W-M-x0; ft=S(27)
        ls=wrap(title,ft,avail)
        if len(ls)>maxl:
            t=title
            while len(wrap(t,ft,avail))>maxl and len(t)>4: t=t[:-4].rstrip()+"..."
            ls=wrap(t,ft,avail)[:maxl]
        for l in ls: d.text((x0,ey),l,font=ft,fill=0); ey+=34
        ey+=2
# quote and question
y=py+ph+24
box(M,y,W-M,H-30,wd=4,r=22)
yy=y+26
for l in wrap("“"+D["quote"]+"”",SB(36),W-2*M-80): d.text((W//2,yy),l,font=SB(36),fill=0,anchor="ma"); yy+=46
d.text((W//2,yy+2),D["author"],font=SI(28),fill=0,anchor="ma")
d.line((M+40,yy+44,W-M-40,yy+44),fill=0,width=2)
d.text((W//2,yy+58),"Ask each other",font=B(26),fill=0,anchor="ma")
for k,l in enumerate(wrap(D["question"],SB(34),W-2*M-80)): d.text((W//2,yy+98+k*44),l,font=SB(34),fill=0,anchor="ma")
im.save("dashboard.png",optimize=True)
