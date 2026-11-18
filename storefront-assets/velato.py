"""Publish the Velato concealed collection using the storefront's shared cart."""
import json
import re
import shutil
import xml.etree.ElementTree as ET
from hashlib import sha256
from html import escape
from pathlib import Path

FINISH = "Brushed Rose Gold"
WARRANTY = '<p class="velato-warranty"><strong>الكفالة الذهبية</strong><span>تبديل خلال أول سنتين من الكفالة</span></p>'
SET = "velato-concealed-set"
SET_GROUP = "concealed-sets"
PARTS = {
    "shower": ("شاور دفن", 1200, 6),
    "basin": ("خلاط مغسلة دفن", 475, 3),
    "toilet": ("خلاط تواليت دفن", 300, 2),
}


def publish(root, origin, store, meta, preview, schema_pattern, json_script):
    source = Path(__file__).with_name("velato")
    models = {}
    for kind, (label, price, count) in PARTS.items():
        photos = [f"/assets/velato-{kind}-{i}.webp" for i in range(1, count + 1)]
        for photo in photos:
            shutil.copyfile(source / Path(photo).name, root / photo.lstrip("/"))
        models[f"velato-concealed-{kind}"] = (label, price, photos, f"concealed-{kind}-mixer")
    models[SET] = ("طقم دفن كامل", 1975, [model[2][0] for model in models.values()], SET_GROUP)
    labels = {"encastre": "خلاطات الدفن", SET_GROUP: "أطقم الدفن الكاملة"}
    labels.update({group: label for slug, (label, price, photos, group) in models.items() if slug != SET})

    def picture(photo, alt):
        return f'<img src="{photo}" alt="{escape(alt)}" loading="lazy" decoding="async">'

    def card(slug, from_set=False):
        label, price, photos, group = models[slug]
        url = f"/{slug}/" + ("?from=set" if from_set else "")
        return (f'<a class="velato-card" href="{url}">{picture(photos[0], f"Velato · {label} · {FINISH}")}'
                f'<span><bdi>Velato</bdi><br>{label}<br><bdi>${price:,}</bdi></span></a>')

    part_cards = "".join(card(slug, from_set=True) for slug in models if slug != SET)
    return_links = "".join(
        f'<a class="velato-link" href="/{slug}/?from=set" data-set-return="{kind}" hidden>'
        f'<span>الرجوع إلى {models[slug][0]}</span><span aria-hidden="true">↶</span></a>'
        for kind in PARTS for slug in [f"velato-concealed-{kind}"]
    )
    hero = (f'<a class="velato-feature" href="/{SET_GROUP}/"><span>أطقم الدفن الكاملة'
            '<br><bdi lang="en">Concealed Sets</bdi><small>استعرض الأطقم</small></span>'
            '<div class="velato-strip">' + "".join(
                picture(model[2][0], model[0]) for slug, model in models.items() if slug != SET
            ) + '</div></a>')
    styles = """<style>
.velato-feature,.velato-card{display:block;color:#f6ebdc;background:#201c19;border:1px solid #9c7656;border-radius:14px;overflow:hidden;text-decoration:none}
.velato-feature{margin:1rem 0}.velato-feature>span,.velato-card>span{display:block;padding:.75rem 1rem}
.velato-feature small{display:block;margin-top:.35rem;color:#e4b58d}
.velato-strip,.velato-parts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.45rem}
.velato-strip img,.velato-card img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover}
.velato-card{max-width:22rem;margin:.6rem 0 1rem}.velato-parts .velato-card>span{padding:.5rem;font-size:.8rem}
.velato-gallery{display:flex;gap:.45rem;overflow-x:auto;padding:.5rem 0}
.velato-gallery button{flex:0 0 4rem;background:transparent;border:1px solid transparent;border-radius:6px;padding:2px}
.velato-gallery button[aria-pressed=true]{border-color:#be9166}.velato-gallery img{display:block;width:100%;border-radius:4px}
.product-info .velato-origin{display:inline-block;margin:.15rem 0 .7rem;padding:.25rem .65rem;
border:1px solid #aa8a5f;border-radius:100px;color:#5b462c;font-size:.76rem;letter-spacing:.025em}
.product-info .velato-warranty{display:grid;gap:.2rem;margin:1rem 0;padding:.65rem .85rem;
border-inline-start:2px solid #a67a3d;background:#ebe3d4;color:#35291b;font-size:.86rem}
.velato-warranty strong{color:#684a25}
.product-info a.velato-link:not([hidden]){display:flex;align-items:center;justify-content:space-between;
gap:1rem;min-height:48px;margin:.7rem 0;padding:.55rem .85rem;border:1px solid #aa8a5f;
border-radius:10px;background:#f7f0e3;color:#392b1b;text-decoration:none;font-weight:650}
.velato-link:focus-visible{outline:2px solid #81591f;outline-offset:3px}
</style>"""
    details = []
    registry_additions = []
    search_links = ""
    saved_links = ""
    for slug, (label, price, photos, group) in models.items():
        name = f"Velato · {label}"
        registry = {"name": name, "search": f"velato فيلاتو {label} دفن {FINISH.lower()} {price}",
                    "price": price, "images": {FINISH: photos[0]}, "defaultColor": FINISH,
                    "category": group, "favoriteKey": "saad-saved-" + slug}
        registry_additions.append(f'  "{slug}": {json.dumps(registry, ensure_ascii=False)},')
        search_links += f'<a href="/{slug}/" data-search-product="{slug}" hidden>{name}</a>'
        saved_links += f'<a href="/{slug}/" data-saved="{slug}" hidden>{name}</a>'
        gallery = ""
        for index, photo in enumerate(photos, 1):
            alt = f"{name} · {FINISH} · صورة {index}"
            gallery += (f'<button type="button" data-gallery-src="{photo}" data-width="1050" data-height="1300" '
                        f'aria-pressed="{str(index == 1).lower()}" aria-label="{alt}">{picture(photo, "")}</button>')
        related = (f'{return_links}<h2>مكوّنات الطقم</h2><div class="velato-parts">{part_cards}</div>' if slug == SET
                   else f'<a class="velato-link" href="/{SET}/?from={slug.rsplit("-", 1)[1]}">'
                        '<span>شوف طقم Velato الكامل</span><span aria-hidden="true">‹</span></a>')
        order = "أضف الطقم للسلة" if slug == SET else "أضف إلى السلة"
        details.append(f"""
<section id="{slug}" class="vanity-detail" data-nosnippet hidden>
  <div class="product-image">{picture(photos[0], name)}
    <button class="circle" data-save type="button" aria-label="إضافة Velato إلى المفضّلة" aria-pressed="false">♡</button>
  </div>
  <div class="product-info">
    <p class="category">{label}</p><h1><bdi>Velato</bdi></h1>
    <span class="velato-origin" lang="en" dir="ltr">Made in Italy</span>
    <div class="velato-gallery" aria-label="صور المنتج">{gallery}</div>
    <p><bdi>{FINISH}</bdi></p>
    <p class="price-tag" dir="ltr">${price:,}</p>
    <div class="qty"><span>الكمية</span><button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button><output data-quantity>1</output><button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button></div>
    <button class="action" data-add-cart type="button">{order} — ${price:,}</button>
    {related}
    {WARRANTY}
  </div>
</section>""")

    home_path = root / "index.html"
    home = home_path.read_text()
    old_script = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    js = (root / old_script).read_text()
    js = js.replace("const products = {", "const products = {\n" + "\n".join(registry_additions), 1)
    if registry_additions[0] not in js:
        raise ValueError("Missing storefront product registry")
    js = js.replace('const encastreScreens = new Set([', f'const encastreScreens = new Set(["{SET_GROUP}", ', 1)
    js = js.replace('addButton.textContent = `أضف إلى السلة — ${money(quantity * unitPrice(product, orderColor()))}`;',
                    'addButton.textContent = `${id === "velato-concealed-set" ? "أضف الطقم للسلة" : "أضف إلى السلة"} — ${money(quantity * unitPrice(product, orderColor()))}`;')
    new_script = f"assets/storefront-{sha256(js.encode()).hexdigest()[:12]}.js"
    (root / new_script).write_text(js)

    def add_inside(html, id_, content, after_heading=False):
        pattern = rf'(<(?:div|section)\b[^>]*\bid="{id_}"[^>]*>)'
        if after_heading:
            pattern += r'(.*?</h1>)'
        html, count = re.subn(pattern, lambda m: m[0] + content, html, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Missing storefront element {id_}")
        return html

    for path in root.rglob("index.html"):
        html = path.read_text()
        if old_script not in html:
            continue
        html = html.replace(old_script, new_script).replace("<title>", styles + "<title>", 1)
        html = add_inside(html, "result", search_links)
        html = add_inside(html, "saved", saved_links)
        html = add_inside(html, "encastre", hero, after_heading=True)
        for slug, (_, _, _, group) in models.items():
            if slug != SET:
                html = add_inside(html, group, card(slug), after_heading=True)
                html = html.replace(f'href="#{group}"', f'href="/{group}/"')
        html = html.replace('href="#encastre"', 'href="/encastre/"')
        html = html.replace("</main>", f'<section class="panel" id="{SET_GROUP}" data-nosnippet hidden>'
                            f'<h1>أطقم الدفن الكاملة<br><bdi>Concealed Sets</bdi></h1>{card(SET)}</section>'
                            + "".join(details) + "</main>", 1)
        path.write_text(html)

    def landing(slug, title, description, photos, data):
        url = f"{origin}/{slug}/"
        full_title = f"{title} | {store}"
        page = home_path.read_text().replace('<html lang="ar" dir="rtl">',
            f'<html lang="ar" dir="rtl" data-screen="{slug}">', 1)
        page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8"><base href="/"> ', 1)
        page = page.replace('<section id="home">', '<section id="home" hidden>', 1)
        pattern = rf'(<section\b[^>]*\bid="{slug}"[^>]*?)(?: data-nosnippet)? hidden>'
        page, count = re.subn(pattern, r'\1>', page, count=1)
        if count != 1:
            raise ValueError(f"Missing page panel {slug}")
        page = re.sub(r"<title>.*?</title>", lambda _: f"<title>{escape(full_title)}</title>", page, count=1)
        page = page.replace(f'rel="canonical" href="{origin}/"', f'rel="canonical" href="{url}"', 1)
        for key, value in {"description": description, "og:title": full_title, "og:description": description,
                           "og:url": url, "twitter:title": full_title, "twitter:description": description}.items():
            page = meta(page, key, value)
        page = preview(page, title, origin + photos[0])
        data.update({"@context": "https://schema.org", "url": url, "name": title, "description": description})
        page = schema_pattern.sub(lambda _: json_script(data), page, count=1)
        target = root / slug
        target.mkdir(exist_ok=True)
        (target / "index.html").write_text(page)

    for slug, (label, price, photos, group) in models.items():
        contents = " يشمل شاور دفن وخلاط مغسلة دفن وخلاط تواليت دفن." if slug == SET else ""
        landing(slug, f"{label} Velato", f"{label} Velato بتشطيب {FINISH}، صنع في إيطاليا. ${price:,}.{contents}",
                photos, {"@type": "Product", "@id": f"{origin}/{slug}/#product", "sku": slug,
                         "color": FINISH, "countryOfOrigin": {"@type": "Country", "name": "Italy"},
                         "image": [origin + photo for photo in photos],
                         "offers": {"@type": "Offer", "price": price, "priceCurrency": "USD",
                                    "url": f"{origin}/{slug}/"}})
    for slug, label in labels.items():
        children = (list(labels)[1:] if slug == "encastre" else
                    [model for model, data in models.items() if data[3] == slug])
        cover = next((data[2] for data in models.values() if data[3] == slug), models[SET][2])
        landing(slug, label, f"تصفّح {label} وشاهد صور Velato بتشطيب {FINISH} والأسعار.", cover,
                {"@type": "CollectionPage", "mainEntity": {"@type": "ItemList", "itemListElement": [
                    {"@type": "ListItem", "position": index, "url": f"{origin}/{child}/"}
                    for index, child in enumerate(children, 1)]}})

    sitemap = root / "sitemap.xml"
    tree = ET.parse(sitemap)
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    node = tree.getroot()
    existing = {entry.text for entry in node.findall(f"{{{namespace}}}url/{{{namespace}}}loc")}
    for slug in (*labels, *models):
        url = f"{origin}/{slug}/"
        if url not in existing:
            ET.SubElement(ET.SubElement(node, f"{{{namespace}}}url"), f"{{{namespace}}}loc").text = url
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)
