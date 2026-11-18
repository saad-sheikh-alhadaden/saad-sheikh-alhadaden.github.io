"""Add multi-finish cabinets to the storefront catalog."""
import hashlib
import json
import re
from pathlib import Path

TEMPLATE = "cabinet-v13"
ORIGIN = "https://saad-customer-app.onrender.com"


def add_cabinet(root, model, width, depth, price, colors, after, *, image_names=None, box_price=None, box_size=None):
    slug = f"cabinet-{model.lower()}"
    default = next(iter(colors))
    images = {color: f"/assets/{slug}-{color.lower()}.webp" for color in colors}
    for color, name in (image_names or {}).items():
        images[color] = f"/assets/{name}"
    dimensions = f"{width} × {depth} cm"
    width_marker = f'data-vanity-width="{width}"'

    def from_v13(markup):
        return (markup.replace(TEMPLATE, slug).replace("V13", model)
                .replace("56 × 50 cm", dimensions)
                .replace(f"{slug}-white.webp", images[default].rsplit("/", 1)[-1])
                .replace('height="987"', 'height="988"')
                .replace("بلون أبيض", f"بلون {colors[default]}")
                .replace("$400", f"${price}"))

    product_data = {
        "name": f"{model} · كابينت مغسلة",
        "search": f"{model.lower()} كابينت مغسلة {' '.join(colors)} {' '.join(colors.values())} {width} {depth} {price}",
        "price": price, "defaultColor": default, "images": images,
        "favoriteKey": f"saad-{slug}-favorite", "category": "cabinet-luxury",
    }
    box_images = {}
    if box_price is not None:
        box_images = {color: f"/assets/{slug}-box-{color.lower()}.webp" for color in colors}
        product_data["boxImages"] = box_images
        product_data["images"] = {**images, **{color + "-BOX": image for color, image in images.items()}}
        product_data["prices"] = {color + "-BOX": price + box_price for color in colors}
        product_data["colorLabels"] = {color + "-BOX": color + " · مع الصيدلية" for color in colors}

    home = (root / "index.html").read_text()
    script_name = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    script = (root / script_name).read_text()
    marker = f'  "{TEMPLATE}": '
    assert script.count(marker) == 1
    script = script.replace(marker, f'  "{slug}": {json.dumps(product_data, ensure_ascii=False)},\n{marker}')
    if box_images and "const orderColor =" not in script:
        script = add_box_controls(script)
    target_script = f'assets/storefront-{hashlib.sha256(script.encode()).hexdigest()[:12]}.js'
    (root / target_script).write_text(script)
    for image in (*images.values(), *box_images.values()):
        destination = root / image.lstrip("/")
        destination.write_bytes((Path(__file__).parent / destination.name).read_bytes())

    choices = "".join(
        f'<button class="option" type="button" data-color="{color}" aria-pressed="{str(color == default).lower()}">'
        f'{label} <bdi dir="ltr">{color}</bdi></button>' for color, label in colors.items()
    )
    options = f'<div class="options" role="group" aria-label="لون الكابينت">{choices}</div>'
    if box_images:
        options += f'''<style>.cabinet-box-check{{visibility:hidden}}[data-cabinet-box]:checked+.cabinet-box-check{{visibility:visible}}[data-cabinet-box]:focus-visible{{outline:2px solid #80591f;outline-offset:3px}}</style><div class="cabinet-box" style="position:relative;margin:16px 0;padding:12px 14px;border:1px solid #b7a58a;border-radius:12px;background:#faf7f0;color:#24201a">
  <label style="display:flex;align-items:center;gap:9px;min-height:44px;margin-left:50px;cursor:pointer">
    <span style="position:relative;display:grid;place-items:center;width:20px;height:20px;flex:none">
      <input type="checkbox" data-cabinet-box style="appearance:none;-webkit-appearance:none;box-sizing:border-box;width:20px;height:20px;margin:0;border:2px solid #24201a;border-radius:4px;background:#fff;color-scheme:light;cursor:pointer">
      <svg class="cabinet-box-check" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true" style="position:absolute;pointer-events:none"><path d="m3.5 8 3 3 6-6" stroke="#24201a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </span>
    <span><strong>إضافة الصيدلية <bdi dir="ltr">+${box_price}</bdi></strong>
      <small dir="ltr" style="display:block;width:max-content;max-width:100%;color:#625342">Size: {box_size} cm</small>
    </span>
  </label>
  <details>
    <summary aria-label="صورة الصيدلية باللون المختار" title="صورة الصيدلية باللون المختار" style="position:absolute;top:12px;left:12px;width:44px;height:44px;display:grid;place-items:center;list-style:none;border:1px solid #b7a58a;border-radius:9px;color:#674a20;cursor:pointer">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m3 17 5-5 4 4 4-5 5 5"/></svg>
    </summary>
    <img data-box-image src="{box_images[default]}" alt="الصيدلية الجانبية" width="140" loading="lazy" style="display:block;height:auto;max-width:100%;margin:12px auto 0;border-radius:8px">
  </details>
</div>'''
    for page in root.rglob("index.html"):
        markup = page.read_text()
        if f"/{script_name}" not in markup:
            continue
        target_card = re.search(rf'<a class="hero mixer-product vanity-card"[^>]*href="/{after}/">.*?</a>', markup, re.S)[0]
        old_card = re.search(r'<a class="hero mixer-product vanity-card"[^>]*href="/cabinet-v13/">.*?</a>', markup, re.S)[0]
        new_card = from_v13(old_card).replace('data-vanity-width="56"', width_marker)
        markup = markup.replace(target_card, target_card + "\n" + new_card, 1)
        detail = re.search(r'<section id="cabinet-v13" class="vanity-detail"(?: hidden)?>.*?</section>', markup, re.S)[0]
        hidden = from_v13(detail).replace('class="vanity-detail">', 'class="vanity-detail" hidden>')
        hidden = hidden.replace('fetchpriority="high"', 'loading="lazy"')
        hidden = hidden.replace('<p>اللون <bdi dir="ltr">WHITE</bdi></p>', options)
        assert options in hidden
        markup = markup.replace(detail, detail + "\n" + hidden, 1)
        for attribute in ("data-search-product", "data-saved"):
            link = re.search(rf'<a href="/{TEMPLATE}/" {attribute}="{TEMPLATE}" hidden>.*?</a>', markup)[0]
            markup = markup.replace(link, link + from_v13(link), 1)
        page.write_text(markup.replace(f"/{script_name}", f"/{target_script}"))

    markup = (root / TEMPLATE / "index.html").read_text()
    header, body = markup.split('<div class="app">', 1)
    header = from_v13(header).replace(f"بلون {colors[default]}", "بألوان " + "، ".join(colors.values()))
    header = header.replace("بسعر 400 دولار", f"بسعر {price} دولار")
    if box_images:
        header = header.replace(f"بسعر {price} دولار.", f"بسعر {price} دولار. الصيدلية الجانبية الظاهرة بالصورة اختيارية بسعر {box_price} دولار.")
    schema_tag = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
    def set_schema(match):
        data = json.loads(match[2])
        data["image"] = [ORIGIN + path for path in images.values()]
        data["color"] = list(colors)
        data["offers"]["price"] = price
        return match[1] + json.dumps(data, ensure_ascii=False) + match[3]

    header = schema_tag.sub(set_schema, header, count=1)
    body = body.replace('<section id="cabinet-v13" class="vanity-detail">',
                        '<section id="cabinet-v13" class="vanity-detail" hidden>', 1)
    body = body.replace(hidden, hidden.replace('class="vanity-detail" hidden>', 'class="vanity-detail">', 1)
                        .replace('loading="lazy"', 'fetchpriority="high"', 1), 1)
    folder = root / slug
    folder.mkdir(exist_ok=True)
    (folder / "index.html").write_text(header + '<div class="app">' + body)


def add_box_controls(script):
    controls = r'''   const box = screen.querySelector("[data-cabinet-box]");
  const boxImage = screen.querySelector("[data-box-image]");
  const orderColor = () => box?.checked ? color + "-BOX" : color;
  const syncOrder = () => {
    addButton.textContent = `أضف إلى السلة — ${money(quantity * unitPrice(product, orderColor()))}`;
    if (boxImage) boxImage.src = product.boxImages[color];
  };
  box?.addEventListener("change", syncOrder);
'''
    changes = {
        "  let quantity = 1;": "  let quantity = 1;\n" + controls,
        '      addButton.textContent = `أضف إلى السلة — ${money(quantity * price)}`;': "      syncOrder();",
        '      addButton.textContent = `أضف إلى السلة — ${money(quantity * unitPrice(product, color))}`;': "      syncOrder();",
        "&& item.color === color);": "&& item.color === orderColor());",
        "else cart.push({product: id, color, qty: quantity});": "else cart.push({product: id, color: orderColor(), qty: quantity});",
    }
    for old, new in changes.items():
        if script.count(old) != 1:
            raise ValueError(f"Expected one storefront cart hook: {old}")
        script = script.replace(old, new)
    return script


if __name__ == "__main__":
    root = Path("storefront")
    add_cabinet(root, "B604", 90, 42, 400, {"BLACK": "أسود", "WHITE": "أبيض"}, "cabinet-v20",
                image_names={"BLACK": "cabinet-b604-black-oak.webp", "WHITE": "cabinet-b604-white-oak.webp"})
    add_cabinet(root, "D608", 74, 45, 325, {"OIL": "زيتي", "WHITE": "أبيض", "BLACK": "أسود"}, "cabinet-v13",
                image_names={"BLACK": "cabinet-d608-black-top.webp"})
    add_cabinet(root, "Z605", 110, 44, 500, {"BLACK": "أسود", "WHITE": "أبيض"},
                "cabinet-v1-leather", box_price=40, box_size="30 × 22 × 120")
    add_cabinet(root, "A609", 70, 42, 300, {"BLACK": "أسود", "WHITE": "أبيض", "IVORE": "عاجي"},
                "cabinet-v13", box_price=40, box_size="26 × 18 × 90")
    add_cabinet(root, "B630", 90, 42, 400, {"GRAY": "رمادي", "BLACK": "أسود", "WHITE": "أبيض"}, "cabinet-b604")
    add_cabinet(root, "A630", 90, 42, 400, {"WHITE": "أبيض", "BLACK": "أسود", "GREIGE": "غريج"},
                "cabinet-b630", box_price=40, box_size="27 × 17 × 90")
