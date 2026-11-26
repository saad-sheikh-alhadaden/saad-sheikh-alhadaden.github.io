"""Add kitchen mixers to the assembled storefront."""
import hashlib
from html import escape, unescape
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET

root = Path("storefront")
origin = "https://saad-customer-app.onrender.com"


def replace_once(html, pattern, replacement):
    html, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Missing storefront markup: {pattern}")
    return html


def publish_mixer(slug, title, model, description, price, labels, photo_count, keywords, after_card=None, italian=True, model_finish=None, brand=None, brand_logo=None, finish_strip=False, category="kitchen", sizes=None, pattern=None, pedestal_size=None, material=None, cover_index=1, basin_code=None):
    is_pedestal = category == "freestanding-pedestal-basins"
    name = f"{model} — {title}" if is_pedestal else f"{title} — {model}"
    if basin_code:
        name = f"{title} — {basin_code}"
    counts = dict.fromkeys(labels, photo_count) if isinstance(photo_count, int) else photo_count
    photo_suffix = "-signed" if category == "decorative-vessel-basins" else ""
    images = {
        finish: [f"/assets/{slug}-{finish.lower().replace(' ', '-')}{photo_suffix}-{index:02}.webp" for index in range(1, counts[finish] + 1)]
        for finish in labels
    }
    for photos in images.values():
        photos.insert(0, photos.pop(cover_index - 1))
    default_finish = next(iter(labels))
    prices = price if isinstance(price, dict) else None
    if prices:
        if set(prices) != set(labels):
            raise ValueError(f"Missing or unexpected finish price for {slug}")
        price = prices[default_finish]
    card_price = f"${min(prices.values())}–${max(prices.values())}" if prices and min(prices.values()) != max(prices.values()) else f"${price}"
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

    gallery_markup = f'<div class="product-gallery">{thumbs}</div>'
    options_markup = f'<div class="options" aria-label="الألوان المتوفرة">{options}</div>'
    if finish_strip:
        # The shared variant strip selects the finish and updates its price.
        gallery_markup = ""
    if model_finish:
        # The shared variant strip builds a selectable thumbnail for each model.
        gallery_markup = ""
        options = "".join(
            f'<button type="button" class="option" data-color="{key}" aria-pressed="{str(key == default_finish).lower()}">{label}</button>'
            for key, label in labels.items()
        )
        options_markup = f'<p>اختر الموديل</p><div class="options" data-package-options aria-label="اختر الموديل">{options}</div>'
    cover_label = labels[default_finish] if not model_finish else "الكروم"
    photo_alt = escape(f"{title}، {sizes[default_finish]}" if sizes else f"{name} باللون {cover_label}", quote=True)
    template_path = root / "rs-kitchen-mixer/index.html"
    template = template_path.read_text()
    section_pattern = r'<section id="rs-kitchen-mixer" class="vanity-detail"[^>]*>.*?</section>'
    section = re.search(section_pattern, template, re.S)[0]
    section = replace_once(section, r'<section[^>]*>', f'<section id="{slug}" class="vanity-detail" data-nosnippet hidden>')
    section = replace_once(section, r'(<div class="product-image">)<img [^>]*>',
                           lambda match: match[1] + f'<img src="{cover}" alt="{photo_alt}" width="790" height="988">')
    heading = f'<h1>{name}</h1>'
    if category == "mixers":
        section = section.replace('<p class="category">خلاطات مجلى</p>', '<p class="category">خلاطات المغاسل</p>')
        heading = f'<h1>{title}</h1><p class="product-model-name" lang="en" dir="ltr">{model}</p>'
    if category in ("stand-toilets", "wall-toilets"):
        label = {"stand-toilets": "تواليتات أرضية", "wall-toilets": "تواليتات معلقة"}[category]
        section = section.replace(' data-nosnippet hidden>', ' data-toilet-chair data-nosnippet hidden>', 1)
        section = section.replace('<p class="category">خلاطات مجلى</p>', f'<p class="category"><a href="/#{category}">{label}</a></p>')
        section = re.sub(r'<div class="warranty">.*?</div>', '', section, flags=re.S)
        heading = f'<h1>{title}</h1><p class="product-model-name" lang="en" dir="ltr">{model}</p>'
    if category in ("porcelain", "decorative-vessel-basins"):
        label = "مغاسل بورسلان" if category == "porcelain" else "أجران مغسلة ديكور"
        section = replace_once(section, r'<p class="category">.*?</p>',
                               f'<p class="category"><a href="/{category}/">{label}</a></p>')
        section = re.sub(r'<p class="product-model-name"[^>]*>.*?</p>', '', section, flags=re.S)
        section = re.sub(r'<div class="warranty">.*?</div>', '', section, flags=re.S)
        heading = f'<h1>{title}</h1>'
        options_markup = f'<p>المقاس <bdi dir="ltr">{model}</bdi></p><p>اللون {labels[default_finish]}</p>'
        if basin_code:
            heading += f'<p class="product-model-name"><bdi lang="en" dir="ltr">{basin_code}</bdi></p>'
            options_markup = (
                f'<p>المقاس <bdi dir="ltr">{model}</bdi></p>'
                f'<p>اللون <bdi lang="en" dir="ltr">{escape(labels[default_finish])}</bdi></p>'
            )
            gallery_markup = ""
    if category == "freestanding-pedestal-basins":
        section = replace_once(section, r'<p class="category">.*?</p>',
                               '<p class="category"><a href="/freestanding-pedestal-basins/">مغاسل برميل ديكور</a></p>')
        section = re.sub(r'<p class="product-model-name"[^>]*>.*?</p>', '', section, flags=re.S)
        section = re.sub(r'<img class="milano-brand"[^>]*>', '', section)
        heading = f'<h1><bdi lang="en" dir="ltr">{model}</bdi></h1><p class="product-model-name" lang="ar" dir="rtl">{title}</p>'
        options_markup = f'<p>المقاس <bdi dir="ltr">{pedestal_size}</bdi></p><p>اللون <bdi lang="en" dir="ltr">{escape(labels[default_finish])}</bdi></p>'
    if category == "granite":
        section = section.replace(' data-nosnippet hidden>', ' data-granite-basin data-nosnippet hidden>', 1)
        section = replace_once(section, r'<p class="category">.*?</p>',
                               '<p class="category"><a href="/#granite">مغاسل غرانيت</a></p>')
        section = re.sub(r'<div class="warranty">.*?</div>', '', section, flags=re.S)
        section = re.sub(r'<p class="product-model-name"[^>]*>.*?</p>', '', section, flags=re.S)
        heading = f'<h1>{title}</h1>'
        if sizes:
            if set(sizes) != set(labels):
                raise ValueError(f"Missing size for {slug}")
            size_options = "".join(
                f'<button class="option" type="button" data-color="{escape(key, quote=True)}" '
                f'aria-pressed="{str(key == default_finish).lower()}"><bdi dir="ltr">{escape(value)}</bdi></button>'
                for key, value in sizes.items()
            )
            gallery_markup = ""
            options_markup = f'<p>اختر المقاس</p><div class="options" aria-label="المقاس">{size_options}</div>'

    section = replace_once(section, r'<h1\b[^>]*>.*?</h1>', heading)
    section = replace_once(section, r'<p class="product-description">.*?</p>', f'<p class="product-description">{description}</p>')
    section = replace_once(section, r'<div class="product-gallery">.*?</div>', gallery_markup)
    section = replace_once(section, r'<div class="options"[^>]*>.*?</div>',
                           options_markup)
    section = replace_once(section, r'(<p class="price-tag"[^>]*>).*?(</p>)', lambda match: f'{match[1]}${price}{match[2]}')
    if not italian:
        section = re.sub(r'<p class="origin"[^>]*>.*?</p>', "", section)
        section = re.sub(r'<img class="milano-brand"[^>]*>', "", section)
    if brand and not brand_logo:
        section = re.sub(r'<img class="milano-brand"[^>]*>', "", section)
    if brand_logo:
        section = re.sub(r'<img class="milano-brand"[^>]*>', "", section)
        signature = (f'<img class="milano-brand" src="/assets/{brand_logo}" alt="{brand}" '
                     'style="filter:none;height:auto">')
        section = replace_once(section, r'<p class="origin"[^>]*>.*?</p>', lambda match: match[0] + signature)
        shutil.copyfile(Path(__file__).with_name(brand_logo), root / "assets" / brand_logo)
    card_title = f'<bdi lang="en" dir="ltr">{model}</bdi>' if is_pedestal else title
    card_subtitle = f'<bdi lang="ar" dir="rtl">{title}</bdi>' if is_pedestal else f'<bdi lang="en" dir="ltr">{model}</bdi>'
    card_code = ""
    if basin_code:
        code = f'<bdi lang="en" dir="ltr">{basin_code}</bdi>'
        finish_label = f'<bdi lang="en" dir="ltr">{escape(labels[default_finish])}</bdi>'
        if category == "decorative-vessel-basins":
            card_title = f'جرن {code}'
            card_subtitle = finish_label
        else:
            card_code = f'<bdi class="basin-model-code" lang="en" dir="ltr">{basin_code}</bdi>'
            card_subtitle += f' · {finish_label}'
    card = (f'<a class="hero mixer-product" href="/{slug}/">'
            f'<img src="{cover}" alt="{photo_alt}" width="790" height="988">'
            f'<div class="mixer-product-copy"><strong>{card_title}</strong>{card_code}'
            f'<small>{card_subtitle}</small>'
            f'<span dir="ltr">{card_price}</span></div></a>')

    registry_pattern = r'<script src="/(assets/storefront-[a-f0-9]+\.js)"'
    home = (root / "index.html").read_text()
    old_registry = re.search(registry_pattern, home)[1]
    registry = (root / old_registry).read_text()
    product = {
        "name": name,
        "search": f"{name} {keywords} {price}",
        "price": price, "category": category, "defaultColor": default_finish,
        "colorLabels": labels, "images": {finish: photos[0] for finish, photos in images.items()},
        "favoriteKey": f"saad-saved-{slug}",
    }
    if prices:
        product["prices"] = prices
    registry = replace_once(registry, r'const products = \{',
                            lambda match: match[0] + f'\n  "{slug}": {json.dumps(product, ensure_ascii=False)},')
    if category == "granite" and '.replace(/^granite-classic$/' not in registry:
        registry = replace_once(registry, r'(function showScreen\(\) \{\s*const hash = location.hash.slice\(1\))',
                                lambda match: match[1] + '.replace(/^granite-classic$/, "granite")')
    new_registry = f"assets/storefront-{hashlib.sha256(registry.encode()).hexdigest()[:12]}.js"

    for asset in gallery:
        shutil.copyfile(Path(__file__).with_name(Path(asset).name), root / asset[1:])
    (root / new_registry).write_text(registry)

    # Sharing and return-to-collection navigation both use these canonical paths.
    def add_share_path(match):
        pages = json.loads(unescape(match[1]))
        pages[slug] = {
            "path": f"/{slug}/",
            "title": f"{name} | شركة سعد شيخ الحدادين",
            "label": "مشاركة المنتج",
        }
        return f'data-share-pages="{escape(json.dumps(pages, ensure_ascii=False), quote=True)}"'

    for page in root.rglob("index.html"):
        html = page.read_text()
        if old_registry not in html:
            continue
        html = re.sub(r'data-share-pages="([^"]*)"', add_share_path, html, count=1)
        if category == "freestanding-pedestal-basins":
            html = re.sub(
                r'(<section class="panel" id="freestanding-pedestal-basins"[^>]*>\s*<h1>.*?</h1>)'
                r'\s*(?:<p>ستُضاف الموديلات قريباً\.</p>|'
                r'<div class="cabinet-gallery" data-pedestal-cards>(.*?)</div>(?=\s*<a class="contact-card"))',
                lambda match: match[1] + f'<div class="cabinet-gallery" data-pedestal-cards>{match[2] or ""}{card}</div>',
                html, count=1, flags=re.S,
            )
        if not re.search(section_pattern, html, re.S):
            page.write_text(html.replace(old_registry, new_registry))
            continue
        html = replace_once(html, section_pattern, lambda match: match[0] + "\n" + section)
        anchor = rf'<a class="hero mixer-product" href="/{after_card or "gessi-venti-semi-pro"}/">.*?</a>'
        if category == "granite":
            if 'data-granite-cards' in html:
                html = replace_once(html, r'(<div class="cabinet-gallery" data-granite-cards>(?:<a class="hero mixer-product"[^>]*>.*?</a>)*)(</div>)',
                                    lambda match: match[1] + card + match[2])
            else:
                html = replace_once(html, r'(<section class="panel" id="granite"[^>]*>\s*<h1>).*?</h1>',
                                    lambda match: match[1] + 'مغاسل غرانيت <bdi>Granite Basins</bdi></h1>'
                                    + f'<div class="cabinet-gallery" data-granite-cards>{card}</div>')
        elif category in ("stand-toilets", "wall-toilets"):
            html = replace_once(html, rf'(<section class="panel" id="{category}"[^>]*>\s*<h1>.*?</h1>)(?:<div class="cabinet-gallery" data-toilet-cards>(.*?)</div>(?=\s*<a class="action"))?',
                                lambda match: match[1] + f'<div class="cabinet-gallery" data-toilet-cards>{match[2] or ""}{card}</div>')
        elif category == "decorative-vessel-basins":
            html = replace_once(
                html,
                r'(<section class="panel" id="decorative-vessel-basins"[^>]*>\s*<h1>.*?</h1>)'
                r'\s*(?:<p>ستُضاف الموديلات قريباً\.</p>|<div class="cabinet-gallery" data-vessel-cards>(.*?)</div>(?=\s*<a class="contact-card"))',
                lambda match: match[1] + f'<div class="cabinet-gallery" data-vessel-cards>{match[2] or ""}{card}</div>',
            )
        elif basin_code:
            html = replace_once(html, r'(<section class="panel" id="porcelain"[^>]*>\s*<h1>.*?</h1>\s*<div class="cabinet-gallery">)',
                                lambda match: match[1] + card)
        elif category != "freestanding-pedestal-basins":
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
    if brand:
        data["brand"] = {"@type": "Brand", "name": brand}
    data.update(name=name, description=description, sku=slug, url=url, color=[model_finish] if model_finish else list(labels),
                image=[origin + image for image in gallery])
    data["offers"].update(price=price, url=url)
    if category == "porcelain":
        data["material"] = "Porcelain"
    if basin_code:
        data.update(sku=basin_code, model=basin_code, size=model)
    if material:
        data["material"] = material
    if category == "freestanding-pedestal-basins":
        data["size"] = pedestal_size
    if sizes:
        data["size"] = list(sizes.values())
        data["color"] = pattern
    if prices:
        data["offers"] = {"@type": "AggregateOffer", "priceCurrency": "USD",
                          "lowPrice": min(prices.values()), "highPrice": max(prices.values()),
                          "offerCount": len(prices), "url": url}
    head = replace_once(head, r'(<script type="application/ld\+json">).*?(</script>)',
                        lambda match: match[1] + json.dumps(data, ensure_ascii=False) + match[2])
    body = body.replace('<section id="rs-kitchen-mixer" class="vanity-detail">',
                        '<section id="rs-kitchen-mixer" class="vanity-detail" data-nosnippet hidden>', 1)
    if category in ("granite", "porcelain", "freestanding-pedestal-basins", "decorative-vessel-basins"):
        body = re.sub(r'(<section id="rs-kitchen-mixer" class="vanity-detail"[^>]*)(?<! hidden)>',
                      r'\g<1> data-nosnippet hidden>', body, count=1)
    body = replace_once(body, rf'(<section id="{slug}" class="vanity-detail"[^>]*?) data-nosnippet hidden>', r'\1>')
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


def publish_illuminated_granite(slug, pattern, finish_description, keywords, *, prices=None, description=None):
    if (root / slug / "index.html").exists():
        return
    prices = prices or {"60x50": 175, "80x50": 200}
    dimensions = {size: size.replace("x", " × ") for size in prices}
    sizes = {size: f"{label} سم" for size, label in dimensions.items()}
    model = " / ".join(dimensions.values()) + " cm"
    publish_mixer(
        slug, f"مغسلة غرانيت مضاءة {pattern}", model,
        description or f"مغسلة غرانيت {finish_description}، مع إضاءة مدمجة بواجهة المغسلة. معها رف ديكور بالنقشة نفسها للمناشف والإكسسوارات، ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس.",
        prices, sizes, 1,
        f"مغسلة غرانيت مضاءة مع إنارة مدمجة رف مرآة تاتش 60x50 80x50 {keywords}",
        italian=False, category="granite",
        sizes=sizes,
        pattern=pattern,
    )

    add_to_sitemap(slug)


def add_to_sitemap(slug):
    sitemap = root / "sitemap.xml"
    if sitemap.is_file():
        namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        ET.register_namespace("", namespace)
        tree = ET.parse(sitemap)
        entry = ET.SubElement(tree.getroot(), f"{{{namespace}}}url")
        ET.SubElement(entry, f"{{{namespace}}}loc").text = f"{origin}/{slug}/"
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)


def publish_coded_porcelain():
    models = (
        ("st-b809-b-porcelain-basin", "مغسلة معلّقة دائرية أسود", "S.T B809 B", "56 × 47 cm", "Black", 125,
         "مغسلة بورسلان دائرية معلّقة بتشطيب أسود مطفي وحوض بانحناءة ناعمة."),
        ("st-d809-g-porcelain-basin", "مغسلة معلّقة ذهبي", "S.T D809 G", "56 × 47 cm", "Gold", 150,
         "مغسلة بورسلان معلّقة بحوض أبيض وإطار ذهبي، مع خطوط ذهبية أفقية تلتف حول الواجهة."),
        ("st-a811-g-porcelain-basin", "مغسلة معلّقة ذهبي", "S.T A811 G", "53 × 45 cm", "Gold", 150,
         "مغسلة بورسلان معلّقة بحوض أبيض وواجهة ذهبية تتقاطع عليها خطوط هندسية دقيقة."),
        ("st-b809-g-porcelain-basin", "مغسلة معلّقة ذهبي", "S.T B809 G", "56 × 47 cm", "Gold", 150,
         "مغسلة بورسلان معلّقة بحوض أبيض وتشطيب ذهبي، مع شريط هندسي بارز تحت حافة الحوض."),
    )
    # The collection prepends each card, so add the models from last to first.
    for slug, title, code, size, finish, price, description in reversed(models):
        if not (root / slug / "index.html").exists():
            publish_mixer(
                slug, title, size, description, price, {finish: finish.upper()}, 1,
                "مغاسل بورسلان معلقة wall hung porcelain basin",
                italian=False, category="porcelain", basin_code=code,
            )
            add_to_sitemap(slug)


def publish_decorative_vessels():
    models = (
        ("B6", "Black & Gold", "واجهة بنقشة هندسية شعاعية دقيقة وحافة لامعة."),
        ("B1", "Chrome & Black", "واجهة بنقشة مرقّطة وحوض دائري بلمعة واضحة."),
        ("B2", "Chrome", "واجهة بنقشة فسيفساء هندسية غير منتظمة."),
        ("W12", "White & Gold", "حوض أبيض بحافة ذهبية وخطوط متقاطعة على الواجهة."),
        ("B5", "Black & Gold", "حوض أسود لامع مع واجهة ذهبية مصقولة وحافة متداخلة."),
        ("W13", "Chrome & White", "حوض أبيض تقابله واجهة كروم عاكسة بتصميم دائري."),
        ("B4", "Black & Gold", "حوض أسود لامع مع زخارف نباتية على واجهة ذهبية."),
    )
    rectangular = (
        ("B15", "Gold & Black", "حوض أسود مستطيل بحافة ذهبية ونقشة هندسية على الواجهة."),
        ("B16", "Black", "حوض مستطيل بتشطيب أسود مطفي وحواف ناعمة."),
    )
    italian_models = (
        ("01", "Black", "60 × 36 cm", "بيضاوي", "تشطيب أسود مطفي وحافة رفيعة ترتفع تدريجياً عند الطرفين."),
        ("02", "Black", "60 × 37 cm", "بيضاوي", "تشطيب أسود مطفي مع جوانب مستقيمة وحافة رفيعة."),
        ("03", "Black", "44 cm", "دائري", "تشطيب أسود مطفي مع قاعدة مرتفعة للخلاط ضمن الحوض."),
        ("04", "Red", "60 × 36 cm", "بيضاوي", "أحمر بتشطيب مطفي وحافة منحنية ترتفع عند الطرفين."),
        ("05", "Blue", "36 cm", "دائري", "أزرق بتشطيب مطفي وحافة رفيعة وجوانب مستديرة."),
        ("06", "Yellow", "36 cm", "دائري", "أصفر بتشطيب مطفي وحافة رفيعة وجوانب مستديرة."),
        ("07", "Navy Blue", "40 cm", "دائري", "أزرق كحلي مع نقشة متعرّجة على الواجهة الخارجية."),
        ("08", "White", "60 × 40 cm", "بيضاوي", "أبيض لامع بخطوط منحنية وحافة غير متماثلة."),
        ("09", "Craig", "40 cm", "مربّع", "بتشطيب CRAIG وزوايا مستديرة."),
        ("10", "Black", "50 × 38 cm", "مستطيل", "تشطيب أسود مطفي، مع حافة رفيعة وزوايا مستديرة."),
        ("11", "Black", "50 × 33 cm", "مستطيل", "تشطيب أسود مطفي بتصميم ناعم وزوايا بانحناء واسع."),
        ("12", "Black", "56 × 40 cm", "بيضاوي", "تشطيب أسود مطفي وحافة مقوّسة ترتفع عند الطرفين."),
        ("13", "Gray & White", "54 × 38 cm", "بيضاوي", "نقشة متموّجة تجمع الرمادي والأبيض بلمسة لامعة."),
        ("14", "Brushed Gold", "53 × 38 cm", "بيضاوي", "تشطيب ذهبي مفرّش مع خطوط متدرّجة على الواجهة الخارجية."),
        ("15", "Marble White", "60 × 50 cm", "بيضاوي", "تشطيب أبيض رخامي بعروق رمادية تمتدّ على الحوض والواجهة الخارجية."),
    )
    products = (
        *((code, finish, "40 cm", "دائري", detail, 100, False) for code, finish, detail in models),
        *((code, finish, "60 × 42 cm", "مستطيل", detail, 100, False) for code, finish, detail in rectangular),
        *((*model, 180, True) for model in italian_models),
    )
    for code, finish, size, shape, detail, price, italian in products:
        slug = f"{code.lower()}-decorative-vessel-basin"
        if not (root / slug / "index.html").exists():
            publish_mixer(
                slug, "جرن مغسلة ديكور", size,
                f"جرن مغسلة ديكور {shape} للتركيب فوق السطح. {detail}",
                price, {finish: finish.upper()}, 1,
                f"أجران مغسلة ديكور جرن {shape} فوق السطح decorative vessel basin {finish}",
                italian=italian, brand="Milano Italy" if italian else None,
                category="decorative-vessel-basins", basin_code=code,
            )
            add_to_sitemap(slug)


if __name__ == "__main__" and sys.argv[1:] == ["--illuminated-granite"]:
    publish_illuminated_granite(
        "granite-white-gray-illuminated", "أبيض مرخمة بالرمادي", "أبيض مرخّمة بعروق رمادية",
        "أبيض مرخم رمادي illuminated white grey veining",
    )
    publish_illuminated_granite(
        "granite-white-gold-gray-illuminated", "أبيض مرخمة بالذهبي والرمادي",
        "أبيض مرخّمة بعروق ذهبية ورمادية", "أبيض مرخم دهبي ذهبي رمادي illuminated white gold grey veining",
    )
    publish_illuminated_granite(
        "granite-silver-gray-illuminated", "رمادية",
        "رمادي فضّي بتموّجات فاتحة وعروق ناعمة",
        "رمادية رمادي فضي illuminated silver gray",
    )
    publish_illuminated_granite(
        "granite-travertino-illuminated", "ترافنتينو",
        "بنقشة ترافنتينو البيج الفاتح",
        "ترافنتينو ترافرتينو بيج illuminated travertino",
    )
    publish_illuminated_granite(
        "granite-black-kadhabi-illuminated", "أسود كذابي",
        "أسود كذابي", "أسود كذابي illuminated black granite",
    )
    publish_illuminated_granite(
        "granite-black-kadhabi-rounded-illuminated", "لف – أسود كذابي",
        "أسود كذابي بزوايا مدوّرة", "أسود كذابي لف rounded black motion sensor anti-fog",
        prices={"50x45": 175, "60x50": 200, "80x50": 225},
        description=(
            "مغسلة غرانيت أسود كذابي بتصميم لفّ وزوايا مدوّرة، مع إنارة مدمجة تعمل بحساس حركة. "
            "بيجي معها رف سفلي للمناشف والإكسسوارات، ومراية مضاءة بثلاث درجات لونية مع خاصية منع الغباش."
        ),
    )
    publish_illuminated_granite(
        "granite-pearl-white-rounded-illuminated", "لف – أبيض لولي",
        "أبيض لولي بزوايا مدوّرة", "أبيض لولي لف rounded pearl white motion sensor anti-fog",
        prices={"50x45": 175, "60x50": 200, "80x50": 225},
        description=(
            "مغسلة غرانيت باللون الأبيض اللولي، بتصميم لفّ وزوايا مدوّرة وإنارة مدمجة تعمل بحساس حركة. "
            "بيجي معها رف سفلي للمناشف والإكسسوارات، ومراية مضاءة بثلاث درجات لونية مع خاصية منع الغباش."
        ),
    )
    # Keep the stored variant keys and image URLs for existing carts and links.
    wudu_size = {"55x50": "60 × 50 سم"}
    wudu_slug = "granite-white-gray-wudu"
    if not (root / wudu_slug / "index.html").exists():
        publish_mixer(
            wudu_slug, "مغسلة غرانيت وضوء – أبيض مرخم رمادي", "60 × 50 cm",
            "مغسلة وضوء من الغرانيت الأبيض بعروق رمادية، تجمع بين حوض علوي وحيّز سفلي مخصّص لغسل القدمين. تأتي كاملة مع الخلاط وجميع الملحقات.",
            {"55x50": 360}, wudu_size, 1,
            "مغسلة غرانيت وضوء أبيض مرخم رمادي غسل القدمين wudu basin",
            italian=False, category="granite",
            sizes=wudu_size, pattern="أبيض مرخم رمادي",
        )
        add_to_sitemap(wudu_slug)
    wudu_slug = "granite-tundra-gray-wudu"
    if not (root / wudu_slug / "index.html").exists():
        publish_mixer(
            wudu_slug, "مغسلة غرانيت وضوء – توندرا رمادي", "60 × 50 cm",
            "مغسلة وضوء من الغرانيت بتشطيب توندرا رمادي، تجمع بين حوض علوي وحيّز سفلي مخصّص لغسل القدمين. تأتي كاملة مع الخلاط وجميع الملحقات.",
            {"55x50": 360}, wudu_size, 1,
            "مغسلة غرانيت وضوء توندرا رمادي غسل القدمين Tundra Gray wudu basin",
            italian=False, category="granite",
            sizes=wudu_size, pattern="توندرا رمادي",
        )
        add_to_sitemap(wudu_slug)
    revirs_slug = "revirs-porcelain-basin"
    if not (root / revirs_slug / "index.html").exists():
        publish_mixer(
            revirs_slug, "مغسلة REVIRS", "50 × 31 cm",
            "مغسلة بورسلان بيضاء معلّقة، صُنعت بأيادٍ أوروبية بتصميم بسيط وزوايا ناعمة. فتحة مدمجة في الواجهة تُبقي منشفة اليد في متناولك، وعمق 31 سم يناسب الحمّامات ذات المساحة المحدودة.",
            160, {"White": "أبيض"}, 1,
            "REVIRS ريفيرس مغسلة بورسلان بيضاء معلقة حامل منشفة towel slot",
            after_card="st-7901-porcelain-basin", italian=False, category="porcelain",
            sizes={"White": "50 × 31 سم"}, pattern="أبيض",
        )
        add_to_sitemap(revirs_slug)
    piega_slug = "piega-freestanding-basin"
    if not (root / piega_slug / "index.html").exists():
        publish_mixer(
            piega_slug, "مغسلة برميل بييغا", "Freestanding Basin PIEGA",
            "من طيّات ورقة مجعّدة استُلهمت بييغا. مغسلة إيطالية قائمة بذاتها، تتشكّل كتلتها البيضاء من انحناءات غير متماثلة وتفاصيل نحتية دقيقة. يمرّ الضوء على الطيّات فيبرز عمقها، فيما يوازن هدوء الأبيض جرأة الشكل.",
            760, {"White": "WHITE"}, 6, "PIEGA بييغا مغسلة برميل ديكور إيطالية",
            category="freestanding-pedestal-basins", pedestal_size="45 cm", cover_index=3,
        )
        add_to_sitemap(piega_slug)
    die_slug = "die-freestanding-basin"
    if not (root / die_slug / "index.html").exists():
        publish_mixer(
            die_slug, "مغسلة برميل النَرْد 🎲", "Freestanding Basin DIE 🎲",
            "حجرَا نرد، أحدهما فوق الآخر، في مغسلة إيطالية قائمة بذاتها. تلين الحواف المستديرة هندسة المكعّبين، وتلتقط التجويفات الدائرية الضوء والظل. فكرة مرحة بصياغة نحتية هادئة، تمنح الحمّام نقطة ارتكاز يُبنى حولها التصميم.",
            970, {"Craig": "CRAIG"}, 5, "DIE نرد مغسلة برميل ديكور إيطالية dice",
            category="freestanding-pedestal-basins", pedestal_size="43 cm", cover_index=3,
        )
        add_to_sitemap(die_slug)
    prisma_slug = "prisma-freestanding-basin"
    if not (root / prisma_slug / "index.html").exists():
        publish_mixer(
            prisma_slug, "مغسلة برميل بريزما", "Freestanding Basin PRISMA",
            "تستحضر بريزما جرأة الخطوط الحادّة في سيارات لامبورغيني، وتترجمها إلى مغسلة إيطالية قائمة بذاتها. صُنعت من الفولاذ المقاوم للصدأ 304، بتشطيب روز غولد مفرّش يلتقط الضوء بشكل مختلف على كل وجه. ومع تغيّر زاوية النظر، تتبدّل الانعكاسات وتبرز دقّة الحواف.",
            840, {"BRUSHED ROSE GOLD": "BRUSHED ROSE GOLD"}, 6, "PRISMA بريزما مغسلة برميل ديكور إيطالية فولاذ",
            category="freestanding-pedestal-basins", pedestal_size="36 cm", material="Stainless Steel 304",
        )
        add_to_sitemap(prisma_slug)
    roccia_slug = "roccia-freestanding-basin"
    if not (root / roccia_slug / "index.html").exists():
        publish_mixer(
            roccia_slug, "مغسلة برميل روتشيا", "Freestanding Basin ROCCIA",
            "تقدّم ميلانو إيطاليا روتشيا، مغسلة قائمة بذاتها بتكوين أسطواني. يلتقي سطح الترافرتين الفاتح، بخطوطه الحجرية وحافته غير المتماثلة، بقاعدة داكنة تبرز فيها عروق الخشب. يرسم التقاء السطحين خطاً متموّجاً يبرز التباين بين هدوء الحجر ودفء الخشب.",
            720, {"Travertine Wood": "Travertine & Wood"}, 3, "ROCCIA روتشيا مغسلة برميل ديكور ترافرتين خشب Milano Italy",
            brand="Milano Italy", category="freestanding-pedestal-basins", pedestal_size="40 cm",
        )
        add_to_sitemap(roccia_slug)
    nerodoro_slug = "nerodoro-kitchen-mixer"
    if not (root / nerodoro_slug / "index.html").exists():
        publish_mixer(
            nerodoro_slug, "خلاط مجلى نيرودورو", "Kitchen Mixer Nerodoro",
            "يجمع نيرودورو بين قوس أسود مرتفع وجسم بتشطيب ذهبي مفرّش. يوازن الذراع المستقيم انحناءة القوس، فيما يضيف المقبض الجانبي المحزّز تفصيلاً دقيقاً يبرز ملمس التشطيب. خلاط مجلى إيطالي يمنح منطقة الحوض حضوراً واضحاً بخطوط بسيطة.",
            275, {"Brushed Gold": "BRUSHED GOLD"}, 9,
            "Nerodoro نيرودورو خلاط مجلى مطبخ إيطالي ذهبي مفرّش Milano Italy",
            after_card="st-01-kitchen-mixer", brand="Milano Italy",
        )
        add_to_sitemap(nerodoro_slug)
    publish_coded_porcelain()
    publish_decorative_vessels()
    sys.exit(0)



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


publish_mixer(
    "st-885-kitchen-mixer", "خلاط مجلى ثلاثي", "Kitchen Mixer S.T 885",
    "خلاط مجلى ثلاثي بجسم منقوش بنمط هندسي وقوس أسود مرتفع.",
    150, {"Brushed Gold": "ذهبي مصقول بالفرشاة", "Black": "أسود"}, 7,
    "st885 st 885 ثلاثي براش غولد أسود",
    after_card="st-685-kitchen-mixer", italian=False,
)


publish_mixer(
    "st-873-kitchen-mixer", "خلاط مجلى ثلاثي", "Kitchen Mixer S.T 873",
    "خلاط مجلى ثلاثي بقوس أسود مرتفع وجسم أسطواني ومقبض جانبي رفيع.",
    100, {"Black": "أسود", "Brushed Gold": "ذهبي مصقول بالفرشاة"}, 5,
    "st873 st 873 ثلاثي أسود براش غولد", after_card="st-885-kitchen-mixer", italian=False,
)


publish_mixer(
    "st-007-kitchen-mixer", "خلاط مجلى سحب", "Kitchen Mixer S.T 007",
    "خلاط مجلى برأس قابل للسحب ومقبض جانبي بتصميم حلقي.",
    125, {"Brushed Gold & Black": "ذهبي مصقول بالفرشاة وأسود", "Black": "أسود", "Chrome": "كروم"},
    {"Brushed Gold & Black": 8, "Black": 7, "Chrome": 6},
    "st007 st 007 سحب براش غولد أسود كروم", after_card="st-01-kitchen-mixer", italian=False,
)


publish_mixer(
    "joyou-kitchen-mixer", "خلاط مجلى طراز جويو", "Kitchen Mixer JOYOU®",
    "ثلاثة موديلات بتشطيب كروم لامع، تختلف في تصميم المقابض. السعر للقطعة الواحدة. "
    "كانت شركة Joyou AG تابعةً لمجموعة GROHE في عام 2015.",
    45, {"Cross": "مقابض متصالبة", "Lever": "مقابض مستقيمة", "White": "مقابض بيضاء"}, 1,
    "joyou chrome جويو كروم", after_card="st-873-kitchen-mixer", italian=False, model_finish="Chrome",
)


publish_mixer(
    "antique-3in1-kitchen-mixer", "خلاط مجلى ثلاثي انتيك", "Kitchen Mixer 3in1 Antique",
    "خلاط مجلى ثلاثي بتشطيب أسود مطفي، يجمع بين انحناءة المصب الكلاسيكية والمقبضين المحزّزين.",
    225, {"Black": "أسود"}, 6, "antique 3in1 انتيك أنتيك أسود ثلاثي",
    after_card="st-873-kitchen-mixer", italian=True,
)


publish_mixer(
    "nero-white-kitchen-mixer", "خلاط مجلى نيرو وايت", "Kitchen mixer Nero White",
    "خلاط مجلى أبيض بقوس مرتفع ومقبض جانبي رفيع مع تحزيز عند الطرف.",
    170, {"White": "أبيض"}, 4, "nero white نيرو وايت أبيض ابيض",
    after_card="antique-3in1-kitchen-mixer", italian=True,
)


publish_mixer(
    "piano-wall-kitchen-mixer", "خلاط مجلى جداري بيانو", "Wall kitchen Mixer Piano",
    "خلاط جداري بقوس مرتفع ورشّاش يدوي بخرطوم حلزوني، مع زرين أماميين على شكل مفاتيح البيانو.",
    150, {"Gold": "ذهبي", "Chrome": "كروم", "Black": "أسود", "Gray": "رمادي"}, 2,
    "بيانو جداري piano wall kitchen mixer ذهبي كروم أسود رمادي",
    after_card="nero-white-kitchen-mixer", italian=True,
)


publish_mixer(
    "gessi-meccanica-316-kitchen-mixer", "خلاط مجلى جيسي 316", "Kitchen mixer GESSI Meccanica 316",
    "تزيّن النقوش الهندسية المحفورة على المعدن جسم الخلاط والذراع الأفقية. "
    "يأتي بقوس أسود أملس في النسخة بالذهبي والأسود، وبقوس ذهبي حلزوني في النسخة الذهبية بالكامل.",
    150, {"GOLD & BLACK": "ذهبي وأسود", "Full GOLD": "ذهبي بالكامل"},
    {"GOLD & BLACK": 8, "Full GOLD": 9}, "جيسي ميكانيكا 316 نقوش هندسية ذهبي أسود",
    after_card="piano-wall-kitchen-mixer", italian=True,
)


publish_mixer(
    "mcpoloo-117-kitchen-mixer", "خلاط مجلى فول أوبشن", "Kitchen mixer McPoLOO 117 — Full option",
    "تنساب المياه من حافة القاعدة المسطّحة على شكل شلّال عريض يغسل الخضروات والفواكه برفق. يمتدّ رأس الرشّ المرن إلى زوايا الحوض، وبضغطة زر يمكنك تغيير نمط تدفّق المياه. ويتيح لك المقبض الجانبي ضبط حرارة المياه وقوّة تدفّقها بيد واحدة.",
    250, {"GRAY": "الرمادي", "GOLD": "الذهبي", "BLACK": "الأسود", "CHROME": "الكروم"}, 6,
    "شلال سحب مكبولو فول أوبشن", after_card="gessi-meccanica-316-kitchen-mixer",
    brand="McPoLOO", brand_logo="mcpoloo-117-brand.png",
)

publish_mixer(
    "java-mix-cube-kitchen-mixer", "خلاط مجلى جافا كيوب شك", "Stand Kitchen Mixer Java Mix Cube",
    "خلاط مجلى قائم بقاعدة مربّعة ومصبّ مرتفع يمتدّ فوق الحوض، مع مقبض جانبي مسطّح ينسجم مع خطوطه الهندسية.",
    {"Chrome": 50, "Black": 60, "Gray": 90, "Brushed Gold": 90, "Gold": 70, "Rose Gold": 70,
     "Black & Chrome": 65, "Black & Rose Gold": 75},
    {"Chrome": "الكروم", "Black": "الأسود", "Gray": "الرمادي", "Brushed Gold": "البراش غولد",
     "Gold": "الذهبي", "Rose Gold": "الروز غولد", "Black & Chrome": "الأسود والكروم",
     "Black & Rose Gold": "الأسود والروز غولد"},
    1, "جافا ميكس كيوب شك", after_card="mcpoloo-117-kitchen-mixer", italian=False, brand="Java Mix", finish_strip=True,
)

publish_mixer(
    "java-mix-cube-wall-kitchen-mixer", "خلاط مجلى جافا كيوب جداري", "Wall Kitchen Mixer Java Mix Cube",
    "خلاط مجلى جداري بمصبّ مرتفع ومقبض أمامي مسطّح للتحكّم بحرارة المياه وتدفّقها.",
    {"Chrome": 50, "Black": 60, "Gray": 90, "Brushed Gold": 90, "Gold": 70, "Rose Gold": 70,
     "Black & Chrome": 65, "Black & Rose Gold": 75},
    {"Chrome": "الكروم", "Black": "الأسود", "Gray": "الرمادي", "Brushed Gold": "البراش غولد",
     "Gold": "الذهبي", "Rose Gold": "الروز غولد", "Black & Chrome": "الأسود والكروم",
     "Black & Rose Gold": "الأسود والروز غولد"},
    1, "جافا ميكس كيوب جداري", after_card="java-mix-cube-kitchen-mixer", italian=False, brand="Java Mix", finish_strip=True,
)

publish_mixer(
    "magic-360-kitchen-mixer", "خلاط مجلى ماجيك 360 درجة", "Wall Kitchen Mixer Magic 360°",
    "خلاط مجلى ماجيك 360° بتصميم أسطواني ومصبّ مائل ومقبض جانبي للتحكّم بتدفّق المياه وحرارتها.",
    225, {"GRAY": "الرمادي", "WHITE": "الأبيض"}, 8,
    "ماجيك 360 رمادي أبيض إيطالي",
    after_card="java-mix-cube-wall-kitchen-mixer", italian=True,
)

# Use the shared overlay style for older product cards from the storefront archive.
legacy_favorite = re.compile(
    r'(<div class="product-image"[^>]*>\s*<img [^>]*>\s*<button class=")save("(?=[^>]*\sdata-save\b))'
)

publish_mixer(
    "fima-galileo-kitchen-mixer", "خلاط مجلى فيما غاليليو", "Kitchen mixer Fima Galileo",
    "خلاط مجلى إيطالي بتصميم معاصر وتشطيب أسود مطفّي يبرز انحناءة الخرطوم وخطوط الخلاط. يخرج رأس الرشّاش من حامله بحركة سهلة، ويمنحك خرطوم السيليكون الأسود المرن والمقوّى حرية توجيه الماء إلى زوايا الحوض، لشطف الأواني وتنظيف المجلى براحة أكبر.",
    500, {"Black": "أسود مطفّي"}, 8,
    "Fima Galileo pull-out silicone black أسود مطفي فيما غاليليو سحب",
    after_card="antique-3in1-kitchen-mixer", brand="Fima",
)

publish_mixer(
    "tall-mixer-aureo", "خلاط مغسلة توب آوريو", "Tall Mixer Aureo",
    "خلاط مغسلة إيطالي بتشطيب ذهبي بملمس ناعم ولمعة هادئة. يجمع تصميمه الطويل بين جسم انسيابي ومصبّ ممتد فوق الحوض، ليناسب المغاسل الموضوعة على سطح الرخامة.",
    250, {"Brushed Gold": "ذهبي فرش"}, 1,
    "Aureo آوريو اوريو brushed gold براش غولد خلاط مغسلة طويل",
    after_card="origini", category="mixers",
)

publish_mixer(
    "tall-mixer-luxe", "خلاط مغسلة توب لوكس", "Tall Mixer Luxe",
    "خلاط مغسلة إيطالي طويل بخطوط هندسية ومصبّ ممتد فوق الحوض. يجمع جسم الكروم مع مقبض وردي أو أزرق، ليناسب المغاسل الموضوعة على سطح الرخامة.",
    250, {"Pink & Chrome": "وردي وكروم", "Blue & Chrome": "أزرق وكروم"}, 1,
    "Luxe لوكس pink blue chrome وردي أزرق كروم خلاط مغسلة طويل",
    after_card="tall-mixer-aureo", category="mixers",
)

publish_mixer(
    "floor-toilet-sofa", "تواليت أرضي كنباية", "Floor toilet sofa",
    "تواليت أرضي أبيض بخطوط منحنية وظهر يحتضن الغطاء، بتصميم مستوحى من شكل الكنباية. غطاؤه من الميلامين المقاوم للكسر، وحوضه بنظام ريملس (Rimless) من دون حافة داخلية، لسهولة التنظيف وتقليل الأماكن التي قد تتراكم فيها البكتيريا.",
    250, {"WHITE": "أبيض"}, 4,
    "تواليت أرضي كنباية ريملس ميلامين أبيض sofa rimless white",
    italian=False, category="stand-toilets",
)

publish_mixer(
    "granite-black-gray-60x50", "مغسلة غرانيت أسود مرخمة بالرمادي", "60 × 50 / 80 × 50 cm",
    "مغسلة غرانيت أسود بعروق رمادية، معها رف ديكور بالنقشة نفسها ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس. الرف بيكمّل شكل المغسلة وبيوفّر مساحة للمناشف والإكسسوارات.",
    {"Black with Gray Veining": 135, "80x50": 145},
    {"Black with Gray Veining": "60 × 50 سم", "80x50": "80 × 50 سم"}, 1,
    "مغسلة غرانيت كلاسيك رف مرآة تاتش 60x50 80x50 أسود رمادي",
    italian=False, category="granite",
    sizes={"Black with Gray Veining": "60 × 50 سم", "80x50": "80 × 50 سم"},
    pattern="أسود مرخمة بالرمادي",
)

publish_mixer(
    "granite-white-gray", "مغسلة غرانيت أبيض مرخمة بالرمادي", "60 × 50 / 80 × 50 cm",
    "مغسلة غرانيت أبيض مرخّمة بعروق رمادية، معها رف ديكور بالنقشة نفسها للمناشف والإكسسوارات، ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس.",
    {"60x50": 135, "80x50": 145},
    {"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"}, 1,
    "مغسلة غرانيت كلاسيك أبيض مرخم رمادي رف مرآة تاتش 60x50 80x50 white grey veining",
    italian=False, category="granite",
    sizes={"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"},
    pattern="أبيض مرخمة بالرمادي",
)

publish_mixer(
    "granite-silver-gray", "مغسلة غرانيت رمادية", "60 × 50 / 80 × 50 cm",
    "مغسلة غرانيت رمادي فضّي بتموّجات فاتحة وعروق ناعمة. معها رف ديكور بالنقشة نفسها للمناشف والإكسسوارات، ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس.",
    {"60x50": 135, "80x50": 145},
    {"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"}, 1,
    "مغسلة غرانيت كلاسيك رمادية رمادي فضي رف مرآة تاتش 60x50 80x50 silver gray",
    italian=False, category="granite",
    sizes={"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"},
    pattern="رمادي فضّي",
)

publish_mixer(
    "granite-white-gold-gray", "مغسلة غرانيت أبيض مرخمة دهبي ورمادي", "60 × 50 / 80 × 50 cm",
    "مغسلة غرانيت أبيض بعروق ذهبية ورمادية، معها رف ديكور بالنقشة نفسها للمناشف والإكسسوارات، ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس.",
    {"60x50": 135, "80x50": 145},
    {"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"}, 1,
    "مغسلة غرانيت كلاسيك أبيض مرخم دهبي ذهبي رمادي رف مرآة تاتش 60x50 80x50",
    italian=False, category="granite",
    sizes={"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"},
    pattern="أبيض مرخمة دهبي ورمادي",
)

publish_mixer(
    "granite-travertino", "مغسلة غرانيت ترافنتينو", "60 × 50 / 80 × 50 cm",
    "مغسلة غرانيت بنقشة ترافنتينو البيج الفاتح، معها رف ديكور بالنقشة نفسها للمناشف والإكسسوارات، ومراية بإضاءة محيطية بثلاث درجات لونية بتتبدّل باللمس.",
    {"60x50": 135, "80x50": 145},
    {"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"}, 1,
    "مغسلة غرانيت كلاسيك ترافنتينو ترافرتينو رف مرآة تاتش 60x50 80x50 travertino",
    italian=False, category="granite",
    sizes={"60x50": "60 × 50 سم", "80x50": "80 × 50 سم"},
    pattern="ترافنتينو",
)

# Move archived kitchen mixer galleries before the title and description.
kitchen_detail = re.compile(r'<section\b[^>]*\bclass="vanity-detail"[^>]*>.*?</section>', re.S)
photo_strip = re.compile(r'<div class="product-gallery"[^>]*>.*?</div>', re.S)
info_and_category = re.compile(r'(<div class="product-info">)(\s*<p class="category">خلاطات مجلى</p>)')

warranty = re.search(r'<div class="warranty">.*?</div>', (root / "index.html").read_text(), re.S)[0]
cart_button = re.compile(r'<button\b[^>]*\bdata-add-cart\b[^>]*>')


def format_kitchen_detail(match):
    section = match[0]
    if '<p class="category">خلاطات مجلى</p>' not in section:
        return section
    heading = re.search(r'<h1>(.*?)</h1>', section, re.S)
    if heading:
        title, separator, model = heading[1].partition(" — ")
        if not separator and 'id="stick-kitchen-mixer"' in section:
            model = "Kitchen mixer Steak"
        if model:
            title_markup = (
                f'<h1 lang="ar" dir="rtl">{title}</h1>'
                '<p class="product-model-name" lang="en" dir="ltr" '
                'style="text-align:right;font-size:clamp(1rem,3.5vw,1.25rem);font-weight:600;'
                'line-height:1.4;margin:0.25rem 0 0.85rem;color:var(--muted,#65533e)">'
                f'{model}</p>'
            )
            section = section[:heading.start()] + title_markup + section[heading.end():]
    if 'class="warranty"' not in section:
        section = cart_button.sub(lambda button: warranty + "\n            " + button[0], section, count=1)
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


kitchen_listing = re.compile(r'<section\b[^>]* id="kitchen"[^>]*>.*?</section>', re.S)


def format_kitchen_listing(match):
    section = match[0]
    gallery_start = '<div class="cabinet-gallery">'
    before, gallery = section.split(gallery_start, 1)
    gallery = gallery.replace(">Stick Kitchen Mixer</bdi>", ">Kitchen mixer Steak</bdi>")
    gallery = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy"', gallery)
    if " hidden" not in before.split(">", 1)[0]:
        gallery = gallery.replace('loading="lazy"', 'loading="eager"', 1)
    gallery = re.sub(
        r'<a class="action"[^>]*>استفسر عن قسم المطبخ عبر واتساب</a>',
        '<a class="kitchen-explore" href="/kitchen-mixers/?view=all" lang="en" dir="ltr">Kitchen Mixers</a>',
        gallery,
    )
    return before + gallery_start + gallery


for page in root.rglob("index.html"):
    html = page.read_text()
    updated = legacy_favorite.sub(r"\1circle\2", html)
    updated = kitchen_detail.sub(format_kitchen_detail, updated)
    updated = updated.replace(
        '<p class="category">خلاطات مجلى</p>',
        '<p class="category"><a href="/kitchen-mixers/" style="color:inherit">خلاطات مجلى</a></p>',
    )
    updated = kitchen_listing.sub(format_kitchen_listing, updated)
    toilet_cards = []
    for category in ("stand-toilets", "wall-toilets"):
        panel = re.search(rf'<section class="panel" id="{category}"[^>]*>.*?</section>', updated, re.S)
        if panel:
            toilet_cards.extend(re.findall(r'<a class="hero mixer-product"[^>]*>.*?</a>', panel[0], re.S))
    if toilet_cards:
        updated = replace_once(updated, r'(<section class="panel" id="toilets"[^>]*>.*?</div>)',
                               lambda match: match[0] + '<div class="cabinet-gallery" data-toilet-rail aria-label="موديلات كراسي التواليت">' + "".join(toilet_cards) + '</div>')
    if updated != html:
        page.write_text(updated)


# Derive the collection's search data from the published cards, including later additions.
collection_file = root / "kitchen-mixers/index.html"
collection_html = collection_file.read_text()
collection_panel = kitchen_listing.search(collection_html)[0]
model_paths = re.findall(r'<a class="hero mixer-product" href="(/[^"]+/)"', collection_panel)
schema_pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def kitchen_collection_schema(match):
    data = json.loads(match[1])
    if data.get("@type") != "CollectionPage":
        return match[0]
    data["mainEntity"] = {
        "@type": "ItemList",
        "numberOfItems": len(model_paths),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "url": origin + path}
            for i, path in enumerate(model_paths, 1)
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


collection_file.write_text(schema_pattern.sub(kitchen_collection_schema, collection_html))

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

