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


HEART = '<svg width="58" height="58" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"><path d="M12 20s-7-4.4-9.2-8.6C1.3 8.4 3 5 6.4 5c2 0 3.3 1.1 4 2.3h3.2C14.3 6.1 15.6 5 17.6 5 21 5 22.7 8.4 21.2 11.4 19 15.6 12 20 12 20z"/></svg>'
BUBBLE = '<svg width="58" height="58" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"><path d="M20.5 12a8.5 8.5 0 0 1-12.6 7.4L3.5 20.5l1.1-4.2A8.5 8.5 0 1 1 20.5 12z"/></svg>'


PLANE_FILLED = '<svg width="{w}" height="{w}" viewBox="0 0 24 24" fill="{c}" stroke="{c}" stroke-width="1.2" stroke-linejoin="round"><path d="M22 3 15 21l-3.8-7.9L3 9.5z"/><path d="M22 3 11.2 13.1" stroke="#111" stroke-width="1.4"/></svg>'


def send_html(s, acc, sub):
    """Kurdele stilinin 'gönder' kısmı. send_style: 'ucus' (kesik çizgili uçuş rotası) | 'kisiler' (kime gönderilir çipleri)."""
    share = s.get("share", "")
    st = s.get("send_style", "ucus")
    if st == "kisiler":
        names = s.get("send_to", ["Annenize", "Eşinize", "Komşunuza"])
        chips = "".join(
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:12px">'
            f'<div style="width:118px;height:118px;border-radius:50%;border:3px dashed {acc};display:flex;align-items:center;justify-content:center;font-family:{SERIF};font-size:52px;font-weight:700;color:{acc}">{n[0]}</div>'
            f'<div style="font-family:{SANS};font-size:30px;color:#fff">{n}</div></div>' for n in names)
        return f'''<div style="position:absolute;left:90px;right:90px;bottom:205px">
<div style="font-family:{SERIF};font-style:italic;font-size:46px;color:{acc};margin-bottom:26px">{share or "Kimin dizi ağrıyor?"}</div>
<div style="display:flex;align-items:flex-end;gap:40px">{chips}
<div style="margin-left:auto;width:118px;height:118px;border-radius:50%;background:{acc};display:flex;align-items:center;justify-content:center;transform:rotate(-12deg);box-shadow:0 12px 26px rgba(0,0,0,.3)">{PLANE.format(c="#111")}</div></div></div>'''
    # 'ucus': kesik çizgili uçuş rotası, uçak rotanın sonunda
    return f'''<svg style="position:absolute;left:70px;bottom:215px" width="940" height="250" viewBox="0 0 940 250" fill="none">
<path d="M10 220 C 180 230, 260 120, 420 150 S 700 230, 820 70" stroke="{acc}" stroke-width="5" stroke-dasharray="4 18" stroke-linecap="round"/>
<circle cx="10" cy="220" r="9" fill="{acc}"/></svg>
<div style="position:absolute;right:70px;bottom:400px;transform:rotate(-8deg);filter:drop-shadow(0 10px 18px rgba(0,0,0,.35))">{PLANE_FILLED.format(c=acc, w=120)}</div>
<div style="position:absolute;left:90px;bottom:375px;max-width:600px;font-family:{SERIF};font-style:italic;font-size:48px;line-height:1.15;color:#fff">{share}</div>'''


def cta_html(s, acc, sub, style):
    share = s.get("share", "")
    if style == "bar":  # Instagram eylem çubuğu + el çizimi oklar
        return f'''<div style="position:absolute;left:90px;right:90px;bottom:225px;height:130px;border-radius:30px;background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.18);display:flex;align-items:center;padding:0 44px;gap:44px">
{HEART}{BUBBLE}<span style="filter:drop-shadow(0 0 14px {acc})">{PLANE.format(c=acc).replace('width="60" height="60"','width="62" height="62"')}</span>
<span style="margin-left:auto;filter:drop-shadow(0 0 14px {acc})"><svg width="62" height="62" viewBox="0 0 24 24" fill="{acc}" stroke="{acc}" stroke-width="2" stroke-linejoin="round"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-5-7 5V4a1 1 0 0 1 1-1z"/></svg></span></div>
<svg style="position:absolute;left:250px;bottom:350px" width="140" height="120" viewBox="0 0 140 120" fill="none" stroke="{acc}" stroke-width="5" stroke-linecap="round"><path d="M20 20 C 60 10, 110 40, 112 95"/><path d="M96 82 L112 98 L124 78"/></svg>
<div style="position:absolute;left:120px;bottom:470px;font-family:{SERIF};font-style:italic;font-size:46px;color:{acc}">{share or "gönderin"}</div>
<svg style="position:absolute;right:120px;bottom:350px" width="120" height="120" viewBox="0 0 120 120" fill="none" stroke="{acc}" stroke-width="5" stroke-linecap="round"><path d="M100 18 C 60 20, 30 50, 40 98"/><path d="M26 84 L40 100 L54 84"/></svg>
<div style="position:absolute;right:110px;bottom:470px;font-family:{SERIF};font-style:italic;font-size:46px;color:{acc}">kaydedin</div>'''
    if style == "ribbon":  # tepeden sarkan yer imi kurdelesi + alt not
        return f'''<div style="position:absolute;right:110px;top:0;width:120px;height:330px;background:{acc};clip-path:polygon(0 0,100% 0,100% 100%,50% 84%,0 100%);box-shadow:0 10px 30px rgba(0,0,0,.35);display:flex;align-items:flex-end;justify-content:center;padding-bottom:86px">
<span style="writing-mode:vertical-rl;transform:rotate(180deg);font-family:{SANS};font-weight:700;letter-spacing:6px;font-size:30px;color:#111">KAYDET</span></div>
{send_html(s, acc, sub)}'''
    # varsayılan "dm": mesaj balonu taslağı
    return f'''<div style="position:absolute;left:90px;right:160px;bottom:215px">
<div style="font-family:{SANS};font-size:26px;letter-spacing:4px;color:{sub};margin-bottom:16px">GÖNDERMEK İSTEDİĞİNİZ KİŞİYE</div>
<div style="display:inline-block;background:#fff;color:#111;font-family:{SANS};font-size:40px;line-height:1.25;padding:26px 34px;border-radius:36px 36px 36px 8px;max-width:760px;box-shadow:0 14px 30px rgba(0,0,0,.25)">{share}</div>
<div style="display:flex;gap:26px;margin-top:26px;align-items:center">
<div style="width:96px;height:96px;border-radius:50%;background:{acc};display:flex;align-items:center;justify-content:center">{PLANE.format(c="#111")}</div>
<div style="width:96px;height:96px;border-radius:50%;border:3px solid {acc};display:flex;align-items:center;justify-content:center">{BOOKMARK.format(c=acc)}</div>
<div style="font-family:{SERIF};font-style:italic;font-size:40px;color:{sub}">gönderin, kaydedin</div></div></div>'''


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
        cta = cta_html(s, acc, sub, s.get("cta_style", "dm"))
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:{SERIF};color:#fff;background:{th["bg"]};position:relative;overflow:hidden}}
.top{{position:absolute;left:90px;top:80px;display:flex;align-items:center;gap:26px}}
.av{{width:124px;height:124px;border-radius:50%}}
.nm{{font-size:46px;font-weight:700;line-height:1.1}}
.hd{{font-family:{SANS};font-size:30px;color:{sub};margin-top:6px}}
.tcnt{{position:absolute;right:90px;top:96px;font-family:{SANS};font-weight:700;font-size:28px;letter-spacing:3px}}
.label{{position:absolute;left:90px;top:262px;font-family:{SANS};font-weight:700;letter-spacing:5px;font-size:28px;color:{acc};text-transform:uppercase}}
.blk{{position:absolute;left:90px;right:{'430px' if has_photo else ('260px' if last and s.get('cta_style')=='ribbon' else '90px')};top:330px;bottom:{('560px' if s.get('cta_style','dm')!='ribbon' else '520px') if last else '290px'};display:flex;align-items:center}}
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
{'' if last and s.get('cta_style')=='ribbon' else f'<div class="tcnt">{i:02d} / {n:02d}</div>'}
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
