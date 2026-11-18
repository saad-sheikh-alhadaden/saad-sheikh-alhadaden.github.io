"""Add B604 to the generated showroom and its existing cart and color controls."""
import hashlib
import json
import re
from pathlib import Path

MODEL = "B604"
SLUG = "cabinet-b604"
TEMPLATE = "cabinet-v13"
DIMENSIONS = "90 × 42 cm"
PRICE = 400
ORIGIN = "https://saad-customer-app.onrender.com"
COLORS = {"BLACK": "أسود", "WHITE": "أبيض"}
IMAGES = {color: f"/assets/{SLUG}-{color.lower()}.webp" for color in COLORS}


def from_v13(markup):
    return (markup.replace(TEMPLATE, SLUG).replace("V13", MODEL)
            .replace("56 × 50 cm", DIMENSIONS)
            .replace(f"{SLUG}-white.webp", f"{SLUG}-black.webp")
            .replace('height="987"', 'height="988"').replace("بلون أبيض", "بلون أسود"))


def add_cabinet(root):
    product_data = {
        "name": f"{MODEL} · كابينت مغسلة",
        "search": "b604 كابينت مغسلة black white أسود اسود أبيض ابيض 90 42 400",
        "price": PRICE, "defaultColor": "BLACK", "images": IMAGES,
        "favoriteKey": f"saad-{SLUG}-favorite", "category": "cabinet-luxury",
    }
    home = (root / "index.html").read_text()
    script_name = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    script = (root / script_name).read_text()
    marker = f'  "{TEMPLATE}": '
    assert script.count(marker) == 1
    script = script.replace(marker, f'  "{SLUG}": {json.dumps(product_data, ensure_ascii=False)},\n{marker}')
    target_script = f'assets/storefront-{hashlib.sha256(script.encode()).hexdigest()[:12]}.js'
    (root / target_script).write_text(script)
    for image in IMAGES.values():
        destination = root / image.lstrip("/")
        destination.write_bytes((Path(__file__).parent / destination.name).read_bytes())

    choices = "".join(
        f'<button class="option" type="button" data-color="{color}" aria-pressed="{str(color == "BLACK").lower()}">'
        f'{label} <bdi dir="ltr">{color}</bdi></button>' for color, label in COLORS.items()
    )
    options = f'<div class="options" role="group" aria-label="لون الكابينت">{choices}</div>'
    for page in root.rglob("index.html"):
        markup = page.read_text()
        if f"/{script_name}" not in markup:
            continue
        target_card = re.search(r'<a class="hero mixer-product vanity-card"[^>]*href="/cabinet-v20/">.*?</a>', markup, re.S)[0]
        old_card = re.search(r'<a class="hero mixer-product vanity-card"[^>]*href="/cabinet-v13/">.*?</a>', markup, re.S)[0]
        new_card = from_v13(old_card).replace('data-vanity-width="56"', 'data-vanity-width="90"')
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
    header = from_v13(header).replace("بلون أسود", "باللونين الأسود والأبيض")
    schema_tag = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
    def set_schema(match):
        data = json.loads(match[2])
        data["image"] = [ORIGIN + path for path in IMAGES.values()]
        data["color"] = list(COLORS)
        return match[1] + json.dumps(data, ensure_ascii=False) + match[3]

    header = schema_tag.sub(set_schema, header, count=1)
    body = body.replace('<section id="cabinet-v13" class="vanity-detail">',
                        '<section id="cabinet-v13" class="vanity-detail" hidden>', 1)
    body = body.replace(hidden, hidden.replace('class="vanity-detail" hidden>', 'class="vanity-detail">', 1)
                        .replace('loading="lazy"', 'fetchpriority="high"', 1), 1)
    folder = root / SLUG
    folder.mkdir(exist_ok=True)
    (folder / "index.html").write_text(header + '<div class="app">' + body)


if __name__ == "__main__":
    add_cabinet(Path("storefront"))
