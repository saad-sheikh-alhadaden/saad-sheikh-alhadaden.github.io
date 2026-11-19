"""Publish concealed fixtures using the storefront's shared cart."""
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
ST_GR = "st-gr"
CASCATA = "cascata-oro"
CASCATA_CHROME = f"{CASCATA}-chrome"
CASCATA_TOILET = f"{CASCATA}-concealed-toilet"
PARTS = {
    "shower": ("شاور دفن", 1200, 6),
    "basin": ("خلاط مغسلة دفن", 475, 3),
    "toilet": ("خلاط تواليت دفن", 300, 2),
}


def publish(root, origin, store, meta, preview, schema_pattern, json_script):
    models = {}
    for kind, (label, price, count) in PARTS.items():
        photos = [f"/assets/velato-{kind}-{i}.webp" for i in range(1, count + 1)]
        models[f"velato-concealed-{kind}"] = (label, price, photos, f"concealed-{kind}-mixer")
    for kind, price in {"shower": 700, "basin": 300}.items():
        photos = [f"/assets/octagon-{kind}-{i}.webp" for i in range(1, 5)]
        models[f"octagon-concealed-{kind}"] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    color_galleries = {}
    for kind, price, count in [("shower", 700, 5), ("basin", 350, 2)]:
        slug = f"eclipse-flow-concealed-{kind}"
        galleries = {
            color: [f"/assets/eclipse-{kind}-{color.lower()}-{i}.webp" for i in range(1, count + 1)]
            for color in ("Black", "Chrome")
        }
        color_galleries[slug] = galleries
        photos = [photo for gallery in galleries.values() for photo in gallery]
        models[slug] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    for kind, price, count, first_color in [
        ("shower", 950, 1, "Rose Gold"),
        ("basin", 500, 4, "Gray"),
    ]:
        slug = f"lunaire-digital-blus-concealed-{kind}"
        colors = [first_color, *[color for color in ("Chrome", "Rose Gold", "Gray", "White")
                                 if color != first_color]]
        galleries = {
            color: [f"/assets/lunaire-{kind}-{color.lower().replace(' ', '-')}-{i}.webp"
                    for i in range(1, count + 1)]
            for color in colors
        }
        color_galleries[slug] = galleries
        photos = [photo for gallery in galleries.values() for photo in gallery]
        models[slug] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    for kind, price, count in [("shower", 450, 5), ("basin", 225, 3), ("toilet", 200, 4)]:
        photos = [f"/assets/cascata-{kind}-{i}.webp" for i in range(1, count + 1)]
        models[f"{CASCATA}-concealed-{kind}"] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    chrome_photos = {
        kind: [f"/assets/cascata-chrome-{kind}-{i}.webp" for i in range(1, count + 1)]
        for kind, count in (("shower", 5), ("basin", 3), ("toilet", 4))
    }
    for kind, price in (("shower", 350), ("basin", 325)):
        models[f"{CASCATA_CHROME}-concealed-{kind}"] = (
            PARTS[kind][0], price, chrome_photos[kind], f"concealed-{kind}-mixer"
        )
    label, price, gold_photos, group = models[CASCATA_TOILET]
    color_galleries[CASCATA_TOILET] = {"Gold": gold_photos, "Chrome": chrome_photos["toilet"]}
    models[CASCATA_TOILET] = (label, price, gold_photos + chrome_photos["toilet"], group)
    for kind, price, count in (("shower", 500, 5), ("basin", 300, 3), ("toilet", 200, 3)):
        photos = [f"/assets/stgr-{kind}-{i}.webp" for i in range(1, count + 1)]
        models[f"{ST_GR}-concealed-{kind}"] = (
            PARTS[kind][0], price, photos, f"concealed-{kind}-mixer"
        )
    sets = {}
    for prefix in ("velato", "octagon", "eclipse-flow", "lunaire-digital-blus", CASCATA, ST_GR):
        slug = f"{prefix}-concealed-set"
        kinds = PARTS if prefix in ("velato", CASCATA, ST_GR) else ("shower", "basin")
        parts = [f"{prefix}-concealed-{kind}" for kind in kinds]
        sets[slug] = parts
        if parts[0] in color_galleries:
            galleries = {
                color: [color_galleries[part][color][0] for part in parts]
                for color in color_galleries[parts[0]]
                if all(color in color_galleries[part] for part in parts)
            }
            color_galleries[slug] = galleries
            photos = [photo for gallery in galleries.values() for photo in gallery]
        else:
            photos = [models[part][2][0] for part in parts]
        price = 1975 if slug == SET else sum(models[part][1] for part in parts)
        label = "طقم دفن كامل" if len(parts) == 3 else "طقم شاور ومغسلة دفن"
        models[slug] = (label, price, photos, SET_GROUP)
    chrome_set = f"{CASCATA_CHROME}-concealed-set"
    chrome_parts = [f"{CASCATA_CHROME}-concealed-shower", f"{CASCATA_CHROME}-concealed-basin", CASCATA_TOILET]
    sets[chrome_set] = chrome_parts
    models[chrome_set] = ("طقم دفن كامل", sum(models[part][1] for part in chrome_parts),
                          [chrome_photos[kind][0] for kind in PARTS], SET_GROUP)
    part_sets = {part: slug for slug, parts in sets.items() for part in parts if part != CASCATA_TOILET}
    photo_sizes = {}
    for folder in ("eclipse", "lunaire", "cascata", "stgr"):
        photo_sizes.update(json.loads(Path(__file__).with_name(folder).joinpath("sizes.json").read_text()))
    for photo in dict.fromkeys(photo for model in models.values() for photo in model[2]):
        filename = Path(photo).name
        source = Path(__file__).with_name(filename.split("-", 1)[0])
        shutil.copyfile(source / filename, root / photo.lstrip("/"))
    labels = {"encastre": "خلاطات الدفن", SET_GROUP: "أطقم الدفن الكاملة"}
    labels.update({group: label for slug, (label, price, photos, group) in models.items() if slug not in sets})
    headings = {
        "encastre": "Encastre",
        SET_GROUP: "Concealed Sets",
        "concealed-shower-mixer": "Concealed Shower Mixer",
        "concealed-basin-mixer": "Concealed Basin Mixer",
        "concealed-toilet-mixer": "Concealed Toilet Mixer",
        "concealed-accessory": "Concealed Accessories",
    }

    def collection_heading(group):
        label = labels.get(group, "إكسسوارات الدفن")
        return (f'<header class="cabinet-heading"><h1><small>{label}</small>'
                f'<bdi lang="en" dir="ltr">{headings[group]}</bdi></h1></header>')

    def picture(photo, alt):
        return f'<img src="{photo}" alt="{escape(alt)}" loading="lazy" decoding="async">'

    def identity(slug):
        if slug.startswith(ST_GR + "-"):
            return "S.T Gr", "Gray"
        if slug == CASCATA_TOILET:
            return "S.T 80036", "Gold / Chrome"
        if slug.startswith(CASCATA_CHROME + "-"):
            return "Cascata Oro", "Chrome"
        if slug.startswith(CASCATA + "-"):
            return "Cascata Oro", "Gold"
        if slug.startswith("lunaire-"):
            return "Lunaire Digital blus", "Chrome / Rose Gold / Gray / White"
        if slug.startswith("eclipse-"):
            return "Eclipse Flow", "Black / Chrome"
        return ("OCTAGON", "Chrome") if slug.startswith("octagon-") else ("Velato", FINISH)

    def has_italian_origin(slug):
        if slug.startswith(ST_GR + "-"):
            return slug.endswith("-basin")
        return not slug.startswith(CASCATA + "-") or slug.startswith(CASCATA_CHROME + "-")

    def set_part_url(part, set_slug):
        color = "&amp;color=chrome" if part == CASCATA_TOILET and set_slug == chrome_set else ""
        return f"/{part}/?from=set{color}"

    def card(slug, set_slug):
        label, price, photos, group = models[slug]
        model_name, finish = identity(slug)
        photo = photos[0]
        if slug == CASCATA_TOILET:
            finish = "Chrome" if set_slug == chrome_set else "Gold"
            photo = color_galleries[slug][finish][0]
        return (f'<a class="velato-card" href="{set_part_url(slug, set_slug)}">{picture(photo, f"{model_name} · {label} · {finish}")}'
                f'<span><bdi>{model_name}</bdi><br>{label}<br><bdi>${price:,}</bdi></span></a>')

    def gallery_card(slug):
        label, price, photos, group = models[slug]
        model_name, finish = identity(slug)
        return (f'<a class="hero mixer-product" href="/{slug}/">'
                f'{picture(photos[0], f"{label} {model_name} · {finish}")}'
                f'<div class="mixer-product-copy"><strong><bdi lang="en" dir="ltr">{model_name}</bdi></strong>'
                f'<small><bdi lang="en" dir="ltr">{finish}</bdi></small>'
                f'<span dir="ltr">${price:,}</span></div></a>')

    grids = {
        group: '<div class="cabinet-gallery">' + "".join(
            gallery_card(slug) for slug, model in reversed(models.items()) if model[3] == group
        ) + '</div>'
        for group in labels if group != "encastre"
    }

    hero = (f'<a class="velato-feature" href="/{SET_GROUP}/"><span>أطقم الدفن الكاملة'
            '<br><bdi lang="en">Concealed Sets</bdi><small>استعرض الأطقم</small></span>'
            '<div class="velato-strip">' + "".join(
                picture(models[slug][2][0], models[slug][0]) for slug in sets[SET]
            ) + '</div></a>')
    styles = """<style>
.velato-feature,.velato-card{display:block;color:#f6ebdc;background:#201c19;border:1px solid #9c7656;border-radius:14px;overflow:hidden;text-decoration:none}
.velato-feature{margin:1rem 0}.velato-feature>span,.velato-card>span{display:block;padding:.75rem 1rem}
.velato-feature small{display:block;margin-top:.35rem;color:#e4b58d}
.velato-strip,.velato-parts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.45rem}
.velato-parts-pair{grid-template-columns:repeat(2,minmax(0,1fr))}
.velato-strip img,.velato-card img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover}
.velato-card{max-width:22rem;margin:.6rem 0 1rem}.velato-parts .velato-card>span{padding:.5rem;font-size:.8rem}
.velato-gallery{display:flex;gap:.45rem;overflow-x:auto;padding:.5rem 0}
.velato-gallery button{flex:0 0 4rem;background:transparent;border:1px solid transparent;border-radius:6px;padding:2px}
.velato-gallery button[aria-pressed=true]{border-color:#be9166}.velato-gallery img{display:block;width:100%;border-radius:4px}
.velato-gallery button[hidden]{display:none}
.velato-set-thumbnails{gap:.55rem;align-items:stretch}
.velato-set-thumbnails button{flex-basis:clamp(4.5rem,26%,6.5rem);min-width:0;padding:3px;
display:flex;flex-direction:column;border-color:#d8c9b6;border-radius:8px}
.velato-set-thumbnails button[aria-pressed=true]{border-color:#aa8055;background:#f7efe2}
.velato-set-thumbnails button:focus-visible{outline:2px solid #81591f;outline-offset:-2px}
.velato-set-thumbnails picture{display:block;width:100%}
.velato-set-thumbnails img{aspect-ratio:4/5;object-fit:cover}
.velato-set-thumbnails .velato-thumb-caption{width:100%;padding:.3rem .1rem .15rem;color:#5b462c;
font-family:inherit;font-size:.72rem;font-weight:600;line-height:1.45;text-align:center}
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
        model_name, finish = identity(slug)
        arabic_name = {"OCTAGON": "أوكتاغون", "Velato": "فيلاتو", "Eclipse Flow": "إكليبس فلو",
                       "Cascata Oro": "كاسكاتا أورو",
                       "S.T Gr": "اس تي جي آر st gr",
                       "S.T 80036": "اس تي 80036 st80036",
                       "Lunaire Digital blus": "لونير ديجيتال بلوس"}[model_name]
        name = f"{model_name} · {label}"
        galleries = color_galleries.get(slug, {finish: photos})
        default_color = next(iter(galleries))
        registry = {"name": name, "search": f"{model_name.lower()} {arabic_name} {label} دفن {finish.lower()} {price}",
                    "price": price, "images": {color: images[0] for color, images in galleries.items()},
                    "defaultColor": default_color,
                    "category": group, "favoriteKey": "saad-saved-" + slug}
        registry_additions.append(f'  "{slug}": {json.dumps(registry, ensure_ascii=False)},')
        search_links += f'<a href="/{slug}/" data-search-product="{slug}" hidden>{name}</a>'
        saved_links += f'<a href="/{slug}/" data-saved="{slug}" hidden>{name}</a>'
        parts = sets.get(slug, [])
        gallery_class = " velato-set-thumbnails" if parts else ""
        gallery = ""
        for color, images in galleries.items():
            color_attr = f' data-gallery-color="{color}"' if slug in color_galleries else ""
            hidden = "" if color == default_color else " hidden"
            for index, photo in enumerate(images, 1):
                width, height = photo_sizes.get(Path(photo).name, (1050, 1300))
                alt = f"{name} · {color} · صورة {index}"
                caption = ""
                if parts:
                    kind = parts[index - 1].rsplit("-", 1)[1]
                    part_label = "خلاط شاور دفن" if kind == "shower" else PARTS[kind][0]
                    alt = f"{part_label} · {color}"
                    caption = f'<span class="velato-thumb-caption">{part_label}</span>'
                pressed = str(index == 1 and not hidden).lower()
                gallery += (f'<button type="button" data-gallery-src="{photo}" data-width="{width}" data-height="{height}"'
                            f'{color_attr}{hidden} aria-pressed="{pressed}" aria-label="{alt}">'
                            f'{picture(photo, "")}{caption}</button>')
        finishes = f"<p><bdi>{finish}</bdi></p>"
        if slug in color_galleries:
            options = "".join(
                f'<button class="option" type="button" data-color="{color}" '
                f'aria-pressed="{str(color == default_color).lower()}"><bdi>{color}</bdi></button>'
                for color in galleries
            )
            finishes = f'<div class="options" role="group" aria-label="التشطيب">{options}</div>'
        if slug in sets:
            part_cards = "".join(card(part, slug) for part in parts)
            return_links = "".join(
                f'<a class="velato-link" href="{set_part_url(part, slug)}" data-set-return="{part.rsplit("-", 1)[1]}" hidden>'
                f'<span>الرجوع إلى {models[part][0]}</span><span aria-hidden="true">↶</span></a>'
                for part in parts
            )
            columns = " velato-parts-pair" if len(parts) == 2 else ""
            related = f'{return_links}<h2>مكوّنات الطقم</h2><div class="velato-parts{columns}">{part_cards}</div>'
        elif slug == CASCATA_TOILET:
            related = ""
        else:
            set_slug = part_sets[slug]
            kind = slug.rsplit("-", 1)[1]
            related = (f'<a class="velato-link" data-related-set href="/{set_slug}/?from={kind}">'
                       f'<span>شوف طقم {model_name} الكامل</span><span aria-hidden="true">‹</span></a>')
            if len(sets[set_slug]) == 2:
                other = next(part for part in sets[set_slug] if part != slug)
                related += (f'<a class="velato-link" href="/{other}/"><span>شوف {models[other][0]} {model_name}</span>'
                            '<span aria-hidden="true">‹</span></a>')
        order = "أضف الطقم للسلة" if slug in sets else "أضف إلى السلة"
        origin_badge = '<span class="velato-origin" lang="en" dir="ltr">Made in Italy</span>' if has_italian_origin(slug) else ""
        details.append(f"""
<section id="{slug}" class="vanity-detail" data-nosnippet hidden>
  <div class="product-image">{picture(photos[0], name)}
    <button class="circle" data-save type="button" aria-label="إضافة {model_name} إلى المفضّلة" aria-pressed="false">♡</button>
  </div>
  <div class="product-info">
    <p class="category">{label}</p><h1><bdi>{model_name}</bdi></h1>
    {origin_badge}
    <div class="velato-gallery{gallery_class}" aria-label="صور المنتج">{gallery}</div>
    {finishes}
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
    quantity_listener = '  for (const button of screen.querySelectorAll("[data-quantity-change]")) {'
    if quantity_listener not in js:
        raise ValueError("Missing storefront quantity controls")
    js = js.replace(quantity_listener,
                    f'  if (id === "{CASCATA_TOILET}" && requestedFinish === "chrome") {{\n'
                    '    choices.find(choice => choice.dataset.color === "Chrome")?.click();\n'
                    '  }\n' + quantity_listener, 1)
    js = js.replace('addButton.textContent = `أضف إلى السلة — ${money(quantity * unitPrice(product, orderColor()))}`;',
                    'addButton.textContent = `${product.category === "concealed-sets" ? "أضف الطقم للسلة" : "أضف إلى السلة"} — ${money(quantity * unitPrice(product, orderColor()))}`;')
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
        html = html.replace(":is(#mixers,#showers)", ":is(#mixers,#showers,.concealed-gallery)")
        html = html.replace("#showers .cabinet-heading h1 small", ":is(#showers,.concealed-gallery) .cabinet-heading h1 small")
        html = html.replace("#showers .cabinet-gallery + .contact-card", ":is(#showers,.concealed-gallery) .cabinet-gallery + .contact-card")
        for group in headings:
            if group != SET_GROUP:
                pattern = rf'(<section class="panel" id="{group}"[^>]*>\s*)<h1>.*?</h1>'
                content = hero if group == "encastre" else grids.get(group, "")
                html, count = re.subn(pattern, lambda m: m[1].replace('class="panel"', 'class="panel concealed-gallery"')
                                      + collection_heading(group) + content, html, count=1, flags=re.S)
                if count != 1:
                    raise ValueError(f"Missing concealed collection heading: {group}")
            if group in grids and group != SET_GROUP:
                html = html.replace(f'href="#{group}"', f'href="/{group}/"')
        html = html.replace('href="#encastre"', 'href="/encastre/"')
        html = html.replace("</main>", f'<section class="panel concealed-gallery" id="{SET_GROUP}" data-nosnippet hidden>'
                            f'{collection_heading(SET_GROUP)}{grids[SET_GROUP]}</section>'
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
        model_name, finish = identity(slug)
        contents = " يشمل " + " و".join(models[part][0] for part in sets[slug]) + "." if slug in sets else ""
        italy = has_italian_origin(slug)
        origin_text = "، صنع في إيطاليا" if italy else ""
        country = {"countryOfOrigin": {"@type": "Country", "name": "Italy"}} if italy else {}
        title = f"{label} {model_name}"
        if slug.startswith(CASCATA_CHROME + "-"):
            title += " · Chrome"
        landing(slug, title, f"{label} {model_name} بتشطيب {finish}{origin_text}. ${price:,}.{contents}",
                photos, {"@type": "Product", "@id": f"{origin}/{slug}/#product", "sku": slug,
                         "color": finish, **country,
                         "image": [origin + photo for photo in photos],
                         "offers": {"@type": "Offer", "price": price, "priceCurrency": "USD",
                                    "url": f"{origin}/{slug}/"}})
    for slug, label in labels.items():
        children = (list(labels)[1:] if slug == "encastre" else
                    [model for model, data in models.items() if data[3] == slug])
        cover = next((data[2] for data in models.values() if data[3] == slug), models[SET][2])
        landing(slug, label, f"تصفّح {label} وشاهد الموديلات والتشطيبات والأسعار.", cover,
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
