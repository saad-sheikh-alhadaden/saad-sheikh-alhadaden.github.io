"""Create crawlable collection pages and describe existing storefront photos."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
from runpy import run_path
from urllib.parse import urlsplit

# This generator is also executed with run_path from the archived catalog installer.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import accessory_families
import milano_brand

ROOT = Path("storefront")
ORIGIN = "https://saad-customer-app.onrender.com"
STORE = "شركة سعد شيخ الحدادين"
DECOR_BASIN_COLLECTIONS = {
    "decorative-vessel-basins": ("أجران مغسلة ديكور", "Decorative Vessel Basins"),
    "freestanding-pedestal-basins": ("مغاسل برميل ديكور", "Freestanding Pedestal Basin"),
}

COLLECTIONS = {
    **{slug: (slug, f"{arabic} | {english}", f"تصفّح قسم {arabic} لدى {STORE}.")
       for slug, (arabic, english) in DECOR_BASIN_COLLECTIONS.items()},
    "mixers": ("mixers", "خلاطات مغاسل فاخرة في دمشق | Trend Of Mixer", "تصفّح خلاطات المغاسل والمطبخ من شركة سعد شيخ الحدادين في دمشق وقارن صور الموديلات وألوانها وأسعارها بالدولار."),
    "showers": ("smart-showers", "أنظمة دش وشاورات ذكية في دمشق | Smart Shower", "اكتشف أنظمة الدش والشاور الذكي من شركة سعد شيخ الحدادين في دمشق. تصفّح صور الموديلات مثل Ferrari وVera وMidas مع الألوان والأسعار."),
    "washbasins": ("washbasins", "مغاسل حمام مع خزائن في دمشق", "تصفّح أقسام المغاسل والكبائن من شركة سعد شيخ الحدادين في دمشق، واختر عرض الكابينت المناسب لحمّامك."),
    "cabinet-luxury": ("cabinet-luxury", "خزائن ومغاسل حمام فوم PVC | Cabinet Luxury", "قارن كابينتات مغاسل الحمّام من فوم PVC بحسب المقاس واللون والسعر في متجر سعد شيخ الحدادين، دمشق."),
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
    return html.replace('href="#contact"', 'href="/branches/#contact"')


def screen_page(home, screen, slug, title, description, page_type="CollectionPage"):
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
    schema = {"@context": "https://schema.org", "@type": page_type, "name": title,
              "description": description, "url": url, "inLanguage": "ar-SY"}
    return schema_pattern.sub(lambda _: json_script(schema), html, count=1)


def set_product_preview(html, name, image):
    for key, value in [("og:image", image), ("twitter:image", image),
                       ("og:image:alt", name), ("twitter:image:alt", name)]:
        html = meta(html, key, value)
    return re.sub(r'<meta property="og:image:(?:width|height|type)"[^>]*>\s*', "", html)


V20_PHOTO_ALT = "مغسلة V20 بخزانة سوداء مخدّدة وشريط ذهبي، وفوقها مرآة مضاءة بإطار ذهبي"


def publish_product_photos(root):
    legacy = "cabinet-v20-black.webp"
    photo = Path(__file__).with_name("cabinet-v20-black-gold-90x50.webp")
    data = photo.read_bytes()
    for name in (legacy, photo.name):
        (root / "assets" / name).write_bytes(data)

    home = (root / "index.html").read_text()
    old_script = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    registry = (root / old_script).read_text()
    if legacy not in registry:
        raise ValueError("Missing V20 image in the storefront registry")
    # Each JAVA MIX set shows the matching Cube mixer photo in its selected finish.
    wall_key = "java-mix-wall-kitchen-mixer"
    old_label = "خلاط مجلى جداري"
    wall_label = "خلاط جداري كيوب"
    wall_entry = re.compile(rf'^  "{wall_key}": .*$', re.M)
    registry = wall_entry.sub(lambda m: m[0].replace(old_label, wall_label), registry)
    # Match the standalone model name and its catalogue qualifiers in page templates.
    wall_name_in_page = re.compile(re.escape(old_label) + r'(?=["<.]| [·–]| (?:من )?JAVA MIX)')
    photo_names = {legacy: photo.name}
    for model_key, prefix in (("java-mix-tall-mixer", "java-mix-cube-kitchen-mixer"),
                              (wall_key, "java-mix-cube-wall-kitchen-mixer")):
        model = json.loads(re.search(rf'^  "{model_key}": (\{{.*\}}),?$', registry, re.M)[1])
        for finish, path in model["images"].items():
            suffix = finish.lower().replace(" ", "-")
            photo_names[Path(path).name] = f"{prefix}-{suffix}-01.webp"
    bath_key = "java-mix-shower-mixer"
    bath_label = "خلاط بانيو كيوب"
    bath_entry = re.compile(rf'^  "{bath_key}": .*$', re.M)
    registry = bath_entry.sub(lambda m: m[0].replace("خلاط حمام", bath_label), registry)
    bath_name_in_page = re.compile(r'خلاط حمام(?=["<.]|، خلاط تواليت| [·–]| (?:من )?JAVA MIX)')
    def rename_mini(text):
        return re.sub(r"Mini Basin Mixer Tap", "Mixer Basin Cube Mini",
                      text.replace("خلاط مغسلة شك ميني", "خلاط مغسلة كيوب يميني"), flags=re.I)

    def rename_toilet(text):
        text = re.sub(r'خلاط تواليت(?=["<.]|، خلاط مجلى| [·–]| (?:من )?JAVA MIX)', "خلاط تواليت كيوب", text)
        return re.sub(r'(?<!Concealed )\bToilet Mixer(?=["<]| [·|])', "Mixer Toilet Cube", text)

    toilet_entry = re.compile(r'^  "java-mix-toilet-mixer": .*$', re.M)
    registry = toilet_entry.sub(lambda m: rename_toilet(m[0].replace("خلاط تواليت", "خلاط تواليت كيوب")), registry)
    registry = rename_mini(registry)
    for model_key, folder in ((bath_key, "bath-cube"), ("java-mix-mini-basin-mixer", "mini-cube"),
                              ("java-mix-toilet-mixer", "toilet-cube")):
        model = json.loads(re.search(rf'^  "{model_key}": (\{{.*\}}),?$', registry, re.M)[1])
        for finish, path in model["images"].items():
            slug = finish.lower().replace(" & ", " ").replace(" ", "-")
            filename = f"java-mix-{folder}-{slug}.webp"
            source = Path(__file__).with_name(folder) / filename
            (root / "assets" / filename).write_bytes(source.read_bytes())
            photo_names[Path(path).name] = filename
    finishes = json.loads(re.search(r'^const javaMixFinishes = (\{.*\});$', registry, re.M)[1])
    for slug in finishes:
        filename = f"java-mix-set-{slug}.webp"
        source = Path(__file__).with_name("java-covers") / filename
        (root / "assets" / filename).write_bytes(source.read_bytes())
        photo_names[f"java-mix-{slug}-cover.webp"] = filename
    cube_names = (
        ("خلاط مجلى أو مغسلة شك عالي", "خلاط مجلى كيوب", "Kitchen or Tall Basin Mixer",
         "Mixer Kitchen Cube", "خلاط شك عالي يُركّب على سطح المجلى أو المغسلة، بمصبّ مرتفع يترك مساحة أوسع تحت الخلاط، ومقبض جانبي للتحكّم بتدفّق المياه وحرارتها."),
        ("خلاط مجلى أو مغسلة جداري", wall_label, "Wall-mounted Kitchen Mixer",
         "Wall Mixer Cube", "خلاط يُركّب على الحائط فوق المجلى أو المغسلة، بمصبّ مقوّس مرتفع ومقبض أمامي مسطّح للتحكّم بتدفّق المياه وحرارتها."),
    )
    for old_ar, new_ar, old_en, new_en, _ in cube_names:
        registry = registry.replace(old_ar, new_ar).replace(old_en, new_en)

    names = re.compile("|".join(re.escape(name) for name in photo_names))

    def update_photo_names(text):
        return names.sub(lambda match: photo_names[match[0]], text)

    registry = update_photo_names(registry)
    java_page = 'const javaMixPage = javaMixModelIds.has(document.documentElement.dataset.screen);'
    if java_page not in registry:
        raise ValueError("Missing JAVA MIX product navigation in the storefront registry")
    registry = registry.replace(java_page, """
const javaFinishGallery = document.documentElement.dataset.screen === "java-mix"
  && Object.hasOwn(javaMixFinishes, requestedFinish);
const javaMixPage = javaFinishGallery || javaMixModelIds.has(document.documentElement.dataset.screen);

if (javaFinishGallery) {
  document.documentElement.dataset.javaGallery = "";
  for (const screen of screens.filter(section => javaMixModelIds.has(section.id))) {
    screen.classList.add("java-gallery-model");
    const selector = document.createElement("nav");
    selector.className = "java-gallery-selector";
    selector.setAttribute("aria-label", "خلاطات الطقم");
    const heading = document.createElement("p");
    heading.className = "java-gallery-heading";
    heading.dir = "ltr";
    heading.textContent = "JAVA MIX · " + javaMixFinishes[javaMixFinish];
    const thumbnails = document.createElement("div");
    thumbnails.className = "java-gallery-thumbnails";
    for (const choice of screen.querySelectorAll("[data-mixer-choice]")) {
      const model = choice.dataset.mixerChoice;
      const link = document.createElement("a");
      link.href = "#" + model;
      link.setAttribute("aria-label", choice.textContent.trim());
      if (model === screen.id) link.setAttribute("aria-current", "true");
      const image = document.createElement("img");
      image.src = products[model].images[javaMixFinishes[javaMixFinish]];
      image.alt = "";
      image.width = 790;
      image.height = 988;
      image.loading = "lazy";
      link.append(image);
      thumbnails.append(link);
    }
    selector.append(heading, thumbnails);
    screen.prepend(selector);
  }
}
""".strip())
    if '? "java-mix-" + requestedFinish : baseScreen;' not in registry:
        raise ValueError("Missing JAVA MIX finish entry in the storefront registry")
    registry = registry.replace('? "java-mix-" + requestedFinish : baseScreen;',
                                '? firstJavaMixModel : baseScreen;')

    new_script = f"assets/storefront-{sha256(registry.encode()).hexdigest()[:12]}.js"
    (root / new_script).write_text(registry)

    for page in root.rglob("index.html"):
        html = page.read_text().replace(old_script, new_script)
        html = html.replace(f'src="/assets/{legacy}" width="790" height="988"',
                            f'src="/assets/{photo.name}" width="1229" height="1536"')
        html = html.replace('alt="كابينت مغسلة V20 بلون أسود"', f'alt="{V20_PHOTO_ALT}"')
        html = update_photo_names(html)
        html = wall_name_in_page.sub(wall_label, html)
        html = rename_toilet(rename_mini(bath_name_in_page.sub(bath_label, html)))
        for old_ar, new_ar, old_en, new_en, description in cube_names:
            subtitle = f'<p class="product-description"><bdi dir="ltr">{old_en}</bdi></p>'
            replacement = (f'<p class="product-description"><bdi lang="en" dir="ltr">{new_en}</bdi></p>'
                           f'<p class="product-description" lang="ar" dir="rtl">{description}</p>')
            html = html.replace(subtitle, replacement).replace(old_en, new_en).replace(old_ar, new_ar)
        if page.parent.name == "cabinet-v20":
            html = html.replace("كابينت مغسلة V20 بلون أسود، مقاس",
                                "مغسلة حمّام V20 مع خزانة سوداء معلّقة بواجهة مخدّدة وشريط ذهبي، مقاس")
        page.write_text(html)


run_path(str(Path(__file__).with_name("cabinet_b604.py")), run_name="__main__")
publish_product_photos(ROOT)
velato = run_path(str(Path(__file__).with_name("velato.py")))
velato["publish"](ROOT, ORIGIN, STORE, meta, set_product_preview, schema_pattern, json_script)

porcelain = run_path(str(Path(__file__).with_name("porcelain.py")))
porcelain["publish"](ROOT, ORIGIN, screen_page, schema_pattern, json_script)
porcelain["publish_kitchen"](ROOT, ORIGIN, screen_page, schema_pattern, json_script)

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
    image_label = V20_PHOTO_ALT if page.parent.name == "cabinet-v20" else schema["name"]
    html = set_product_preview(html, image_label, images[0])
    if page.parent.name.startswith("java-mix-"):
        java_models.append((urlsplit(url).path, schema["name"].split(" · ")[-1]))
    entry = ET.SubElement(image_map, "url")
    ET.SubElement(entry, "loc").text = url
    for image in dict.fromkeys(images):
        photo = ET.SubElement(entry, "image:image")
        ET.SubElement(photo, "image:loc").text = image
    page.write_text(html)

def add_decor_basin_sections(html):
    vessel, pedestal = DECOR_BASIN_COLLECTIONS
    vessel_arabic, vessel_english = DECOR_BASIN_COLLECTIONS[vessel]
    pedestal_arabic, pedestal_english = DECOR_BASIN_COLLECTIONS[pedestal]
    vessel_card = (f'<a href="/{vessel}/"><strong>{vessel_arabic}</strong>'
                   f'<small><bdi lang="en" dir="ltr">{vessel_english}</bdi></small></a>')
    pedestal_card = (f'<a class="velato-feature" href="/{pedestal}/"><span>'
                     f'<strong>{pedestal_arabic}</strong><br><bdi lang="en" dir="ltr">{pedestal_english}</bdi>'
                     '<small>استعرض المغاسل</small></span></a>')
    panels = "".join(
        f'<section class="panel" id="{slug}" hidden><h1>{arabic}<br>'
        f'<bdi lang="en" dir="ltr">{english}</bdi></h1>'
        '<p>ستُضاف الموديلات قريباً.</p>'
        '<a class="contact-card" href="/washbasins/">المغاسل والكبائن</a></section>'
        for slug, (arabic, english) in DECOR_BASIN_COLLECTIONS.items()
    )

    def add_cards(match):
        panel = match[0]
        panel = panel.replace('</div><div class="vanity-filter"', vessel_card + '</div><div class="vanity-filter"', 1)
        return panel.replace("</section>", pedestal_card + "</section>" + panels, 1)

    return re.sub(r'<section class="panel" id="washbasins"[^>]*>.*?</section>',
                  add_cards, html, count=1, flags=re.S)


def java_finish_panels(root, models):
    home = (root / "index.html").read_text()
    script = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    registry = (root / script).read_text()
    finishes = json.loads(re.search(r'^const javaMixFinishes = (\{.*\});$', registry, re.M)[1])
    cards = {slug: [] for slug in finishes}
    for path, name in models:
        key = path.strip("/")
        model = json.loads(re.search(rf'^  "{re.escape(key)}": (\{{.*\}}),?$', registry, re.M)[1])
        for slug, finish in finishes.items():
            cards[slug].append(
                f'<a class="hero mixer-product java-finish-card" href="{path}?color={slug}">'
                f'<img src="{escape(model["images"][finish])}" loading="lazy" width="790" height="988" '
                f'alt="{escape(name)} · {escape(finish)}"><div class="java-finish-copy">'
                f'<strong>{escape(name)}</strong><span dir="ltr">${model["prices"][finish]}</span></div></a>'
            )
    return "".join(
        f'<section class="panel" id="java-mix-{slug}" data-java-finish="{slug}" hidden>'
        f'<header class="java-finish-heading"><h1 lang="en" dir="ltr">JAVA MIX</h1>'
        f'<span><bdi lang="en" dir="ltr">{escape(label)}</bdi></span></header>'
        f'<div class="java-finish-list">'
        f'{"".join(cards[slug])}</div></section>'
        for slug, label in finishes.items()
    )


# A finish opens a list of models. Individual model links keep the same finish.
finish_panels = java_finish_panels(ROOT, java_models)
model_links = "".join(f'<a href="{escape(path)}">{escape(name)}</a>' for path, name in java_models)
model_list = f'<details><summary>تصفّح بحسب نوع الخلاط</summary><div class="collections category-list">{model_links}</div></details>'


def add_java_collection(match):
    panel = match[0].replace('href="/java-mix-mini-basin-mixer/?color=', 'href="/java-mix/?color=')
    panel = panel.replace('<a class="contact-card" href="catalogs/java-mix-2027.pdf"',
                          model_list + '<a class="contact-card" href="catalogs/java-mix-2027.pdf"', 1)
    return panel + finish_panels


for page in ROOT.rglob("index.html"):
    html = add_decor_basin_sections(category_links(page.read_text()))
    html = re.sub(r'<section class="panel" id="java-mix"[^>]*>.*?</section>',
                  add_java_collection, html, count=1, flags=re.S)
    page.write_text(html)

home_path = ROOT / "index.html"
home = home_path.read_text()
website = {"@context": "https://schema.org", "@type": "WebSite", "url": ORIGIN + "/",
           "name": STORE, "alternateName": "SAAD SHEIKH ALHADADEN COMPANY", "inLanguage": "ar-SY"}
home_path.write_text(schema_pattern.sub(lambda m: m[0] + "\n" + json_script(website), home, count=1))
for screen, (slug, title, description) in COLLECTIONS.items():
    destination = ROOT / slug / "index.html"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(screen_page(home, screen, slug, title, description))

branches = ROOT / "branches"
branches.mkdir(exist_ok=True)
branches.joinpath("index.html").write_text(screen_page(
    home, "contact", "branches", "فروع الأدوات الصحية في دمشق وريف دمشق",
    "عنوان ورقم هاتف فرعي شركة سعد شيخ الحدادين في المناخلية بدمشق وعين ترما بريف دمشق، مع روابط الخرائط والتواصل.",
    page_type="ContactPage",
))

ET.ElementTree(image_map).write(ROOT / "product-images.xml", encoding="utf-8", xml_declaration=True)
robots = ROOT / "robots.txt"
directive = f"Sitemap: {ORIGIN}/product-images.xml"
if directive not in robots.read_text():
    robots.write_text(robots.read_text().rstrip() + "\n" + directive + "\n")

guides = run_path(str(Path(__file__).with_name("local_guides.py")), run_name="__main__")

catalog_search = run_path(str(Path(__file__).with_name("catalog_search.py")))
catalog_search["publish"](ROOT, ORIGIN, STORE, guides["BRANCHES"])

sharing = run_path(str(Path(__file__).with_name("storefront_share.py")), run_name="__main__")

# Publish shared storefront styles and photo controls.
publish_asset = sharing["publish_asset"]
milano_logo = publish_asset(ROOT, Path(__file__).with_name("milano-italy-bronze.webp"))
ferrari_logo = publish_asset(ROOT, Path(__file__).with_name("ferrari-red.webp"))
milano_css = publish_asset(ROOT, Path(__file__).with_name("storefront-milano.css"))
logo = Path(__file__).with_name("saad-watermark-gold.webp")
(ROOT / "assets" / logo.name).write_bytes(logo.read_bytes())
branch_css = publish_asset(ROOT, Path(__file__).with_name("storefront-branches.css"))
finish_css = publish_asset(ROOT, Path(__file__).with_name("storefront-finishes.css"))
finish_picker = publish_asset(ROOT, Path(__file__).with_name("storefront-finish-picker.js"))
photo_css = publish_asset(ROOT, Path(__file__).with_name("storefront-photos.css"))
photo_js = publish_asset(ROOT, Path(__file__).with_name("storefront-photos.js"))
photo_controls = f'<link rel="stylesheet" href="{photo_css}"><script defer src="{photo_js}"></script>'
home_cover_js = Path(__file__).with_name("storefront-home-cover.js").read_text()

# The catalog generator supplies one cart handler shared by all product screens.
home = (ROOT / "index.html").read_text()
cart_script = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
cart_js = (ROOT / cart_script).read_text()
# Preserve old finish bookmarks and choose the matching model grid on direct entry.
cart_js = cart_js.replace('/${firstJavaMixModel}/?color=${hash.slice(', '/java-mix/?color=${hash.slice(')
initial_screen = 'const initialScreen = document.documentElement.dataset.screen || "home";'
if cart_js.count(initial_screen) != 1:
    raise ValueError("Missing storefront initial screen")
cart_js = cart_js.replace(initial_screen, '''const baseScreen = document.documentElement.dataset.screen || "home";
  const initialScreen = baseScreen === "java-mix" && Object.hasOwn(javaMixFinishes, requestedFinish)
    ? "java-mix-" + requestedFinish : baseScreen;''')
cart_hooks = {
    '  const syncOrder = () => {': '''  const confirmation = cartConfirmationFor(addButton);
  const syncOrder = () => {
    confirmation.clear();''',
    '  addButton.addEventListener("click", () => {': '''  addButton.addEventListener("click", () => {
    if (addButton.hasAttribute("data-cart-added")) return;''',
    '    addCatalogItem(id, orderColor(), quantity);\n    location.hash = "#cart";': '''    addCatalogItem(id, orderColor(), quantity);
    confirmation.show(product, orderColor(), quantity);''',
}
for original, replacement in cart_hooks.items():
    if cart_js.count(original) != 1:
        raise ValueError(f"Expected one shared cart handler containing {original}")
    cart_js = cart_js.replace(original, replacement)
cart_js += "\n" + Path(__file__).with_name("storefront-cart-feedback.js").read_text()
updated_cart_script = f"assets/storefront-{sha256(cart_js.encode()).hexdigest()[:12]}.js"
(ROOT / updated_cart_script).write_text(cart_js)

washbasin_cards = (
    ("/cabinet-luxury/", "CABINET LUXURY", "كابينتات فخمة", "مغاسل كابينت فاخرة", "Luxury Bathroom Vanities"),
    ("/porcelain/", "Porcelain", "بورسلان", "مغاسل بورسلان", "Porcelain Basins"),
    ("#granite", "Granite", "غرانيت", "مغاسل غرانيت", "Granite Basins"),
)

for page in ROOT.rglob("index.html"):
    markup = page.read_text()
    markup = milano_brand.add_to_products(markup, milano_logo, ferrari_logo)
    markup = re.sub(
        r'(<a\b[^>]*\bhref="(?:#toilets|/toilets/)"[^>]*>)\s*تواليت\s*<bdi\b[^>]*>Toilet</bdi>\s*</a>',
        r'\1<strong>كراسي تواليت</strong><small><bdi lang="en" dir="ltr">Toilets</bdi></small></a>',
        markup,
    )
    markup = re.sub(
        r'(<a href="(?:#encastre|/encastre/)">)دفن(?=<small><bdi lang="en" dir="ltr">Encastre</bdi>)',
        r'\1خلاطات دفن',
        markup,
    )
    markup = re.sub(
        r'(<a href="(?:#mixers|/mixers/)">)Trend Of Mixer<small>الخلاطات الفاخرة</small></a>',
        r'\1<span>الخلاطات الفاخرة</span><small><strong><bdi lang="en" dir="ltr">Trend Of Mixer</bdi></strong></small></a>',
        markup,
    )
    markup = re.sub(
        r'<a href="(?:#washbasins|/washbasins/)">المغاسل والكبائن</a>(?=<a href="(?:#accessories|/accessories/)")',
        '<a href="/washbasins/"><strong>المغاسل والكبائن</strong>'
        '<small><bdi lang="en" dir="ltr">Basins &amp; Vanities</bdi></small></a>',
        markup,
    )
    for href, old_english, old_arabic, arabic, english in washbasin_cards:
        original = f'<a href="{href}"><bdi lang="en" dir="ltr">{old_english}</bdi><small>{old_arabic}</small></a>'
        updated = f'<a href="{href}"><strong>{arabic}</strong><small><bdi lang="en" dir="ltr">{english}</bdi></small></a>'
        markup = markup.replace(original, updated)
    if cart_script in markup:
        markup = markup.replace(f'<script src="/{cart_script}"',
                                '<div id="cart-feedback" role="status" aria-atomic="true"></div>\n'
                                f'<script src="/{updated_cart_script}"')
        # Select the cover as soon as its link is parsed, before the main catalog script.
        markup, count = re.subn(r'(<a class="hero" href="/cobra-plus-2027/">.*?</a>)',
                                lambda m: m[0] + f'\n<script>{home_cover_js}</script>',
                                markup, count=1, flags=re.S)
        if not count:
            raise ValueError(f"Missing home cover in {page}")
    if not re.search(r"<img\b", markup, re.I):
        continue
    markup = markup.replace("<span>أول سنتين تبديل</span>", "<span>تبديل فوري خلال أول سنتين، وصيانة خلال السنوات الثلاث التالية.</span>")
    collection_alignment = """<style>
.category-list > a {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding-inline: 1.3rem;
    text-align: center;
}
.category-list > a::after {
    position: absolute;
    inset-inline-end: .45rem;
    top: 50%;
    transform: translateY(-50%);
}
.category-list > a > small { margin-block-start: .2rem; }
a.top-ten-entry { position: relative; justify-content: center; text-align: center; padding-inline: 3.2rem; }
.top-ten-entry .top-ten-title { text-align: center; }
a.top-ten-entry .top-ten-arrow { position: absolute; inset-inline-end: .75rem; }
.velato-feature > span { text-align: center; }
[data-java-finish] {
    --java-gold: #dfbd86;
    max-width: 45rem;
    margin-inline: auto;
}
.java-finish-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: .5rem 1rem;
    padding-block: .3rem .8rem;
    margin-block-end: .95rem;
    border-block-end: 1px solid #6e5739;
}
[data-java-finish] .java-finish-heading h1 {
    margin: 0;
    font-size: clamp(1.45rem, 4.8vw, 2rem);
    letter-spacing: .065em;
}
.java-finish-heading > span {
    color: var(--java-gold);
    font-size: .78rem;
    letter-spacing: .035em;
}
.java-finish-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.1rem .8rem;
}
[data-java-finish] .java-finish-card {
    display: block;
    align-self: start;
    margin: 0;
    padding: 0 0 .65rem;
    color: #f7f0e6;
    background: transparent;
    border: 0;
    border-block-end: 1px solid #594936;
    border-radius: 0;
    text-decoration: none;
}
.java-finish-card:first-child { grid-column: 1 / -1; }
[data-java-finish] .java-finish-card > img {
    display: block;
    width: 100%;
    height: auto;
    margin: 0;
    border-radius: .45rem;
    aspect-ratio: 790 / 988;
    object-fit: contain;
}
[data-java-finish] .java-finish-card:first-child > img {
    max-height: min(59svh, 30rem);
    background: #17191a;
}
.java-finish-copy {
    display: grid;
    gap: .25rem;
    padding: .52rem .1rem 0;
    text-align: start;
}
.java-finish-copy strong { font-size: .92rem; line-height: 1.5; }
.java-finish-copy > span { color: var(--java-gold); font-size: .87rem; justify-self: start; }
.java-finish-card:first-child .java-finish-copy {
    grid-template-columns: 1fr auto;
    align-items: baseline;
    gap: .55rem;
}
.java-finish-card:first-child .java-finish-copy strong {
    font-size: clamp(1.08rem, 3.8vw, 1.35rem);
}
.java-finish-card:focus-visible { outline: 2px solid var(--java-gold); outline-offset: 3px; }
@media (min-width: 760px) {
    .java-finish-list { gap: 1.4rem 1.1rem; }
}
[data-java-gallery] main > .java-gallery-model:not([hidden]) {
    max-width: 54rem;
    margin-inline: auto;
    background: #171512;
    color: #f5eee2;
}
.java-gallery-selector {
    padding: .8rem clamp(.8rem, 4vw, 1.4rem) .85rem;
}
.java-gallery-heading {
    margin: 0 0 .65rem;
    color: #e1c296;
    text-align: center;
    font-size: .8rem;
    letter-spacing: .09em;
}
.java-gallery-thumbnails {
    display: grid;
    max-width: 23rem;
    margin-inline: auto;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: .45rem;
}
.java-gallery-thumbnails > a {
    display: block;
    padding: 2px;
    border: 1px solid #655541;
    border-radius: .5rem;
}
.java-gallery-thumbnails > a[aria-current] { border-color: #e1c296; }
.java-gallery-thumbnails img {
    display: block;
    width: 100%;
    height: auto;
    aspect-ratio: 4 / 5;
    border-radius: .32rem;
}
[data-java-gallery] .java-gallery-model > .product-image > img {
    width: 100%;
    height: min(52svh, 34rem);
    object-fit: contain;
}
[data-java-gallery] .java-gallery-model > .product-info {
    background: #171512;
    color: #f5eee2;
    padding: 1rem clamp(1rem, 4vw, 2rem) 1.5rem;
}
[data-java-gallery] .java-gallery-model .product-info h1 {
    font-size: clamp(1.45rem, 5vw, 2.05rem);
}
[data-java-gallery] .java-gallery-model .product-info .product-description,
[data-java-gallery] .java-gallery-model .product-info .price-tag { color: #e1c296; }
[data-java-gallery] .java-gallery-model :is(.store-photo-strip, .catalog-trail, .product-info .category,
    .options:has([data-mixer-choice]), p:has(+ .options [data-mixer-choice])) { display: none; }
</style>"""
    controls = (collection_alignment + f'<link rel="stylesheet" href="{finish_css}">'
                f'<script defer src="{finish_picker}"></script>' + photo_controls)
    if 'class="milano-brand"' in markup:
        controls += f'<link rel="stylesheet" href="{milano_css}">'
    if 'class="branch-links"' in markup:
        controls += f'<link rel="stylesheet" href="{branch_css}">'
    markup, count = re.subn(r"(<title\b[^>]*>)", lambda match: controls + match[0], markup, count=1, flags=re.I)
    if not count:
        raise ValueError(f"Missing page title in {page}")
    page.write_text(markup)

# Write legacy entry points after generators that expect full product pages.
accessory_families.write_legacy_pages(ROOT, ORIGIN)
