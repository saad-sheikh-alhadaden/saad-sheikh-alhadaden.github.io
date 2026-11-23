"""Add kitchen mixers to the assembled storefront."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

root = Path("storefront")
origin = "https://saad-customer-app.onrender.com"


def replace_once(html, pattern, replacement):
    html, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Missing storefront markup: {pattern}")
    return html


def publish_mixer(slug, title, model, description, price, labels, photo_count, keywords, after_card=None, italian=True):
    name = f"{title} — {model}"
    counts = dict.fromkeys(labels, photo_count) if isinstance(photo_count, int) else photo_count
    images = {
        finish: [f"/assets/{slug}-{finish.lower().replace(' ', '-')}-{index:02}.webp" for index in range(1, counts[finish] + 1)]
        for finish in labels
    }
    default_finish = next(iter(labels))
    cover = images[default_finish][0]
    gallery = [asset for photos in images.values() for asset in photos]

    def thumbnail(image, finish, index):
        hidden = " hidden" if finish != default_finish else ""
        pressed = str(image == cover).lower()
        return (
            f'<button type="button" data-gallery-src="{image}" data-gallery-color="{finish}" '
            f'data-width="790" data-height="988" aria-label="{name} · {finish} · {index}" '
            f'aria-pressed="{pressed}"{hidden}><img src="{image}" width="64" height="80" alt="" loading="lazy"></button>'
        )

    thumbs = "".join(thumbnail(image, finish, index)
                     for finish, photos in images.items() for index, image in enumerate(photos, 1))
    options = "".join(
        f'<button class="option" type="button" data-color="{finish}" '
        f'aria-pressed="{str(finish == default_finish).lower()}"><bdi>{finish}</bdi></button>'
        for finish in labels
    )

    template_path = root / "rs-kitchen-mixer/index.html"
    template = template_path.read_text()
    section_pattern = r'<section id="rs-kitchen-mixer" class="vanity-detail"[^>]*>.*?</section>'
    section = re.search(section_pattern, template, re.S)[0]
    section = replace_once(section, r'<section[^>]*>', f'<section id="{slug}" class="vanity-detail" data-nosnippet hidden>')
    section = replace_once(section, r'(<div class="product-image">)<img [^>]*>',
                           lambda match: match[1] + f'<img src="{cover}" alt="{name} باللون {labels[default_finish]}" width="790" height="988">')
    section = replace_once(section, r'<h1>.*?</h1>', f'<h1>{name}</h1>')
    section = replace_once(section, r'<p class="product-description">.*?</p>', f'<p class="product-description">{description}</p>')
    section = replace_once(section, r'<div class="product-gallery">.*?</div>', f'<div class="product-gallery">{thumbs}</div>')
    section = replace_once(section, r'<div class="options"[^>]*>.*?</div>',
                           f'<div class="options" aria-label="الألوان المتوفرة">{options}</div>')
    section = replace_once(section, r'(<p class="price-tag"[^>]*>).*?(</p>)', lambda match: f'{match[1]}${price}{match[2]}')
    if not italian:
        section = re.sub(r'<p class="origin"[^>]*>.*?</p>', "", section)
        section = re.sub(r'<img class="milano-brand"[^>]*>', "", section)
    card = (f'<a class="hero mixer-product" href="/{slug}/">'
            f'<img src="{cover}" alt="{name} باللون {labels[default_finish]}" width="790" height="988">'
            f'<div class="mixer-product-copy"><strong>{title}</strong>'
            f'<small><bdi lang="en" dir="ltr">{model}</bdi></small>'
            f'<span dir="ltr">${price}</span></div></a>')

    registry_pattern = r'<script src="/(assets/storefront-[a-f0-9]+\.js)"'
    home = (root / "index.html").read_text()
    old_registry = re.search(registry_pattern, home)[1]
    registry = (root / old_registry).read_text()
    product = {
        "name": name,
        "search": f"{name} خلاطات مجلى {keywords} {price}",
        "price": price, "category": "kitchen", "defaultColor": default_finish,
        "colorLabels": labels, "images": {finish: photos[0] for finish, photos in images.items()},
        "favoriteKey": f"saad-saved-{slug}",
    }
    registry = replace_once(registry, r'const products = \{',
                            lambda match: match[0] + f'\n  "{slug}": {json.dumps(product, ensure_ascii=False)},')
    new_registry = f"assets/storefront-{hashlib.sha256(registry.encode()).hexdigest()[:12]}.js"

    for asset in gallery:
        shutil.copyfile(Path(__file__).with_name(Path(asset).name), root / asset[1:])
    (root / new_registry).write_text(registry)

    for page in root.rglob("index.html"):
        html = page.read_text()
        if old_registry not in html:
            continue
        if not re.search(section_pattern, html, re.S):
            page.write_text(html.replace(old_registry, new_registry))
            continue
        html = replace_once(html, section_pattern, lambda match: match[0] + "\n" + section)
        anchor = rf'<a class="hero mixer-product" href="/{after_card or "gessi-venti-semi-pro"}/">.*?</a>'
        html = replace_once(html, anchor, lambda match: match[0] + card if after_card else card + match[0])
        for attribute in ("data-saved", "data-search-product"):
            link = f'<a href="/{slug}/" {attribute}="{slug}" hidden>{name}</a>'
            html = replace_once(html, rf'<a href="/rs-kitchen-mixer/" {attribute}="rs-kitchen-mixer" hidden>.*?</a>',
                                lambda match: match[0] + link)
        page.write_text(html.replace(old_registry, new_registry))

    updated_template = template_path.read_text()
    head, body = updated_template.split('<div class="app">', 1)
    old_schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
    data = json.loads(old_schema[1])
    old_url, old_cover = data["url"], data["image"][0]
    url = f"{origin}/{slug}/"
    head = (head.replace('data-screen="rs-kitchen-mixer"', f'data-screen="{slug}"')
            .replace(old_url, url).replace(old_cover, origin + cover)
            .replace(data["name"], name).replace(data["description"], description))
    if not italian:
        data.pop("countryOfOrigin", None)
    data.update(name=name, description=description, sku=slug, url=url, color=list(labels),
                image=[origin + image for image in gallery])
    data["offers"].update(price=price, url=url)
    head = replace_once(head, r'(<script type="application/ld\+json">).*?(</script>)',
                        lambda match: match[1] + json.dumps(data, ensure_ascii=False) + match[2])
    body = body.replace('<section id="rs-kitchen-mixer" class="vanity-detail">',
                        '<section id="rs-kitchen-mixer" class="vanity-detail" data-nosnippet hidden>', 1)
    body = body.replace(f'<section id="{slug}" class="vanity-detail" data-nosnippet hidden>',
                        f'<section id="{slug}" class="vanity-detail">', 1)
    destination = root / slug / "index.html"
    destination.parent.mkdir()
    destination.write_text(head + '<div class="app">' + body)

    image_index = root / "product-images.xml"
    if image_index.is_file():
        sitemap_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        image_namespace = "http://www.google.com/schemas/sitemap-image/1.1"
        ET.register_namespace("", sitemap_namespace)
        ET.register_namespace("image", image_namespace)
        tree = ET.parse(image_index)
        entry = ET.SubElement(tree.getroot(), f"{{{sitemap_namespace}}}url")
        ET.SubElement(entry, f"{{{sitemap_namespace}}}loc").text = url
        for asset in gallery:
            photo = ET.SubElement(entry, f"{{{image_namespace}}}image")
            ET.SubElement(photo, f"{{{image_namespace}}}loc").text = origin + asset
        tree.write(image_index, encoding="utf-8", xml_declaration=True)


publish_mixer(
    "ray-ban-kitchen-mixer", "خلاط مجلى ريبان", "Kitchen Mixer Ray-Ban",
    (
        "خلاط مجلى إيطالي بتصميم انسيابي وخرطوم سيليكون مرن بقوس مرتفع. "
        "يعود رأس الرشّاش القابل للسحب إلى مكانه بتثبيت مغناطيسي، ويتبدّل بزر واحد بين التدفق العادي والرش. "
        "يتيح المقبض الأحادي ضبط حرارة الماء وقوة التدفق، فيما يمنح دوران الخلاط 360° مرونة إضافية للأحواض المزدوجة."
    ),
    350, {"White": "أبيض", "Rose Gold": "روز غولد"}, 9,
    "ray ban rayban أبيض white روز غولد rose gold magnetic docking",
)
publish_mixer(
    "strass-kitchen-mixer", "خلاط مجلى مرصّع بالستراس الفاخر", "Kitchen Mixer Strass",
    "خلاط مجلى إيطالي بخطوط هندسية مربّعة وذراع علوي مرصّع بحبّات الستراس، تتلألأ مع الضوء وتبرز تفاصيل التصميم.",
    475, {"Gold": "ذهبي", "Black": "أسود"}, 5,
    "strass ستراس مرصع مرصّع gold ذهبي black أسود",
    after_card="rs-kitchen-mixer",
)

publish_mixer(
    "milano-quadro-kitchen-mixer", "خلاط مجلى ميلانو كوادرو", "Kitchen Mixer Milano Quadro",
    "خلاط مجلى بتصميم إيطالي يجمع بين جسم مربّع وقوس معدني مخدّد، بلمسة من الكروم اللامع.",
    520, {"Chrome": "كروم"}, 6, "milano quadro chrome كروم ميلانو كوادرو",
    after_card="strass-kitchen-mixer",
)

publish_mixer(
    "st-685-kitchen-mixer", "خلاط مجلى ثلاثي", "Kitchen Mixer S.T 685",
    "خلاط مجلى برقبتين مستقلّتين، إحداهما للمياه الساخنة والباردة، والثانية مخصّصة لمياه الشرب.",
    200, {"Brushed Gold": "ذهبي مصقول بالفرشاة", "Black": "أسود", "Chrome": "كروم", "Satin": "ساتان"},
    {"Brushed Gold": 9, "Black": 9, "Chrome": 9, "Satin": 8},
    "st685 st 685 ثلاثي مياه الشرب براش غولد أسود كروم ساتان",
    after_card="milano-quadro-kitchen-mixer", italian=False,
)


# Use the shared overlay style for older product cards from the storefront archive.
legacy_favorite = re.compile(
    r'(<div class="product-image"[^>]*>\s*<img [^>]*>\s*<button class=")save("(?=[^>]*\sdata-save\b))'
)
# Move archived kitchen mixer galleries before the title and description.
kitchen_detail = re.compile(r'<section\b[^>]*\bclass="vanity-detail"[^>]*>.*?</section>', re.S)
photo_strip = re.compile(r'<div class="product-gallery"[^>]*>.*?</div>', re.S)
info_and_category = re.compile(r'(<div class="product-info">)(\s*<p class="category">خلاطات مجلى</p>)')


def format_kitchen_detail(match):
    section = match[0]
    if '<p class="category">خلاطات مجلى</p>' not in section:
        return section
    section = section.replace(">", " data-kitchen-mixer>", 1)
    if not info_and_category.search(section):
        return section
    gallery = photo_strip.search(section)
    if gallery is None:
        return section
    section = section[:gallery.start()] + section[gallery.end():]
    return info_and_category.sub(
        lambda info: info[1] + "\n            " + gallery[0] + info[2], section, count=1
    )


for page in root.rglob("index.html"):
    html = page.read_text()
    updated = legacy_favorite.sub(r"\1circle\2", html)
    updated = kitchen_detail.sub(format_kitchen_detail, updated)
    if updated != html:
        page.write_text(updated)


# Attach the catalog-wide photo strip to pages using the shared storefront registry.
gallery_assets = Path(__file__).resolve().parent.parent
strip_tags = []
for suffix in ("css", "js"):
    source = gallery_assets / f"storefront-gallery-strip.{suffix}"
    payload = source.read_bytes()
    name = f"{source.stem}-{hashlib.sha256(payload).hexdigest()[:12]}.{suffix}"
    (root / "assets" / name).write_bytes(payload)
    strip_tags.append(f'<link rel="stylesheet" href="/assets/{name}">' if suffix == "css"
                      else f'<script defer src="/assets/{name}"></script>')

storefront_script = re.compile(r'<script src="/assets/storefront-[a-f0-9]+\.js"></script>')
for page in root.rglob("index.html"):
    html = page.read_text()
    updated = storefront_script.sub(lambda match: match[0] + "".join(strip_tags), html, count=1)
    if updated != html:
        page.write_text(updated)
