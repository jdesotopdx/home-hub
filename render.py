import json, os, datetime
from zoneinfo import ZoneInfo
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
# date sits low so the Kindle status bar clock never covers it
d.text((M,96),D["date"],font=SB(50),fill=0)
# weather
y=176; box(M,y,W-M,y+160)
d.text((M+36,y+14),w["temp"]+"°",font=B(104),fill=0)
d.text((M+330,y+28),w["cond"],font=B(40),fill=0)
d.text((M+330,y+82),f'High {w["high"]}   Low {w["low"]}   Rain {w["rain"]}%',font=S(32),fill=0)
d.text((M+330,y+122),"Portland",font=S(24),fill=110)
# forecast
y=356; tw=(W-2*M-4*14)//5
for i,(dn,hi,lo) in enumerate(D["days"]):
    x=M+i*(tw+14)
    if i==0: d.rounded_rectangle((x,y,x+tw,y+136),radius=16,fill=0); c=255
    else: box(x,y,x+tw,y+136,r=16); c=0
    d.text((x+tw//2,y+10),dn,font=B(24),fill=c,anchor="ma")
    d.text((x+tw//2,y+44),hi+"°",font=B(52),fill=c,anchor="ma")
    d.text((x+tw//2,y+100),lo+"°",font=S(28),fill=c if i==0 else 90,anchor="ma")
# photo of the day (4:5) on the left, five day agenda cards on the right
py=514; pw,ph=560,700
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
cx=M+pw+30 if p else M
def agenda_rows():
    # five days starting today (Pacific). Uses D["agenda"] when present, else the events list.
    now=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).date()
    days=[now+datetime.timedelta(days=i) for i in range(5)]
    labels=["TODAY"]+[x.strftime("%a").upper()+" "+str(x.day) for x in days[1:]]
    evs=[[] for _ in range(5)]
    if "agenda" in D:
        for lab,items in D["agenda"][:5]:
            tok=lab.split()[0].upper()
            for i in range(5):
                if (i==0 and tok=="TODAY") or (i>0 and tok==days[i].strftime("%a").upper()): evs[i]=[list(e) for e in items]
    else:
        for e in D.get("events",[]):
            parts=e[3].split(" ",1); tok=parts[0].upper(); rest=parts[1] if len(parts)>1 else ""
            for i in range(5):
                if (i==0 and tok=="TODAY") or (i>0 and tok==days[i].strftime("%a").upper()): evs[i].append([rest,e[2]]); break
    return list(zip(labels,evs))
rows=agenda_rows()
gap=12; ch=(ph-gap*4)//5
for i,(label,evs) in enumerate(rows):
    yy=py+i*(ch+gap); dark=(i==0)
    if dark: d.rounded_rectangle((cx,yy,W-M,yy+ch),radius=18,fill=0)
    else: box(cx,yy,W-M,yy+ch)
    fg=255 if dark else 0; mut=210 if dark else 110
    px=cx+22
    d.text((px,yy+14),label,font=B(26),fill=fg)
    if not evs:
        d.text((px,yy+56),"Nothing planned",font=S(24),fill=150); continue
    shown=evs[:2]; maxl=2 if len(evs)==1 else 1
    ey=yy+54
    for when,title in shown:
        tf=S(22); tw_=d.textlength(when,font=tf) if when else 0
        d.text((px,ey+4),when,font=tf,fill=mut)
        x0=px+tw_+(12 if when else 0); avail=W-M-22-x0; ft=S(26)
        ls=wrap(title,ft,avail)
        if len(ls)>maxl:
            t=title
            while len(wrap(t,ft,avail))>maxl and len(t)>4: t=t[:-4].rstrip()+"..."
            ls=wrap(t,ft,avail)[:maxl]
        for l in ls: d.text((x0,ey),l,font=ft,fill=fg); ey+=32
        ey+=2
# quote and question, content centred in the box
y=py+ph+26; y1=H-30
box(M,y,W-M,y1,wd=4,r=22)
ql=wrap("“"+D["quote"]+"”",SB(40),W-2*M-80); qul=wrap(D["question"],SB(38),W-2*M-80)
total=len(ql)*52+38+30+34+len(qul)*48
yy=y+(y1-y-total)//2
for l in ql: d.text((W//2,yy),l,font=SB(40),fill=0,anchor="ma"); yy+=52
d.text((W//2,yy),D["author"],font=SI(28),fill=0,anchor="ma"); yy+=38
d.line((M+40,yy+8,W-M-40,yy+8),fill=0,width=2); yy+=30
d.text((W//2,yy),"Ask each other",font=B(26),fill=0,anchor="ma"); yy+=40
for l in qul: d.text((W//2,yy),l,font=SB(38),fill=0,anchor="ma"); yy+=48
im.save("dashboard.png",optimize=True)
