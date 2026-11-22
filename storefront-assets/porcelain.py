"""Publish the porcelain collection and its first model."""
import json
import re
from hashlib import sha256
from pathlib import Path


def publish(root, origin, screen_page, schema_pattern, json_script):
    group = "porcelain"
    collection = "مغاسل بورسلان"
    slug = "wudu-basin"
    name = "مغسلة وضوء"
    description = "مغسلة وضوء من البورسلان الأبيض بحوض سفلي لغسل القدمين. السعر يشمل الخلاط وجميع الملحقات."
    price = 260
    size = "50 × 43"
    photo = "/assets/wudu-basin-white.webp"
    (root / photo[1:]).write_bytes(Path(__file__).with_name(Path(photo).name).read_bytes())
    image = f'<img src="{photo}" alt="{name} من البورسلان الأبيض" width="790" height="988">'
    card = (f'<a class="hero mixer-product" href="/{slug}/">{image}'
            f'<div class="mixer-product-copy"><strong>{name}</strong>'
            f'<small><bdi dir="ltr">{size} cm</bdi> · أبيض</small>'
            f'<span dir="ltr">${price}</span></div></a>')
    section = f'''<section id="{slug}" class="vanity-detail" hidden>
      <div class="product-image">{image}<button class="save" type="button" data-save aria-pressed="false" aria-label="إضافة إلى المفضّلة">♡</button></div>
      <div class="product-info">
        <p class="category">{collection}</p>
        <h1>{name}</h1>
        <p class="product-description">{description}</p>
        <p>المقاس <bdi dir="ltr">{size} cm</bdi></p>
        <p>اللون أبيض</p>
        <p class="price-tag" data-unit-price dir="ltr">${price}</p>
        <div class="qty">
          <button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button>
          <span data-quantity>1</span>
          <button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button>
        </div>
        <button class="action" type="button" data-add-cart>أضف إلى السلة</button>
      </div>
    </section>'''
    home = (root / "index.html").read_text()
    registry = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    js = (root / registry).read_text()
    data = {"name": name, "search": f"{name} wudu ablution porcelain بورسلان أبيض",
            "price": price, "category": group, "defaultColor": "White",
            "colorLabels": {"White": "أبيض"}, "images": {"White": photo},
            "favoriteKey": f"saad-saved-{slug}"}
    js = js.replace("const products = {", f'const products = {{\n  "{slug}": {json.dumps(data, ensure_ascii=False)},', 1)
    new_registry = f"assets/storefront-{sha256(js.encode()).hexdigest()[:12]}.js"
    (root / new_registry).write_text(js)
    for page in root.rglob("index.html"):
        html = page.read_text()
        if registry not in html:
            continue
        html = html.replace(registry, new_registry).replace('href="#porcelain"><bdi', 'href="/porcelain/"><bdi')
        html = re.sub(
            r'(<section class="panel" id="porcelain"[^>]*>)\s*<h1>.*?</h1>',
            lambda m: m[1] + f'<h1>{collection}</h1><div class="cabinet-gallery">{card}</div>',
            html, count=1, flags=re.S)
        for container, attribute in (("saved", "data-saved"), ("result", "data-search-product")):
            html, count = re.subn(
                rf'(<[^>]+\bid="{container}"[^>]*>)',
                lambda m: m[1] + f'<a href="/{slug}/" {attribute}="{slug}" hidden>{name}</a>',
                html, count=1)
            if count != 1:
                raise ValueError(f"Missing {container} in {page}")
        html = html.replace("</main>", section + "</main>", 1)
        page.write_text(html)
    home = (root / "index.html").read_text()
    page = screen_page(home, group, group, "مغاسل بورسلان | Porcelain Basins",
                       "تصفّح مغاسل البورسلان مع المقاسات والأسعار.")
    dest = root / group
    dest.mkdir(exist_ok=True)
    (dest / "index.html").write_text(page)
    # screen_page opens panels using the shared section class.
    product_shell = home.replace(f'<section id="{slug}" class="vanity-detail" hidden>',
                                 f'<section class="panel" id="{slug}" hidden>', 1)
    page = screen_page(product_shell, slug, slug, name, description, "Product")
    page = page.replace(f'<section class="panel" id="{slug}">', f'<section id="{slug}" class="vanity-detail">', 1)
    schema = {"@context": "https://schema.org", "@type": "Product", "name": name, "description": description,
              "sku": slug, "url": f"{origin}/{slug}/", "image": [origin + photo], "color": "White",
              "size": f"{size} cm", "material": "Porcelain",
              "offers": {"@type": "Offer", "price": price, "priceCurrency": "USD", "url": f"{origin}/{slug}/"}}
    dest = root / slug
    dest.mkdir(exist_ok=True)
    (dest / "index.html").write_text(schema_pattern.sub(lambda _: json_script(schema), page, count=1))
