"""Extend the packaged storefront using the existing floor toilet detail layout."""

from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
from shutil import copyfile

SOFA = "floor-toilet-sofa"
HOST = "https://saad1910.com"
COLORS = {"PINK": "زهري", "WHITE": "أبيض", "GRAY": "رمادي", "BLACK": "أسود", "GOLD": "دهبي"}


def add_stand_toilets(output):
    source = Path(__file__).parent / "stand-toilets"
    products = json.loads((source / "products.json").read_text())
    template = (output / SOFA / "index.html").read_text()
    section_pattern = re.compile(r'<section id="floor-toilet-sofa".*?</section>', re.S)
    detail = section_pattern.search(template)[0]
    description = re.search(r'<p class="product-description">(.*?)</p>', detail)[1]
    header, body = template.split('<div class="app">', 1)
    schema_pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)')
    original_schema = json.loads(schema_pattern.search(header)[2])
    cards, searches, favorites, shares, catalog, urls, images = [], [], [], [], [], [], []

    for p in products:
        slug, ar, en, color, price = (p[key] for key in ("slug", "ar", "en", "color", "price"))
        title = f"{en} — {ar}"
        path = f"/{slug}/"
        image = f"/assets/{slug}.webp"
        copyfile(source / (slug + ".webp"), output / image.lstrip("/"))
        schema = dict(original_schema, name=title, description=p["description"],
                      sku=slug, url=HOST + path, image=[HOST + image], color=[color],
                      offers=dict(original_schema["offers"], price=price, url=HOST + path))
        head = schema_pattern.sub(lambda m: m[1] + json.dumps(schema, ensure_ascii=False) + m[3], header, count=1)

        def personalize(fragment):
            return (fragment.replace(description, escape(p["description"]))
                    .replace("تواليت أرضي كنباية — Floor toilet sofa", escape(title))
                    .replace("/assets/floor-toilet-sofa-white-01.webp", image)
                    .replace(SOFA, slug))

        panel = re.sub(r'<button type="button" data-gallery-src="[^"]+-0[234]\.webp".*?</button>', '', detail)
        panel = personalize(panel).replace("WHITE", color).replace("باللون أبيض", "باللون " + COLORS[color])
        panel = panel.replace('data-screen-heading>تواليت أرضي كنباية', 'data-screen-heading dir="ltr">' + escape(en))
        panel = panel.replace('dir="auto">Floor toilet sofa', 'dir="rtl">' + escape(ar)).replace("$250", f"${price}")
        page = personalize(head) + '<div class="app">' + section_pattern.sub(lambda _: panel, body, count=1)
        dest = output / slug
        dest.mkdir(exist_ok=True)
        (dest / "index.html").write_text(page)
        cards.append(f'<a class="hero mixer-product" href="{path}"><img src="{image}" alt="{escape(title)}" width="790" height="988" loading="lazy" decoding="async"><div class="mixer-product-copy"><strong dir="ltr">{escape(en)}</strong><small>{escape(ar)}</small><span dir="ltr">${price}</span></div></a>')
        searches.append(f'<a href="{path}" data-search-product="{slug}" hidden>{escape(title)}</a>')
        favorites.append(f'<a href="{path}" data-saved="{slug}" hidden>{escape(title)}</a>')
        share = {slug: {"path": path, "title": title + " | شركة سعد شيخ الحدادين", "label": "مشاركة المنتج"}}
        shares.append(escape(json.dumps(share, ensure_ascii=False, separators=(",", ":"))[1:-1]))
        product = dict(name=title, search=f"{title} {color} {COLORS[color]} {price}", price=price,
                       category="stand-toilets", defaultColor=color, colorLabels={color: COLORS[color]},
                       images={color: image}, favoriteKey="saad-saved-" + slug)
        catalog.append(json.dumps(slug) + ": " + json.dumps(product, ensure_ascii=False))
        urls.append(f"<url><loc>{HOST}{path}</loc></url>")
        images.append(f"<url><loc>{HOST}{path}</loc><image:image><image:loc>{HOST}{image}</image:loc></image:image></url>")

    assets = output / "assets"
    copyfile(source / "wall-category.webp", assets / "wall-category.webp")
    css = (source / "categories.css").read_bytes()
    css_name = "toilet-categories-" + sha256(css).hexdigest()[:12] + ".css"
    (assets / css_name).write_bytes(css)
    choices = [("stand-toilets", "تواليتات أرضية", "Stand toilets", "floor-toilet-sofa-white-01.webp"),
               ("wall-toilets", "تواليتات معلقة", "Wall toilets", "wall-category.webp")]

    def labels(ar, en):
        return f'<span lang="ar">{ar}</span> <bdi lang="en" dir="ltr">{en}</bdi>'

    def heading(ar, en):
        return f'<h2 data-screen-heading class="toilet-heading">{labels(ar, en)}</h2>'

    landing = heading("تواليت", "Toilet") + '<div class="toilet-choices">'
    for section_id, ar, en, filename in choices:
        image = "/assets/" + filename
        landing += (f'<a class="toilet-choice" href="#{section_id}">'
                    f'<div class="toilet-choice-photo" style="--scene:url({image})">'
                    f'<img src="{image}" alt="" loading="lazy"></div>'
                    f'<div class="toilet-choice-label">{labels(ar, en)}</div></a>')
    landing += "</div>"
    landing_pattern = re.compile(r'(<section\b[^>]*\bid="toilets"[^>]*>).*?</section>', re.S)
    old_js = re.search(r'src="/assets/(storefront-[0-9a-f]+\.js)"', template)[1]
    script = (assets / old_js).read_text()
    anchor = '  "floor-toilet-sofa": {'
    assert script.count(anchor) == 1
    updated = script.replace(anchor, ",\n".join(catalog) + ",\n" + anchor)
    new_js = "storefront-" + sha256(updated.encode()).hexdigest()[:12] + ".js"
    (assets / new_js).write_text(updated)
    card = re.search(r'<a class="hero mixer-product" href="/floor-toilet-sofa/".*?</a>', template)[0]
    for page in output.rglob("index.html"):
        html = page.read_text()
        if old_js not in html:
            continue
        html = html.replace(old_js, new_js).replace(card, card + "".join(cards))
        html = re.sub(r'(<link rel="stylesheet" href="/assets/[^"]+"[^>]*>)',
                      lambda m: m[1] + f'<link rel="stylesheet" href="/assets/{css_name}">', html, count=1)
        html = landing_pattern.sub(lambda m: m[1] + landing + "</section>", html)
        for _, ar, en, _ in choices:
            html = html.replace(f"<h2 data-screen-heading>{ar} <bdi>{en}</bdi></h2>", heading(ar, en))
        for attr, entries in (("data-saved", favorites), ("data-search-product", searches)):
            marker = f'<a href="/{SOFA}/" {attr}='
            html = html.replace(marker, "".join(entries) + marker)
        key = '&quot;floor-toilet-sofa&quot;:'
        page.write_text(html.replace(key, ",".join(shares) + "," + key))
    for filename, entries in (("sitemap.xml", urls), ("product-images.xml", images)):
        file = output / filename
        file.write_text(file.read_text().replace("</urlset>", "".join(entries) + "</urlset>"))
