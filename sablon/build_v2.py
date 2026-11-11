"""Carousel şablonu v2 (11 Kasım 2026).
Kullanım: python3 build_v2.py icerik.json cikti_klasoru [slayt_no]
icerik.json:
{"theme":"petrol"|"firtina",
 "slides":[
  {"label":"…","stat":"10'da 6","stat_note":"kısa açıklama","text":"… <b>vurgu</b> …"},   # kapak (rakamlı)
  {"label":"…","text":"… <b>vurgu</b> …"},                                               # normal slayt
  {"label":"…","title":"Hangi durumda muayene?","items":["…","…","…"]},                  # liste slaytı
  {"label":"Sonuç","text":"…","share":"Dizi ağrıyan birine gönderin"}                     # son slayt
 ]}
Görsel (opsiyonel, yalnız Kage'nin kendi fotoğrafı): "photo":"dosya.jpg" -> slaytın sağ altına yerleşir.
"""
import sys, json, asyncio, base64, os, mimetypes
from playwright.async_api import async_playwright

SERIF = "'Liberation Serif','Times New Roman','DejaVu Serif',serif"
SANS = "'Carlito','DejaVu Sans',sans-serif"
THEMES = {
    "petrol":  {"bg": "radial-gradient(circle at 80% 15%,#2C6E9E 0,#13697A 45%,#0A3A4E 100%)", "acc": "#FFD23F", "sub": "#BFE3EE"},
    "firtina": {"bg": "radial-gradient(circle at 80% 15%,#4A5568 0,#2D3748 45%,#151A23 100%)", "acc": "#FF7A59", "sub": "#CBD5E0"},
}
HERE = os.path.dirname(os.path.abspath(__file__))


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


FOTO = b64(os.path.join(HERE, 'foto_yuvarlak.png'))
LOGO = b64(os.path.join(HERE, 'logo.png'))

BOOKMARK = '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-5-7 5V4a1 1 0 0 1 1-1z"/></svg>'
PLANE = '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M22 3 9.2 10.1"/><path d="M22 3 15 21l-3.8-7.9L3 9.5z"/></svg>'


def photo_tag(s, spec_dir):
    p = s.get("photo")
    if not p:
        return ""
    path = p if os.path.isabs(p) else os.path.join(spec_dir, p)
    mt = mimetypes.guess_type(path)[0] or "image/jpeg"
    return f'<img class="ph" src="data:{mt};base64,{b64(path)}">'


def slide_html(i, n, s, th, spec_dir):
    acc, sub = th["acc"], th["sub"]
    last = (i == n)
    pct = int(100 * i / n)
    label = s.get("label", "")
    has_photo = bool(s.get("photo"))

    if "stat" in s:  # rakamlı kapak
        body = f'''<div class="stat">{s["stat"]}</div>
<div class="statnote">{s.get("stat_note","")}</div>
<div class="txt cover">{s.get("text","")}</div>'''
        block = f'<div class="blk col">{body}</div>'
    elif "items" in s:  # liste slaytı
        lis = "".join(f'<li><span class="num">{k}</span><span>{t}</span></li>' for k, t in enumerate(s["items"], 1))
        block = f'<div class="blk col"><div class="ltitle">{s.get("title","")}</div><ul>{lis}</ul></div>'
    else:
        big = s.get("big", False)
        block = f'<div class="blk"><div class="bar"></div><div class="txt" style="font-size:{96 if big else 66}px">{s["text"]}</div></div>'

    cta = ""
    if last:
        share = s.get("share", "")
        cta = f'''<div class="cta"><div class="ic">{BOOKMARK.format(c=acc)}<span>Kaydet</span></div>
<div class="ic">{PLANE.format(c=acc)}<span>Gönder</span></div></div>
{f'<div class="shareline">{share}</div>' if share else ''}'''

    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:{SERIF};color:#fff;background:{th["bg"]};position:relative;overflow:hidden}}
.top{{position:absolute;left:90px;top:80px;display:flex;align-items:center;gap:26px}}
.av{{width:124px;height:124px;border-radius:50%}}
.nm{{font-size:46px;font-weight:700;line-height:1.1}}
.hd{{font-family:{SANS};font-size:30px;color:{sub};margin-top:6px}}
.tcnt{{position:absolute;right:90px;top:96px;font-family:{SANS};font-weight:700;font-size:28px;letter-spacing:3px}}
.label{{position:absolute;left:90px;top:262px;font-family:{SANS};font-weight:700;letter-spacing:5px;font-size:28px;color:{acc};text-transform:uppercase}}
.blk{{position:absolute;left:90px;right:{'430px' if has_photo else '90px'};top:330px;bottom:{'360px' if last else '290px'};display:flex;align-items:center}}
.blk.col{{flex-direction:column;align-items:flex-start;justify-content:center}}
.bar{{width:8px;align-self:stretch;background:{acc};margin-right:44px;border-radius:2px}}
.txt{{font-weight:700;line-height:1.16;letter-spacing:-.5px}}
.txt b,.ltitle b,li b{{color:{acc};font-weight:700}}
.stat{{font-size:230px;font-weight:700;line-height:.95;color:{acc};letter-spacing:-6px}}
.statnote{{font-family:{SANS};font-size:36px;color:{sub};margin:18px 0 44px;max-width:860px;line-height:1.25}}
.txt.cover{{font-size:74px}}
.ltitle{{font-size:66px;font-weight:700;line-height:1.12;margin-bottom:44px}}
ul{{list-style:none;display:flex;flex-direction:column;gap:30px}}
li{{display:flex;gap:28px;align-items:flex-start;font-family:{SANS};font-size:44px;line-height:1.25}}
.num{{flex:0 0 64px;height:64px;border-radius:50%;border:3px solid {acc};color:{acc};font-weight:700;display:flex;align-items:center;justify-content:center;font-size:34px}}
.ph{{position:absolute;right:60px;bottom:220px;width:340px;height:440px;object-fit:cover;border-radius:28px;box-shadow:0 18px 40px rgba(0,0,0,.35)}}
.foot{{position:absolute;left:90px;right:90px;bottom:62px;display:flex;align-items:center;gap:26px;font-family:{SANS}}}
.logo{{width:118px;height:118px}}
.track{{flex:1;height:8px;background:rgba(255,255,255,.22);border-radius:4px;position:relative}}
.fill{{position:absolute;left:0;top:0;bottom:0;width:{pct}%;background:{acc};border-radius:4px}}
.dot{{position:absolute;left:{pct}%;top:50%;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:{acc}}}
.kaydir{{font-weight:700;font-size:30px;letter-spacing:2px}}
.cta{{position:absolute;left:90px;bottom:250px;display:flex;gap:56px;font-family:{SANS};font-weight:700;font-size:50px}}
.ic{{display:flex;align-items:center;gap:18px}}
.shareline{{position:absolute;left:90px;bottom:200px;font-family:{SANS};font-size:34px;color:{sub}}}
</style></head><body>
<div class="top"><img class="av" src="data:image/png;base64,{FOTO}"><div><div class="nm">Uzm. Dr. Kadir Güler</div><div class="hd">Fiziksel Tıp ve Rehabilitasyon</div></div></div>
<div class="tcnt">{i:02d} / {n:02d}</div>
<div class="label">{label}</div>
{block}
{photo_tag(s, spec_dir)}
{cta}
<div class="foot"><img class="logo" src="data:image/png;base64,{LOGO}"><div class="track"><div class="fill"></div><div class="dot"></div></div>{'' if last else '<div class="kaydir">KAYDIR →</div>'}</div>
</body></html>"""


async def main(spec_path, outdir, only=None):
    spec = json.load(open(spec_path, encoding="utf-8"))
    th = THEMES[spec.get("theme", "petrol")]
    slides = spec["slides"]
    n = len(slides)
    spec_dir = os.path.dirname(os.path.abspath(spec_path))
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            if only and i != only:
                continue
            await pg.set_content(slide_html(i, n, s, th, spec_dir))
            await pg.screenshot(path=f"{outdir}/slayt-{i:02d}.png")
        await b.close()

asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None))
