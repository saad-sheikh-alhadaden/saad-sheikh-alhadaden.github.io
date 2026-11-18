"""Add multi-finish cabinets to the storefront catalog."""
import hashlib
import json
import re
from pathlib import Path

TEMPLATE = "cabinet-v13"
ORIGIN = "https://saad-customer-app.onrender.com"


def add_cabinet(root, model, width, depth, price, colors, after, *, image_names=None):
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
    home = (root / "index.html").read_text()
    script_name = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    script = (root / script_name).read_text()
    marker = f'  "{TEMPLATE}": '
    assert script.count(marker) == 1
    script = script.replace(marker, f'  "{slug}": {json.dumps(product_data, ensure_ascii=False)},\n{marker}')
    target_script = f'assets/storefront-{hashlib.sha256(script.encode()).hexdigest()[:12]}.js'
    (root / target_script).write_text(script)
    for image in images.values():
        destination = root / image.lstrip("/")
        destination.write_bytes((Path(__file__).parent / destination.name).read_bytes())

    choices = "".join(
        f'<button class="option" type="button" data-color="{color}" aria-pressed="{str(color == default).lower()}">'
        f'{label} <bdi dir="ltr">{color}</bdi></button>' for color, label in colors.items()
    )
    options = f'<div class="options" role="group" aria-label="لون الكابينت">{choices}</div>'
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


if __name__ == "__main__":
    root = Path("storefront")
    add_cabinet(root, "B604", 90, 42, 400, {"BLACK": "أسود", "WHITE": "أبيض"}, "cabinet-v20")
    add_cabinet(root, "D608", 74, 45, 325, {"OIL": "زيتي", "WHITE": "أبيض", "BLACK": "أسود"}, "cabinet-v13",
                image_names={"BLACK": "cabinet-d608-black-top.webp"})
