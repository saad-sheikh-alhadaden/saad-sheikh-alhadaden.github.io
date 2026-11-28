"""Extend the packaged storefront using the existing floor toilet detail layout."""

from hashlib import sha256
from itertools import groupby
from html import escape
import json
from pathlib import Path
import re
from shutil import copyfile

SOFA = "floor-toilet-sofa"
HOST = "https://saad1910.com"
COLORS = {"BLUE": "أزرق", "RED": "أحمر", "YELLOW": "أصفر", "ROSE GOLD": "روز غولد", "BLACK & GOLD": "أسود ودهبي", "GOLD & BLACK": "دهبي وأسود", "WHITE & GOLD": "أبيض ودهبي", "CHROME": "كروم", "PINK": "زهري", "WHITE": "أبيض", "GRAY": "رمادي", "BLACK": "أسود", "GOLD": "دهبي"}


def add_stand_toilets(output):
    source = Path(__file__).parent / "stand-toilets"
    products = json.loads((source / "products.json").read_text())
    wall_source = source.parent / "wall-toilets"
    wall_products = json.loads((wall_source / "products.json").read_text())
    color_trio = {"wall-toilet-blue", "wall-toilet-red", "wall-toilet-yellow"}
    bubbles = [item for item in wall_products if item["slug"].startswith("wall-toilet-bubbles-")]
    italian_colors = [item for item in wall_products if item["slug"] in color_trio]
    st_models = [item for item in wall_products if item["slug"].startswith("wall-toilet-st-")]
    variants_by_slug = {item["slug"]: family for family in (st_models, bubbles, italian_colors) for item in family}
    card_rows = {slug: "italian" for slug in color_trio}
    card_rows.update({item["slug"]: "bubbles" for item in bubbles if item["color"] in {"CHROME", "GOLD", "ROSE GOLD"}})
    black_bubbles = "wall-toilet-bubbles-g01-02"
    signature_revision = sha256((wall_source / f"{black_bubbles}.webp").read_bytes()).hexdigest()[:12]

    def image_url(slug):
        if slug == black_bubbles:
            return f"/assets/{slug}-{signature_revision}.webp"
        return f"/assets/{slug}.webp"

    wall_cards = []
    template = (output / SOFA / "index.html").read_text()
    section_pattern = re.compile(r'<section id="floor-toilet-sofa".*?</section>', re.S)
    detail = section_pattern.search(template)[0]
    description = re.search(r'<p class="product-description">(.*?)</p>', detail)[1]
    header, body = template.split('<div class="app">', 1)
    schema_pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)')
    original_schema = json.loads(schema_pattern.search(header)[2])
    cards, searches, favorites, shares, catalog, urls, images = [], [], [], [], [], [], []

    features = ('<p class="toilet-features">غطاء من الميلامين مقاوم للكسر، ونظام شطف بلا حواف داخلية '
                '(<bdi>Rimless</bdi>) بتقنية مضادّة للبكتيريا يسهّل التنظيف اليومي.</p>'
                '<div class="toilet-warranty"><strong>كفالة ثبات اللون</strong><span>خمس سنوات</span></div>')

    entries = [(p, "stand-toilets", source, cards) for p in products]
    entries.extend((p, "wall-toilets", wall_source, wall_cards) for p in wall_products)
    for p, category, image_dir, category_cards in entries:
        slug, ar, en, color, price = (p[key] for key in ("slug", "ar", "en", "color", "price"))
        title = f"{en} — {ar}"
        path = f"/{slug}/"
        image = image_url(slug)
        copyfile(image_dir / (slug + ".webp"), output / image.lstrip("/"))
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
        if slug in variants_by_slug:
            swatches = []
            thumbnails = []
            for variant in variants_by_slug[slug]:
                current = ' aria-current="page"' if variant["slug"] == slug else ""
                label = escape(COLORS[variant["color"]])
                if variant in st_models:
                    code = variant["en"].split()[-1]
                    finish = variant["ar"].removeprefix("تواليت معلق ")
                    label = f'<bdi>{escape(code)}</bdi> {escape(finish)}'
                thumbnails.append(
                    f'<a href="/{variant["slug"]}/" aria-label="{escape(variant["en"])}"{current}>'
                    f'<img src="{image_url(variant["slug"])}" alt="{escape(variant["ar"])}" width="52" height="65"></a>'
                )
                swatches.append(
                    f'<a href="/{variant["slug"]}/" data-finish="{variant["color"]}"{current}>'
                    f'<span>{label}</span></a>' 
                )
            strip = '<nav class="toilet-thumbnails" aria-label="صور الموديلات">' + "".join(thumbnails) + '</nav>'
            panel = re.sub(r'<div class="product-gallery">.*?</div>', lambda _: strip, panel, count=1)
            picker = '<nav class="wall-variant-colors" aria-label="الألوان المتوفرة">' + "".join(swatches) + '</nav>'
            panel = re.sub(r'<div class="options"[^>]*>.*?</div>', lambda _: picker, panel, count=1)
        if p.get("origin") == "Italy":
            origin_badge = ('<p class="origin" dir="ltr" lang="en">Made in Italy</p>'
                            '<img class="milano-brand" src="/assets/milano-italy-bronze-01dae327f89e.webp" '
                            'alt="Milano Italy" width="679" height="328">')
            panel = panel.replace('<p class="price-tag"', origin_badge + '<p class="price-tag"', 1)
        if category == "wall-toilets":
            panel = panel.replace('/#stand-toilets">تواليتات أرضية', '/#wall-toilets">تواليتات معلقة')
        panel = panel.replace('<div class="qty">', features + '<div class="qty">', 1)
        page = personalize(head) + '<div class="app">' + section_pattern.sub(lambda _: panel, body, count=1)
        dest = output / slug
        dest.mkdir(exist_ok=True)
        (dest / "index.html").write_text(page)
        if category == "wall-toilets":
            card_name = f'<strong lang="ar" dir="rtl">{escape(ar)}</strong><small lang="en" dir="ltr">{escape(en)}</small>'
        else:
            card_name = f'<strong dir="ltr">{escape(en)}</strong><small>{escape(ar)}</small>'
        category_cards.append(f'<a class="hero mixer-product" href="{path}"><img src="{image}" alt="{escape(title)}" width="790" height="988" loading="lazy" decoding="async"><div class="mixer-product-copy">{card_name}<span dir="ltr">${price}</span></div></a>')
        searches.append(f'<a href="{path}" data-search-product="{slug}" hidden>{escape(title)}</a>')
        favorites.append(f'<a href="{path}" data-saved="{slug}" hidden>{escape(title)}</a>')
        share = {slug: {"path": path, "title": title + " | شركة سعد شيخ الحدادين", "label": "مشاركة المنتج"}}
        shares.append(escape(json.dumps(share, ensure_ascii=False, separators=(",", ":"))[1:-1]))
        product = dict(name=title, search=f"{title} {color} {COLORS[color]} {price}", price=price,
                       category=category, defaultColor=color, colorLabels={color: COLORS[color]},
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
    nav_file = re.search(r'src="/assets/(storefront-navigation-[a-f0-9]+\.js)"', template)[1]
    nav = (assets / nav_file).read_text()
    anchor_nav = '    const filtered = group === "cabinet-luxury" && bandButton;'
    assert nav.count(anchor_nav) == 1
    nav = nav.replace(anchor_nav, """    if (group === "wall-toilets" || group === "stand-toilets") {
      let origin = model;
      try {
        const saved = JSON.parse(sessionStorage.getItem(positionKey));
        const slug = saved?.href.split("/")[1];
        if (saved?.section === group && products[slug]?.category === group) origin = slug;
      } catch {}
      returnLink.href = "/?model=" + encodeURIComponent(origin) + "#" + group;
      returnLink.setAttribute("aria-label", "الرجوع لقائمة الموديلات");
      return;
    }
""" + anchor_nav)
    new_nav = "storefront-navigation-" + sha256(nav.encode()).hexdigest()[:12] + ".js"
    (assets / new_nav).write_text(nav)
    card = re.search(r'<a class="hero mixer-product" href="/floor-toilet-sofa/".*?</a>', template)[0]
    wall_grid = []
    for grouped, items in groupby(zip(wall_products, wall_cards), key=lambda item: card_rows.get(item[0]["slug"])):
        content = "".join(card_html for _, card_html in items)
        wall_grid.append(f'<div class="wall-color-row">{content}</div>' if grouped else content)
    for page in output.rglob("index.html"):
        html = page.read_text()
        if old_js not in html:
            continue
        if section_pattern.search(html):
            sofa_panel = detail.replace(description, description.split(" غطاؤه")[0])
            sofa_panel = sofa_panel.replace('<div class="qty">', features + '<div class="qty">', 1)
            html = section_pattern.sub(lambda _: sofa_panel, html, count=1)
        html = html.replace(old_js, new_js).replace(nav_file, new_nav).replace(card, card + "".join(cards))
        html = re.sub(r'(<link rel="stylesheet" href="/assets/[^"]+"[^>]*>)',
                      lambda m: m[1] + f'<link rel="stylesheet" href="/assets/{css_name}">', html, count=1)
        html = landing_pattern.sub(lambda m: m[1] + landing + "</section>", html)
        for _, ar, en, _ in choices:
            html = html.replace(f"<h2 data-screen-heading>{ar} <bdi>{en}</bdi></h2>", heading(ar, en))
        wall_heading = heading("تواليتات معلقة", "Wall toilets")
        html = html.replace(wall_heading, wall_heading + '<div class="cabinet-gallery" data-toilet-cards>'
                            + "".join(wall_grid) + "</div>")
        for attr, entries in (("data-saved", favorites), ("data-search-product", searches)):
            marker = f'<a href="/{SOFA}/" {attr}='
            html = html.replace(marker, "".join(entries) + marker)
        key = '&quot;floor-toilet-sofa&quot;:'
        page.write_text(html.replace(key, ",".join(shares) + "," + key))
    for filename, entries in (("sitemap.xml", urls), ("product-images.xml", images)):
        file = output / filename
        file.write_text(file.read_text().replace("</urlset>", "".join(entries) + "</urlset>"))
