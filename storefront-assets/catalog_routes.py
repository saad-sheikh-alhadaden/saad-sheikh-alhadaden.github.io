"""Publish focused product documents while retaining the storefront's shared navigation."""
from hashlib import sha256
from html import escape, unescape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from catalog_search import SCHEMA, script, text_content, trail

SCREEN = re.compile(r'<html\b[^>]*\bdata-screen="([^"]+)"')
SECTION = re.compile(r'(<section\b[^>]*\bid="([^"]+)"[^>]*>)(.*?)</section>', re.S)
REGISTRY = re.compile(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"')
SHARE = re.compile(r'data-share-pages="([^"]+)"')
GRANITE_PATH = "/granite-basins/"
GRANITE_TITLE = "مغاسل غرانيت في دمشق | المقاسات والأسعار | شركة سعد شيخ الحدادين"
GRANITE_DESCRIPTION = "قارن صور وأسعار مغاسل الغرانيت في دمشق، من المغاسل المعلّقة إلى الموديلات المضاءة ومغاسل الوضوء. اختر الموديل وشاهد المقاسات المتاحة لكل تصميم."
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one occurrence of {old[:80]!r}")
    return text.replace(old, new, 1)


def build_registry(root, asset):
    source = (root / asset).read_text()
    # Saved products and the cart span every page, even when only one detail form is mounted.
    first = source.index('  const favoriteButton = screen.querySelector("[data-save]");')
    end = source.index('  renderFavorite();\n}', first) + len('  renderFavorite();')
    source = source[:first] + source[end:]
    helpers = Path(__file__).with_name("catalog-routes.js").read_text()
    hook = '  const screen = document.getElementById(id);\n  const image = screen.querySelector(".product-image img");'
    source = once(source, hook, '  const screen = document.getElementById(id);\n'
                  '  bindCatalogFavorite(id, product, screen);\n  if (!screen) continue;\n'
                  '  const image = screen.querySelector(".product-image img");')
    hook = '  const baseScreen = document.documentElement.dataset.screen || "home";'
    source = once(source, hook, '  if (openLinkedProduct(hash)) return;\n' + hook)
    source = once(source, '  for (const screen of screens) screen.hidden = screen.id !== active;',
                  '  for (const screen of screens) setScreenVisibility(screen, screen.id === active);')
    data = (helpers + "\n" + source).encode()
    name = f"assets/storefront-{sha256(data).hexdigest()[:12]}.js"
    (root / name).write_bytes(data)
    return name


def granite_page(root):
    template = (root / "decorative-vessel-basins/index.html").read_text()
    previous = json.loads(SCHEMA.search(template)[1])
    origin = urlsplit(previous["url"])
    origin = f"{origin.scheme}://{origin.netloc}"
    url = origin + GRANITE_PATH
    panel = next(m[0] for m in SECTION.finditer(template) if m[2] == "granite")
    cards = re.findall(r'<a class="hero mixer-product" href="([^"]+)"[^>]*>.*?<strong>(.*?)</strong>.*?</a>', panel, re.S)
    if not cards:
        raise ValueError("Missing granite collection cards")
    entries = [{"@type": "ListItem", "position": i, "url": origin + path, "name": text_content(name)}
               for i, (path, name) in enumerate(cards, 1)]
    crumbs, schema = trail(origin, [("الرئيسية", "/"), ("المغاسل والكبائن", "/washbasins/"), ("مغاسل غرانيت", GRANITE_PATH)])
    data = {"@context": "https://schema.org", "@type": "CollectionPage", "name": GRANITE_TITLE,
            "description": GRANITE_DESCRIPTION, "url": url, "inLanguage": "ar-SY",
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(entries), "itemListElement": entries}}
    page = once(template, 'data-screen="decorative-vessel-basins"', 'data-screen="granite"')
    page = re.sub(r'<title>.*?</title>', f'<title>{GRANITE_TITLE}</title>', page, count=1)
    for attr, value in [('name="description"', GRANITE_DESCRIPTION), ('property="og:description"', GRANITE_DESCRIPTION),
                        ('property="og:title"', GRANITE_TITLE), ('property="og:url"', url)]:
        page = re.sub(r'(<meta '+attr+r' content=")[^"]+', lambda m: m[1]+escape(value, quote=True), page, count=1)
    page = re.sub(r'(<link rel="canonical" href=")[^"]+', lambda m: m[1]+url, page, count=1)
    page = SCHEMA.sub("", page)
    page = once(page, "</title>", "</title>\n" + script(data) + "\n" + script(schema))
    page = once(page, panel, panel.replace("</section>", crumbs + "</section>"))
    destination = root / GRANITE_PATH.strip("/") / "index.html"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(page)
    sitemap = root / "sitemap.xml"
    tree = ET.parse(sitemap)
    if url not in {loc.text for loc in tree.iter(f"{{{NS}}}loc")}:
        ET.register_namespace("", NS)
        ET.SubElement(ET.SubElement(tree.getroot(), f"{{{NS}}}url"), f"{{{NS}}}loc").text = url
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)


def focus_section(match, active, routes):
    tag, screen, content = match.groups()
    if screen == active:
        tag = re.sub(r' (?:data-nosnippet|hidden)(?=[\s>])', '', tag)
        content = content.replace("<h1", "<h1 data-screen-heading", 1)
    else:
        # The JAVA MIX finish selector moves between all five forms within one document.
        java_gallery = "data-mixer-choice" in content and active.startswith("java-mix")
        if "data-add-cart" in content and screen in routes and not java_gallery:
            return ""
        if " hidden" not in tag:
            tag = tag[:-1] + " data-nosnippet hidden>"
        content = content.replace("<h1", "<h2 data-screen-heading", 1).replace("</h1>", "</h2>", 1)
    return tag + content + "</section>"


def publish(root):
    granite_page(root)
    registries = {}
    share_maps = {}
    for page in root.rglob("index.html"):
        original = page.read_text()
        registry = REGISTRY.search(original)
        if not registry:
            continue
        asset = registry[1]
        if asset not in registries:
            registries[asset] = build_registry(root, asset)
        encoded = SHARE.search(original)[1]
        if encoded not in share_maps:
            routes = json.loads(unescape(encoded))
            routes["granite"] = {"path": GRANITE_PATH, "title": GRANITE_TITLE, "label": "مشاركة المجموعة"}
            share_maps[encoded] = (routes, escape(json.dumps(routes, ensure_ascii=False, separators=(",", ":")), quote=True))
        routes, new_map = share_maps[encoded]
        screen = SCREEN.search(original)
        active = screen[1] if screen else "home"
        markup = SECTION.sub(lambda m: focus_section(m, active, routes), original)
        markup = markup.replace(f'src="/{asset}"', f'src="/{registries[asset]}"', 1)
        markup = markup.replace('data-share-pages="' + encoded + '"', 'data-share-pages="' + new_map + '"', 1)
        markup = re.sub(r'href="/?#granite(?:-classic)?"', f'href="{GRANITE_PATH}"', markup)
        page.write_text(markup)
