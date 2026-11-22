"""Publish search metadata from the same ready collections shoppers can browse."""
import json
import re
from html import escape, unescape
from urllib.parse import urlencode, urljoin, urlsplit


GROUPS = {
    "mixers": "الخلاطات الفاخرة",
    "smart-showers": "الشاورات الذكية",
    "java-mix": "أطقم خلاطات JAVA MIX",
    "washbasins": "المغاسل والكبائن",
    "cabinet-luxury": "مغاسل مع خزائن",
    "porcelain": "مغاسل بورسلان",
}
INTRO = {
    "mixers": "قارن خلاطات المغاسل الطويلة والجدارية بحسب نوع الحوض، وشاهد ألوان كل موديل وسعره.",
    "smart-showers": "تصفّح أنظمة الدش وقارن طرق التحكّم ومخارج المياه والتشطيبات في صفحة كل شاور.",
    "cabinet-luxury": "اختر مغسلة مع خزانة من فوم PVC. تحت كل موديل بتلاقي المقاس والسعر، وبصفحته فيك تشوف الألوان المتوفّرة.",
    "washbasins": "تصفّح مغاسل الحمّام مع خزائنها حسب العرض المتاح عندك، وقارن المقاسات والأسعار ضمن مجموعة Cabinet Luxury.",
}
SCHEMA = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
SCREEN = re.compile(r'<html\b[^>]*\bdata-screen="([^"]+)"')
BREADCRUMB_STYLE = """<style>.catalog-trail{display:flex;align-items:baseline;flex-wrap:wrap;gap:.45em;
margin:1rem 0;font:400 .85rem/1.6 system-ui,sans-serif;color:inherit}.catalog-trail a{color:inherit;
text-underline-offset:.2em}.catalog-intro{line-height:1.7;margin:.6rem 0 1.1rem;max-width:48rem}</style>"""


def script(data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    return f'<script type="application/ld+json">{payload}</script>'


def primary_panel(page):
    screen = SCREEN.search(page)[1]
    return re.search(rf'<section\b(?=[^>]* id="{re.escape(screen)}")[^>]*>.*?</section>', page, re.S)[0]


def text_content(markup):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def trail(origin, items):
    crumbs = []
    elements = []
    for position, (label, path) in enumerate(items, 1):
        url = urljoin(origin, path)
        label_html = escape(label)
        if position == len(items):
            crumbs.append(f'<bdi aria-current="page">{label_html}</bdi>')
        else:
            crumbs.append(f'<a href="{escape(path)}">{label_html}</a>')
        elements.append({"@type": "ListItem", "position": position, "name": label, "item": url})
    links = '<span aria-hidden="true">‹</span>'.join(crumbs)
    nav = f'<nav class="catalog-trail" aria-label="مسار التصفح">{links}</nav>'
    return nav, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}


def finish_group(product, registry, finishes, origin, description):
    """The JAVA MIX colour URL selects the pictured finish and its order price."""
    key = urlsplit(product["url"]).path.strip("/")
    model = json.loads(re.search(rf'^  "{re.escape(key)}": (\{{.*\}}),?$', registry, re.M)[1])
    variants = []
    for param, color in finishes.items():
        url = product["url"] + "?" + urlencode({"color": param})
        variants.append({
            "@type": "Product", "@id": url + "#product", "url": url,
            "sku": key + "-" + param, "name": product["name"] + " · " + color,
            "color": color, "image": urljoin(origin + "/", model["images"][color]),
            "offers": {"@type": "Offer", "url": url, "price": model["prices"][color],
                       "priceCurrency": product["offers"]["priceCurrency"],
                       "seller": {"@id": origin + "/#organization"}},
        })
    return {"@context": "https://schema.org", "@type": "ProductGroup", "name": product["name"],
            "@id": product["url"] + "#group", "url": product["url"], "description": description,
            "productGroupID": key, "variesBy": "https://schema.org/color", "hasVariant": variants}


def update_product(page, data, panel, group, registry, finishes, origin, store):
    label = text_content(re.search(r'<h1\b[^>]*>(.*?)</h1>', panel, re.S)[1])
    if group == "cabinet-luxury":
        size = re.search(r'مقاس الكابينت\s*<bdi[^>]*>([^<]+) cm</bdi>', panel)[1]
        data["size"] = size + " cm"
        title = f"مغسلة مع خزانة {label}، {size} سم | {store}"
        page = re.sub(r'<title>.*?</title>', lambda _: f'<title>{escape(title)}</title>', page, count=1)
        page = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m[1] + escape(title), page, count=1)
    description = unescape(re.search(r'<meta name="description" content="([^"]*)"', page)[1])
    data["description"] = description
    if group == "java-mix" and data["offers"]["@type"] == "AggregateOffer":
        data = finish_group(data, registry, finishes, origin, description)
    else:
        data["@id"] = data["url"] + "#product"
    model = re.search(r'<p class="product-description">\s*<bdi[^>]*>([^<]+)</bdi>\s*</p>', panel)
    data["model"] = text_content(model[1]) if model else label
    data["category"] = GROUPS[group]
    return page, data, label


def publish(root, origin, store, branches):
    pages = {p.parent.name: p.read_text() for p in root.glob("*/index.html")}
    products = {}
    for slug, page in pages.items():
        match = SCHEMA.search(page)
        if match:
            data = json.loads(match[1])
            if data.get("@type") == "Product":
                products[slug] = data
    ready = set(products) | set(GROUPS)
    members = {}
    for slug in GROUPS:
        links = re.findall(r'href="/([a-z0-9-]+)/"', primary_panel(pages[slug]))
        members[slug] = list(dict.fromkeys(link for link in links if link in ready and link != slug))
    # Category navigation may include a link back up to its parent.
    members["cabinet-luxury"] = [m for m in members["cabinet-luxury"] if m in products]
    parents = {model: group for group, links in members.items() for model in links if model in products}

    home = (root / "index.html").read_text()
    registry_path = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    registry = (root / registry_path).read_text()
    finishes = json.loads(re.search(r'^const javaMixFinishes = (\{[^\n]+\})', registry, re.M)[1])

    for slug in [*GROUPS, *parents, "branches"]:
        page = pages[slug]
        data = json.loads(SCHEMA.search(page)[1])
        panel = primary_panel(page)
        items = [("الرئيسية", "/")]
        if slug in parents:
            group = parents[slug]
            if group in ("cabinet-luxury", "porcelain"):
                items.append((GROUPS["washbasins"], "/washbasins/"))
            items.append((GROUPS[group], f"/{group}/"))
            page, data, label = update_product(page, data, panel, group, registry, finishes, origin, store)
        elif slug in GROUPS:
            label = GROUPS[slug]
            if slug in ("cabinet-luxury", "porcelain"):
                items.append((GROUPS["washbasins"], "/washbasins/"))
            content = [{"@type": "ListItem", "position": i, "url": f"{origin}/{link}/",
                        "name": products[link]["name"] if link in products else GROUPS[link]}
                       for i, link in enumerate(members[slug], 1)]
            data["mainEntity"] = {"@type": "ItemList", "numberOfItems": len(content), "itemListElement": content}
        else:
            label = "الفروع والتواصل"
            data["mainEntity"] = {"@id": origin + "/#organization", "@type": "Organization", "name": store,
                                  "subOrganization": [
                {"@type": "Store", "name": f"{store} – {name}", "hasMap": maps, "telephone": "+963" + phone[1:],
                 "address": {"@type": "PostalAddress", "addressLocality": city, "streetAddress": street,
                             "addressCountry": "SY"}} for name, city, street, phone, maps in branches
            ]}
        nav, breadcrumbs = trail(origin, items + [(label, f"/{slug}/")])
        new_panel = panel
        if slug in INTRO:
            end_heading = "</header>" if "</header>" in panel else "</h1>"
            new_panel = panel.replace(end_heading, end_heading + f'<p class="catalog-intro">{INTRO[slug]}</p>', 1)
        if slug in parents:
            new_panel = new_panel.replace('<div class="product-info">', '<div class="product-info">' + nav, 1)
        else:
            new_panel = new_panel.replace("</section>", nav + "</section>", 1)
        page = SCHEMA.sub(lambda _: script(data) + "\n" + script(breadcrumbs) + BREADCRUMB_STYLE, page, count=1)
        (root / slug / "index.html").write_text(page.replace(panel, new_panel, 1))

    for file in root.rglob("index.html"):
        page = file.read_text()
        # Other screens share this SPA shell but describe different canonical pages.
        page = re.sub(r'(<section\b[^>]*?) hidden(?=[\s>])', r'\1 data-nosnippet hidden', page)
        if '<meta name="robots"' not in page:
            page = page.replace("<title>", '<meta name="robots" content="max-image-preview:large">\n<title>', 1)
        file.write_text(page)
