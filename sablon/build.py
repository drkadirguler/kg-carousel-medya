import sys, json, asyncio, base64
from playwright.async_api import async_playwright
SERIF="'Liberation Serif','Times New Roman','DejaVu Serif',serif"
SANS="'Carlito','DejaVu Sans',sans-serif"
ACC="#FFFFFF"
def b64(f): return base64.b64encode(open(f,'rb').read()).decode()
FOTO=b64('foto_yuvarlak.png'); LOGO=b64('logo.png')

def slide_html(i,n,s):
    last=(i==n); label=s.get("label",""); body=s["text"]; big=s.get("big",False)
    fs=96 if big else 66; pct=int(100*i/n)
    cta='<div class="btn"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-5-7 5V4a1 1 0 0 1 1-1z"/></svg><span>Kaydet</span></div>' if last else ''
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:{SERIF};color:#111;background:radial-gradient(circle at 78% 18%,#FFC27A 0,#F9973F 45%,#EE7424 100%);position:relative;overflow:hidden}}
.top{{position:absolute;left:90px;top:80px;display:flex;align-items:center;gap:26px}}
.av{{width:124px;height:124px;border-radius:50%}}
.nm{{font-size:46px;font-weight:700;line-height:1.1}}
.hd{{font-family:{SANS};font-size:30px;color:#5a250b;margin-top:6px}}
.tcnt{{position:absolute;right:90px;top:96px;font-family:{SANS};font-weight:700;font-size:28px;letter-spacing:3px}}
.label{{position:absolute;left:90px;top:262px;font-family:{SANS};font-weight:700;letter-spacing:5px;font-size:28px;color:#5a1a05;text-transform:uppercase}}
.blk{{position:absolute;left:90px;right:90px;top:330px;bottom:290px;display:flex;align-items:center}}
.bar{{width:8px;align-self:stretch;background:#111;margin-right:44px;border-radius:2px}}
.txt{{font-size:{fs}px;font-weight:700;line-height:1.16;letter-spacing:-.5px}}
.txt b{{color:{ACC};font-weight:700}}
.foot{{position:absolute;left:90px;right:90px;bottom:62px;display:flex;align-items:center;gap:26px;font-family:{SANS}}}
.logo{{width:118px;height:118px}}
.track{{flex:1;height:8px;background:rgba(17,17,17,.22);border-radius:4px;position:relative}}
.fill{{position:absolute;left:0;top:0;bottom:0;width:{pct}%;background:#111;border-radius:4px}}
.dot{{position:absolute;left:{pct}%;top:50%;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:#111}}
.kaydir{{font-weight:700;font-size:30px;letter-spacing:2px}}
.btn{{position:absolute;left:90px;bottom:210px;display:flex;align-items:center;gap:22px;font-family:{SANS};font-weight:700;font-size:54px;color:#111}}
</style></head><body>
<div class="top"><img class="av" src="data:image/png;base64,{FOTO}"><div><div class="nm">Uzm. Dr. Kadir Güler</div><div class="hd">Fiziksel Tıp ve Rehabilitasyon</div></div></div>
<div class="tcnt">{i:02d} / {n:02d}</div>
<div class="label">{label}</div>
<div class="blk"><div class="bar"></div><div class="txt">{body}</div></div>
{cta}
<div class="foot"><img class="logo" src="data:image/png;base64,{LOGO}"><div class="track"><div class="fill"></div><div class="dot"></div></div>{'' if last else '<div class="kaydir">KAYDIR →</div>'}</div>
</body></html>"""

async def main(spec_path,outdir,only=None):
    slides=json.load(open(spec_path,encoding="utf-8"))["slides"]; n=len(slides)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1080,"height":1350})
        for i,s in enumerate(slides,1):
            if only and i!=only: continue
            await pg.set_content(slide_html(i,n,s)); await pg.screenshot(path=f"{outdir}/slayt-{i:02d}.png")
        await b.close()
asyncio.run(main(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else None))
