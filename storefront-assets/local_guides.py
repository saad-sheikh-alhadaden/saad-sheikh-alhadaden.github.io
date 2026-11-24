"""Build the two local shopping guides from the storefront's published products."""
import json
import re
from decimal import Decimal
from html import escape
from pathlib import Path
from urllib.parse import quote

ORIGIN = "https://saad-customer-app.onrender.com"
STORE = "شركة سعد شيخ الحدادين"
MAIN_MAP = "https://maps.app.goo.gl/ATzzUQw2CAZLy3iN7?g_st=ic"
EIN_MAP = "https://maps.google.com/?cid=2144353980955415821"
BATH = "bathroom-fixtures-damascus"
KITCHEN = "kitchen-mixers-damascus"
KITCHEN_COLLECTION = "kitchen-mixers"
GUIDES = {
    BATH: {
        "title": "تجهيزات وإكساء حمامات في دمشق",
        "intro": "عم تجهّز حمّامك؟ ابدأ بعرض المغسلة، وشوف أي خلاط وشاور بيناسبوا المساحة والتمديدات. فيك تقارن الموديلات هون أو تشوفها معنا في المناخلية وعين ترما.",
        "groups": [
            ("مغاسل مع خزائن", "قِس العرض المتاح بين الحائط والباب، واترك مجال لفتح أدراج الخزانة. إذا بدك حوضين، شوف مقاس VIVION DUBE.",
             [("cabinet-v13", "مغسلة مع خزانة", "V13"), ("cabinet-vivion-dube", "مغسلة بحوضين مع خزانة", "VIVION DUBE")]),
            ("خلاطات مغاسل وشاورات", "ارتفاع حافة الحوض ومكان خروج المياه بيساعدوك تختار خلاط المغسلة. وللشاور، قارن شكل الجهاز وطريقة التحكم من صور كل موديل.",
             [("slim", "خلاط مغسلة", "Slim"), ("shower-midas", "شاور بيانو", "Midas"), ("shower-fish", "شاور بيانو", "Fish")]),
        ],
        "related": [("/washbasins/", "كل المغاسل والخزائن"), ("/smart-showers/", "كل الشاورات الذكية"),
                    ("/#accessories", "إكسسوارات الحمام"), ("/mixers/", "كل الخلاطات")],
    },
    KITCHEN: {
        "title": "خلاطات مطبخ في دمشق",
        "intro": "قارن خلاطات المطبخ حسب مكان التركيب وطريقة استخدام الحوض. شوف صور الموديلات وأسعارها، أو اسألنا بفرع المناخلية بدمشق أو عين ترما بريف دمشق.",
        "groups": [
            ("اختَر حسب مكان التركيب", "الخلاط الجداري بيركب على تمديدات الحائط. أمّا إذا عندك فتحة على المجلى أو الرخامة، فشوف موديل الشكّ العالي وتأكد من المساحة المتاحة خلفه.",
             [("java-mix-wall-kitchen-mixer", "خلاط جداري كيوب", "JAVA MIX"), ("java-mix-tall-mixer", "خلاط مجلى كيوب", "JAVA MIX")]),
            ("خلاطات للحوض الواسع", "إذا كان الحوض عريض، قارن شكل المصبّ ومدى وصوله إلى الأطراف. صور كل موديل بتبيّن مكان المقبض والمساحة اللي بيحتاجها عند التركيب.",
             [("gessi-venti-semi-pro", "خلاط مجلى فينتي", "Gessi Venti Semi-Pro"), ("rs-kitchen-mixer", "خلاط مجلى RS", "Kitchen Mixer RS")]),
        ],
        "related": [("/java-mix-cube-wall-kitchen-mixer/", "جافا كيوب جداري وأسعار ألوانه"),
                    ("/java-mix-cube-kitchen-mixer/", "جافا كيوب شك للمجلى"),
                    ("/magic-360-kitchen-mixer/", "صور خلاط ماجيك 360°"),
                    (f"/{KITCHEN_COLLECTION}/", "كل خلاطات المجلى وأسعارها"), ("/java-mix/", "كل أطقم JAVA MIX"), ("/mixers/", "كل الخلاطات"),
                    (f"/{BATH}/", "تجهيزات الحمّام")],
    },
}

STYLE = """
:root{color-scheme:dark;--bg:#171512;--card:#24201c;--line:#423a30;--ink:#f5f0e7;--muted:#c8c0b4;--gold:#e1c18a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:1rem/1.65 system-ui,sans-serif}
a{color:var(--gold);text-underline-offset:.22em}a:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.wrap{max-width:62rem;margin:auto;padding:0 1.2rem}header,footer{border-block-end:1px solid var(--line)}
.bar{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1rem}
.brand,.card,.related a{text-decoration:none}.brand{display:flex;align-items:center;gap:.6rem;color:var(--ink);font-weight:650}
.brand img{object-fit:contain}header a:last-child{white-space:nowrap}main{padding-block-end:3rem!important}
h1,h2,h3{line-height:1.35;margin:0}h1{font-size:clamp(1.9rem,6vw,3.3rem);margin-block:.25em}
h2{font-size:clamp(1.35rem,4vw,1.85rem)}h3{font-size:1.04rem}.intro{padding-block:clamp(1.4rem,5vw,3.3rem) .3rem}
p{max-width:47rem;margin:.5rem 0 1.2rem;color:var(--muted)}.group,.more{margin-block:2rem}
.grid,.branches{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(13rem,100%),1fr));gap:1rem}
.card{display:flex;flex-direction:column;overflow:hidden;border:1px solid var(--line);border-radius:.9rem;background:var(--card);color:var(--ink)}
.card img{display:block;width:100%;height:auto;aspect-ratio:4/5;object-fit:contain;background:#191715}
.cardbody{display:grid;gap:.2rem;padding:.8rem 1rem}.model{color:var(--muted);font-size:.9rem}.price{font-weight:700;color:var(--gold)}
.related{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:.85rem}.related a{border:1px solid var(--line);border-radius:2rem;padding:.45em .9em}
.branches{margin-top:1rem}.branches article{border-block-start:1px solid var(--line);padding-block:1rem}.branches p{margin:.25rem 0 .7rem}
.actions{display:flex;flex-wrap:wrap;gap:1.4rem}footer{border-block:1px solid var(--line);padding-block:1rem;color:var(--muted)}
@media(min-width:54rem){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}.grid.pair{grid-template-columns:repeat(2,minmax(0,1fr));max-width:44rem}}
@media(max-width:32rem){.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem}.cardbody{padding:.7rem}.branches{grid-template-columns:1fr}}
"""


def read_card(root, slug, title, model):
    source = (root / slug / "index.html").read_text()
    for payload in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
        product = json.loads(payload)
        if product.get("@type") == "Product":
            break
    else:
        raise ValueError(f"No product data for {slug}")
    image = product["image"]
    if isinstance(image, list):
        image = image[0]
    offer = product["offers"]
    low = Decimal(str(offer.get("price", offer.get("lowPrice"))))
    high = Decimal(str(offer.get("highPrice", low)))
    if offer["priceCurrency"] != "USD":
        raise ValueError(f"Unexpected price currency for {slug}")
    price = format(low.normalize(), "f")
    if high != low:
        price += "–" + format(high.normalize(), "f")
    return {"path": f"/{slug}/", "image": image, "title": title, "model": model, "price": price}


def card_html(card, first):
    load = 'fetchpriority="high"' if first else 'loading="lazy"'
    return f'''<a class="card" href="{card['path']}"><img src="{escape(card['image'])}" width="400" height="500" alt="" {load}>
    <div class="cardbody"><h3>{escape(card['title'])}</h3><span class="model"><bdi>{escape(card['model'])}</bdi></span>
    <span class="price"><bdi dir="ltr">{card['price']}</bdi> دولار</span></div></a>'''


BRANCHES = [
    ("المناخلية", "دمشق", "شارع الملك فيصل، مقابل قوس المناخلية", "0944881127", MAIN_MAP),
    ("عين ترما", "ريف دمشق", "عين ترما، دوار السفينة", "0945541790", EIN_MAP),
]
BRANCH_NUMBERS = {
    phone: (name, maps) for name, city, address, phone, maps in BRANCHES
}
ICONS = {
    "phone": '<path d="M6.6 3.5h2l1.5 4-2 1.8a14 14 0 0 0 6.6 6.6l1.8-2 4 1.5v2c0 1.8-1.5 3.2-3.3 2.9C10.3 19.2 4.8 13.7 3.7 6.8c-.3-1.8 1.1-3.3 2.9-3.3Z"/>',
    "whatsapp": '<path d="M20.8 11.8a8.8 8.8 0 0 1-13 7.7l-4.7 1.3 1.3-4.5A8.8 8.8 0 1 1 20.8 11.8Z"/><path d="M8.6 7.4c-.7.2-1 1.2-.8 2.1.7 2.6 3.6 5.5 6.4 6 .9.1 1.8-.5 2-1.4l-2.4-1.3-.9 1c-1.6-.7-2.8-1.9-3.5-3.4l.8-1-1-2Z" fill="currentColor" stroke="none"/>',
    "map": '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.2"/>',
}


def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def branch_links(number):
    name, maps = BRANCH_NUMBERS[number]
    phone = "963" + number[1:]
    message = f"مرحباً، عم بتصفّح متجركم الإلكتروني وحابب استفسر عن أحد المنتجات المتوفّرة بفرع {name}."
    return f'''<div class="branch-links">
    <div class="branch-buttons">
      <a class="branch-call" href="tel:+{phone}" aria-label="اتصل بفرع {name}">{icon("phone")}اتصال</a>
      <a class="branch-chat" href="https://wa.me/{phone}?text={quote(message)}" target="_blank" rel="noopener" aria-label="راسل فرع {name} على واتساب">{icon("whatsapp")}واتساب</a>
    </div>
    <div class="branch-details"><a href="{escape(maps)}" target="_blank" rel="noopener" aria-label="موقع فرع {name} على الخريطة">{icon("map")}الخريطة</a><bdi dir="ltr">{number}</bdi></div>
    </div>'''


def branch_html(name, address, number):
    return f'<article><h3>{name}</h3><p>{address}</p>{branch_links(number)}</article>'


def build_page(root, slug, guide):
    url = f"{ORIGIN}/{slug}/"
    groups, cards = [], []
    for heading, text, products in guide["groups"]:
        group = [read_card(root, *product) for product in products]
        rendered = "".join(card_html(card, not cards and idx == 0) for idx, card in enumerate(group))
        layout = "grid pair" if len(group) == 2 else "grid"
        groups.append(f'<div class="group"><h2>{heading}</h2><p>{text}</p><div class="{layout}">{rendered}</div></div>')
        cards.extend(group)
    title, intro = guide["title"], guide["intro"]
    item_list = [{"@type": "ListItem", "position": i, "url": ORIGIN + card["path"],
                  "name": card["title"] + " " + card["model"]} for i, card in enumerate(cards, 1)]
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "url": url, "name": title,
              "inLanguage": "ar-SY", "description": intro, "mainEntity": {"@type": "ItemList", "itemListElement": item_list}}
    related = "".join(f'<a href="{path}">{label}</a>' for path, label in guide["related"])
    branches = "".join(branch_html(name, f"{city}، {address}", phone)
                       for name, city, address, phone, _ in BRANCHES)
    return f'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {STORE}</title><meta name="description" content="{escape(intro)}">
<link rel="canonical" href="{url}"><link rel="icon" href="/assets/saad-brand-icon-48.png">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{title} | {STORE}">
<meta property="og:description" content="{escape(intro)}"><meta property="og:image" content="{escape(cards[0]['image'])}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script><style>{STYLE}</style></head>
<body><header><div class="wrap bar"><a class="brand" href="/"><img width="40" height="40" src="/assets/saad-gold-mark.webp" alt="">{STORE}</a>
<a href="/#collections">المجموعات</a></div></header>
<main class="wrap"><section><div class="intro"><h1>{title}</h1><p>{intro}</p></div>
{''.join(groups)}<div class="more"><h2>تصفّح أيضاً</h2><div class="related">{related}</div></div>
<div class="more"><h2>وين بتلاقينا؟</h2><div class="branches">{branches}</div></div></section></main>
<footer><div class="wrap"><a href="/branches/">عناوين الفروع وأرقام التواصل</a> · <a href="/">العودة إلى متجر {STORE}</a></div></footer></body></html>'''


def publish_guides(root):
    kitchen_link = '<a href="#kitchen">مطبخ <bdi>Kitchen</bdi></a>'
    links = (f'<a href="/{KITCHEN_COLLECTION}/"><strong>خلاطات مجلى</strong>'
             '<small><bdi lang="en" dir="ltr">Kitchen Mixers</bdi></small></a>'
             f'<a href="/{KITCHEN}/">خلاطات مطبخ في دمشق</a>'
             f'<a href="/{BATH}/">تجهيزات وإكساء حمامات في دمشق</a>')
    legacy_actions = re.compile(r'<div class="contact-actions">([^<]*(?:<a\b[^>]*>.*?</a>\s*)+)</div>', re.S)

    def upgrade_actions(match):
        telephone = re.search(r'href="tel:\+963(9\d{8})"', match[1])
        number = "0" + telephone[1] if telephone else ""
        return branch_links(number) if number in BRANCH_NUMBERS else match[0]

    heading = ('<header class="cabinet-heading"><h1><small>خلاطات مجلى</small>'
               '<bdi lang="en" dir="ltr">Kitchen Mixers</bdi></h1></header>'
               '<p class="catalog-intro">قارن أسعار خلاطات المجلى الجدارية والشكّ وخلاطات السحب، وشوف الألوان المتاحة لكل موديل. '
               f'<a href="/{KITCHEN}/">كيف تختار خلاط المطبخ المناسب لحوضك؟</a></p>')
    panel = re.compile(r'(<section class="panel" id="kitchen"[^>]*>)\s*<h1>.*?</h1>', re.S)

    for page in root.rglob("index.html"):
        source = page.read_text()
        if page == root / "index.html" and kitchen_link not in source and links not in source:
            raise ValueError("The storefront's home collection menu has changed")
        updated = legacy_actions.sub(upgrade_actions, source.replace(kitchen_link, links))
        # Apply the same collection styling as Smart Shower.
        updated = updated.replace("#showers,.concealed-gallery)", "#showers,#kitchen,.concealed-gallery)")
        updated = panel.sub(
            lambda m: m[1] + heading,
            updated, count=1)
        if updated != source:
            page.write_text(updated)
    home = (root / "index.html").read_text()
    collection_page = home.replace('<html lang="ar" dir="rtl">', '<html lang="ar" dir="rtl" data-screen="kitchen">', 1)
    collection_page = collection_page.replace('<meta charset="utf-8">', '<meta charset="utf-8"><base href="/">', 1)
    collection_page = collection_page.replace('<section id="home">', '<section id="home" hidden>', 1)
    collection_page, count = re.subn(r'(<section class="panel" id="kitchen")[^>]*>', r'\1>', collection_page, count=1)
    if count != 1 or heading not in collection_page:
        raise ValueError("Missing kitchen collection panel")
    url = f"{ORIGIN}/{KITCHEN_COLLECTION}/"
    title = f"خلاطات مجلى ومطبخ في دمشق – الموديلات والأسعار | {STORE}"
    description = "قارن أسعار خلاطات المجلى الجدارية والشكّ والسحب من شركة سعد شيخ الحدادين. تصفّح صور الموديلات وألوانها، وشاهد عناوين فرعَي دمشق وعين ترما."
    collection_page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", collection_page, count=1)
    collection_page = collection_page.replace(f'rel="canonical" href="{ORIGIN}/"', f'rel="canonical" href="{url}"', 1)
    for key, value in {"description": description, "og:description": description, "og:url": url,
                       "og:title": title}.items():
        collection_page = re.sub(
            rf'(<meta (?:name|property)="{re.escape(key)}" content=")[^"]*',
            lambda m: m[1] + escape(value), collection_page, count=1)
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "url": url, "name": "خلاطات مجلى",
              "inLanguage": "ar-SY", "description": description}
    collection_page = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        lambda _: f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>',
        collection_page, count=1, flags=re.S)
    folder = root / KITCHEN_COLLECTION
    folder.mkdir(exist_ok=True)
    (folder / "index.html").write_text(collection_page)
    for slug, guide in GUIDES.items():
        folder = root / slug
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(build_page(root, slug, guide))


if __name__ == "__main__":
    publish_guides(Path("storefront"))
