"""Publish the porcelain collection and its models."""
import json
import re
from hashlib import sha256
from pathlib import Path


def publish(root, origin, screen_page, schema_pattern, json_script):
    group = "porcelain"
    collection = "مغاسل بورسلان"
    models = (
        ("wudu-basin", "مغسلة وضوء", "مغسلة وضوء من البورسلان الأبيض بحوض سفلي لغسل القدمين. السعر يشمل الخلاط وجميع الملحقات.", 260, "50 × 43", "wudu ablution"),
        ("square-wall-hung-basin", "مغسلة معلّقة مربّعة", "مغسلة بورسلان بيضاء مربّعة بتثبيت جداري. السعر للمغسلة وحدها، والخلاط والملحقات تُباع بشكل منفصل.", 75, "53 × 44", "معلقة مربعة square wall hung"),
        ("round-wall-hung-basin", "مغسلة معلّقة دائرية", "مغسلة بورسلان بيضاء بحوض دائري وتثبيت جداري. السعر للمغسلة وحدها، والخلاط والملحقات خارج السعر.", 75, "47 × 46", "معلقة دائرية round wall hung"),
        ("st-7903-porcelain-basin", "مغسلة معلّقة S.T 7903", "مغسلة بورسلان بيضاء بتثبيت جداري، مع رفّ مدمج أسفل الحوض ومفتوح من الخلف لوضع عبوات الشامبو ومستحضرات العناية. السعر للمغسلة وحدها، والخلاط والملحقات خارج السعر.", 175, "50 × 38", "st 7903 معلقة رف شامبو wall hung"),
        ("st-7900-porcelain-basin", "مغسلة معلّقة S.T 7900", "مغسلة بورسلان بيضاء بتثبيت جداري، مع فتحة تخزين مدمجة أسفل الحوض، مفتوحة من الخلف ومخصّصة لعبوات الشامبو ومستحضرات التجميل. السعر للمغسلة وحدها، والخلاط والملحقات خارج السعر.", 175, "39 × 27", "st 7900 معلقة رف شامبو wall hung"),
        ("st-7902-porcelain-basin", "مغسلة معلّقة S.T 7902", "مغسلة بورسلان بيضاء بتثبيت جداري، مع مساحة تخزين مدمجة أسفل الحوض لوضع عبوات الشامبو ومستحضرات التجميل في متناول اليد. السعر للمغسلة وحدها، والخلاط والملحقات خارج السعر.", 175, "45 × 42", "st 7902 معلقة رف شامبو wall hung"),
        ("st-7901-porcelain-basin", "مغسلة معلّقة S.T 7901", "مغسلة بورسلان بيضاء بتثبيت جداري، مع فتحة تخزين مدمجة أسفل الحوض ومفتوحة من الخلف، لترتيب عبوات الشامبو ومستحضرات التجميل وإبقائها في متناول اليد. السعر للمغسلة وحدها، والخلاط والملحقات خارج السعر.", 175, "43 × 30", "st 7901 معلقة رف شامبو wall hung"),
    )
    publish_models(root, origin, screen_page, schema_pattern, json_script, group, group, collection,
                   "Porcelain Basins", models, "White", "أبيض", "Porcelain")


def publish_kitchen(root, origin, screen_page, schema_pattern, json_script):
    models = (
        ("stick-kitchen-mixer", "خلاط مجلى ستيك",
         "خلاط مجلى إيطالي بتصميم ستيك، يجمع بين الخطوط الهندسية الدقيقة ولمسة رمادية هادئة. تمنحك رقبة السيليكون المرنة حرية توجيه الماء داخل الحوض بسهولة.",
         400, None, "stick kitchen mixer ستيك خلاط مجلى gray رمادي"),
        ("st-01-kitchen-mixer", "خلاط مجلى 3 في 1 — Kitchen Mixer S.T 01",
         "خلاط مجلى إيطالي بتشطيب ذهبي مفرّش ورقبة سيليكون مرنة تمنحك حرية توجيه الماء داخل الحوض. يجمع تصميمه العصري ثلاثة خطوط في خلاط واحد: للمياه الباردة، وللمياه الساخنة، وخط مستقل يُوصَل بفلتر مياه الشرب أو بخط مياه الشركة.",
         350, None, "st 01 3in1 3 in 1 فلتر brushed gold"),
    )
    publish_models(root, origin, screen_page, schema_pattern, json_script, "kitchen", "kitchen-mixers",
                   "خلاطات مجلى", "Kitchen Mixers", models, "Gray", "رمادي", country="Italy",
                   finishes={"st-01-kitchen-mixer": ("Brushed Gold", "ذهبي مفرّش")},
                   galleries={"st-01-kitchen-mixer": ("detail", "in-use")})


def publish_models(root, origin, screen_page, schema_pattern, json_script, group, collection_slug,
                   collection, english, models, default_color, default_label, material=None, country=None,
                   finishes=None, galleries=None):
    cards = []
    sections = []
    home = (root / "index.html").read_text()
    registry = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    js = (root / registry).read_text()
    for slug, name, description, price, size, keywords in models:
        color, color_label = (finishes or {}).get(slug, (default_color, default_label))
        photo = f"/assets/{slug}-{color.lower().replace(' ', '-')}.webp"
        photos = [photo, *(f"/assets/{slug}-{view}.webp" for view in (galleries or {}).get(slug, ()))]
        for asset in photos:
            (root / asset[1:]).write_bytes(Path(__file__).with_name(Path(asset).name).read_bytes())
        gallery = ""
        if len(photos) > 1:
            thumbnails = "".join(
                f'<button type="button" data-gallery-src="{asset}" data-width="790" data-height="988" '
                f'aria-label="{name} · {label}" aria-pressed="{str(i == 0).lower()}">'
                f'<img src="{asset}" width="64" height="80" alt="" loading="lazy"></button>'
                for i, (asset, label) in enumerate(zip(photos, ("الصورة الرئيسية", "التفاصيل", "أثناء الاستخدام")))
            )
            gallery = f'<div class="product-gallery">{thumbnails}</div>'
        image = f'<img src="{photo}" alt="{name} باللون {color_label}" width="790" height="988">'
        dimensions = f'<bdi dir="ltr">{size} cm</bdi> · ' if size else ""
        size_line = f'<p>المقاس <bdi dir="ltr">{size} cm</bdi></p>' if size else ""
        country_line = '<p>صنع في إيطاليا</p>' if country == "Italy" else ""
        card_name, separator, model_name = name.partition(" — ") if group == "kitchen" else (name, "", "")
        if group == "kitchen":
            subtitle = model_name if separator else "Stick Kitchen Mixer"
            caption = f'<bdi lang="en" dir="ltr">{subtitle}</bdi>'
        else:
            caption = f"{dimensions}{color_label}"
        card = (f'<a class="hero mixer-product" href="/{slug}/">{image}'
                f'<div class="mixer-product-copy"><strong>{card_name}</strong>'
                f'<small>{caption}</small>'
                f'<span dir="ltr">${price}</span></div></a>')
        section = f'''<section id="{slug}" class="vanity-detail" hidden>
          <div class="product-image">{image}<button class="save" type="button" data-save aria-pressed="false" aria-label="إضافة إلى المفضّلة">♡</button></div>
          <div class="product-info">
            <p class="category">{collection}</p>
            <h1>{name}</h1>
            <p class="product-description">{description}</p>
            {gallery}
            {size_line}
            <p>اللون {color_label}</p>
            {country_line}
            <p class="price-tag" data-unit-price dir="ltr">${price}</p>
            <div class="qty">
              <button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button>
              <span data-quantity>1</span>
              <button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button>
            </div>
            <button class="action" type="button" data-add-cart>أضف إلى السلة</button>
          </div>
        </section>'''
        data = {"name": name, "search": f"{name} {keywords} {collection} {color_label}",
                "price": price, "category": group, "defaultColor": color,
                "colorLabels": {color: color_label}, "images": {color: photo},
                "favoriteKey": f"saad-saved-{slug}"}
        js = js.replace("const products = {", f'const products = {{\n  "{slug}": {json.dumps(data, ensure_ascii=False)},', 1)
        cards.append(card)
        sections.append(section)
    new_registry = f"assets/storefront-{sha256(js.encode()).hexdigest()[:12]}.js"
    (root / new_registry).write_text(js)
    for page in root.rglob("index.html"):
        html = page.read_text()
        if registry not in html:
            continue
        html = html.replace(registry, new_registry).replace('href="#porcelain"><bdi', 'href="/porcelain/"><bdi')
        html = re.sub(
            rf'(<section class="panel" id="{group}"[^>]*>)\s*<h1>.*?</h1>',
            lambda m: m[1] + f'<h1>{collection}</h1><div class="cabinet-gallery">{"".join(cards)}</div>',
            html, count=1, flags=re.S)
        for slug, name, *_ in models:
            for container, attribute in (("saved", "data-saved"), ("result", "data-search-product")):
                html, count = re.subn(
                    rf'(<[^>]+\bid="{container}"[^>]*>)',
                    lambda m: m[1] + f'<a href="/{slug}/" {attribute}="{slug}" hidden>{name}</a>',
                    html, count=1)
                if count != 1:
                    raise ValueError(f"Missing {container} in {page}")
        html = html.replace("</main>", "".join(sections) + "</main>", 1)
        page.write_text(html)
    home = (root / "index.html").read_text()
    page = screen_page(home, group, collection_slug, f"{collection} | {english}",
                       f"تصفّح موديلات {collection} وصورها وأسعارها.")
    dest = root / collection_slug
    dest.mkdir(exist_ok=True)
    (dest / "index.html").write_text(page)
    for slug, name, description, price, size, _ in models:
        color, color_label = (finishes or {}).get(slug, (default_color, default_label))
        photo = f"/assets/{slug}-{color.lower().replace(' ', '-')}.webp"
        photos = [photo, *(f"/assets/{slug}-{view}.webp" for view in (galleries or {}).get(slug, ()))]
        # screen_page opens panels using the shared section class.
        product_shell = home.replace(f'<section id="{slug}" class="vanity-detail" hidden>',
                                     f'<section class="panel" id="{slug}" hidden>', 1)
        page = screen_page(product_shell, slug, slug, name, description, "Product")
        page = page.replace(f'<section class="panel" id="{slug}">', f'<section id="{slug}" class="vanity-detail">', 1)
        schema = {"@context": "https://schema.org", "@type": "Product", "name": name, "description": description,
                  "sku": slug, "url": f"{origin}/{slug}/", "image": [origin + asset for asset in photos], "color": color,
                  "offers": {"@type": "Offer", "price": price, "priceCurrency": "USD", "url": f"{origin}/{slug}/"}}
        if size:
            schema["size"] = f"{size} cm"
        if material:
            schema["material"] = material
        if country:
            schema["countryOfOrigin"] = {"@type": "Country", "name": country}
        dest = root / slug
        dest.mkdir(exist_ok=True)
        (dest / "index.html").write_text(schema_pattern.sub(lambda _: json_script(schema), page, count=1))
