"""Create crawlable collection pages and describe existing storefront photos."""
import json
import re
import xml.etree.ElementTree as ET
from html import escape, unescape
from pathlib import Path
from runpy import run_path
from urllib.parse import urlsplit

ROOT = Path("storefront")
ORIGIN = "https://saad-customer-app.onrender.com"
STORE = "شركة سعد شيخ الحدادين"
COLLECTIONS = {
    "mixers": ("mixers", "الخلاطات الفاخرة | Trend Of Mixer", "تصفّح خلاطات المغاسل والمطبخ من شركة سعد شيخ الحدادين في دمشق وقارن صور الموديلات وألوانها وأسعارها بالدولار."),
    "showers": ("smart-showers", "الشاورات الذكية | Smart Shower", "اكتشف أنظمة الدش والشاور الذكي من شركة سعد شيخ الحدادين في دمشق. تصفّح صور الموديلات مثل Ferrari وVera وMidas مع الألوان والأسعار."),
    "washbasins": ("washbasins", "المغاسل والكبائن", "تصفّح أقسام المغاسل والكبائن من شركة سعد شيخ الحدادين في دمشق، واختر عرض الكابينت المناسب لحمّامك."),
    "cabinet-luxury": ("cabinet-luxury", "كابينتات مغاسل فخمة | Cabinet Luxury", "قارن كابينتات مغاسل الحمّام من فوم PVC بحسب المقاس واللون والسعر في متجر سعد شيخ الحدادين، دمشق."),
}
schema_pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def json_script(data):
    payload = json.dumps(data, ensure_ascii=False).replace("<", r"\u003c")
    return f'<script type="application/ld+json">{payload}</script>'


def meta(html, key, value):
    pattern = rf'(<meta (?:name|property)="{re.escape(key)}" content=")[^"]*(">)'
    return re.sub(pattern, lambda m: m[1] + escape(value, quote=True) + m[2], html, count=1)


def category_links(html):
    for screen, (slug, _, _) in COLLECTIONS.items():
        html = html.replace(f'href="#{screen}"', f'href="/{slug}/"')
    return html


def collection_page(home, screen, slug, title, description):
    url = f"{ORIGIN}/{slug}/"
    html = home.replace('<html lang="ar" dir="rtl">',
                        f'<html lang="ar" dir="rtl" data-screen="{screen}">\n<base href="/">', 1)
    html = html.replace('<section id="home">', '<section id="home" hidden>', 1)
    panel = f'<section class="panel" id="{screen}"'
    if panel + " hidden>" not in html:
        raise ValueError(f"Missing collection panel: {screen}")
    html = html.replace(panel + " hidden>", panel + ">", 1)
    title = f"{title} | {STORE}"
    html = re.sub(r"<title>.*?</title>", lambda _: f"<title>{escape(title)}</title>", html, count=1)
    html = html.replace(f'rel="canonical" href="{ORIGIN}/"', f'rel="canonical" href="{url}"', 1)
    for key, value in [("og:url", url), ("og:title", title), ("og:description", description), ("description", description)]:
        html = meta(html, key, value)
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
              "description": description, "url": url, "inLanguage": "ar-SY"}
    return schema_pattern.sub(lambda _: json_script(schema), html, count=1)


def set_product_preview(html, name, image):
    for key, value in [("og:image", image), ("twitter:image", image),
                       ("og:image:alt", name), ("twitter:image:alt", name)]:
        html = meta(html, key, value)
    return re.sub(r'<meta property="og:image:(?:width|height|type)"[^>]*>\s*', "", html)


image_map = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
                                  "xmlns:image": "http://www.google.com/schemas/sitemap-image/1.1"})
java_models = []
for page in sorted(ROOT.glob("*/index.html")):
    html = page.read_text()
    schema = json.loads(schema_pattern.search(html)[1])
    if schema.get("@type") != "Product":
        continue
    url = f"{ORIGIN}/{page.parent.name}/"
    images = schema["image"] if isinstance(schema["image"], list) else [schema["image"]]
    html = set_product_preview(html, schema["name"], images[0])
    if page.parent.name.startswith("java-mix-"):
        java_models.append((urlsplit(url).path, schema["name"].split(" · ")[-1]))
    entry = ET.SubElement(image_map, "url")
    ET.SubElement(entry, "loc").text = url
    for image in dict.fromkeys(images):
        photo = ET.SubElement(entry, "image:image")
        ET.SubElement(photo, "image:loc").text = image
    page.write_text(html)

# Keep the colour-first JAVA MIX selector and expose direct model links beneath it.
model_links = "".join(f'<a href="{escape(path)}">{escape(name)}</a>' for path, name in java_models)
model_list = f'<details><summary>تصفّح بحسب نوع الخلاط</summary><div class="collections category-list">{model_links}</div></details>'
for page in ROOT.rglob("index.html"):
    html = category_links(page.read_text())
    html = html.replace('<a class="contact-card" href="catalogs/java-mix-2027.pdf"',
                        model_list + '<a class="contact-card" href="catalogs/java-mix-2027.pdf"', 1)
    page.write_text(html)

home_path = ROOT / "index.html"
home = home_path.read_text()
website = {"@context": "https://schema.org", "@type": "WebSite", "url": ORIGIN + "/",
           "name": STORE, "alternateName": "SAAD SHEIKH ALHADADEN COMPANY", "inLanguage": "ar-SY"}
home_path.write_text(schema_pattern.sub(lambda m: m[0] + "\n" + json_script(website), home, count=1))
for screen, (slug, title, description) in COLLECTIONS.items():
    destination = ROOT / slug / "index.html"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(collection_page(home, screen, slug, title, description))

ET.ElementTree(image_map).write(ROOT / "product-images.xml", encoding="utf-8", xml_declaration=True)
robots = ROOT / "robots.txt"
directive = f"Sitemap: {ORIGIN}/product-images.xml"
if directive not in robots.read_text():
    robots.write_text(robots.read_text().rstrip() + "\n" + directive + "\n")

run_path(str(Path(__file__).with_name("local_guides.py")), run_name="__main__")
