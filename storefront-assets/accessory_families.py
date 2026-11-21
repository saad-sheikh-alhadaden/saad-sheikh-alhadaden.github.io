"""Catalog data and options for concealed accessories sold in two forms."""
from html import escape
from itertools import product
from urllib.parse import urlencode

HEAD = "rain-shower-head-304"
HAND = "hand-shower-set"
OUTLET = "shower-outlet-with-holder"
TANK = "grohe-cistern"
SPOUT = "shower-spout"
JET = "shower-jet"
SMARTCONTROL = "grohtherm-smartcontrol"
SMARTBOX = "rapido-smartbox"
SIZES = {"20": 25, "25": 50, "30": 75, "40": 100}
SHAPES = {"round": "دائري", "cube": "مربّع"}
PACKAGES = {"without-plate": "بدون كبسة الدفن", "with-plate": "مع كبسة الدفن"}

SMARTCONTROL_OUTLETS = {"1": "مخرج واحد", "2": "مخرجان", "3": "٣ مخارج"}

DIVERTERS = {"without-diverter": "بدون تحويلة", "with-diverter": "مع تحويلة"}
DIVERTER_PRICES = {"without-diverter": 50, "with-diverter": 75}

# The first entry in each group is the initial selection.
FAMILIES = {
    SMARTCONTROL: dict(name="Grohtherm SmartControl", label="بياض كروهي سمارت", cover="smartcontrol",
                       category="grohe", forms=SMARTCONTROL_OUTLETS, form_title="عدد المخارج",
                       colors=("Brushed Gold", "Black", "Chrome"),
                       photos={outlet: f"smartcontrol-{outlet}" for outlet in SMARTCONTROL_OUTLETS},
                       prices={"1": {"brushed-gold": 530, "black": 460, "chrome": None},
                               "2": {"brushed-gold": 1025, "black": 925, "chrome": None},
                               "3": {"brushed-gold": 1150, "black": 1050, "chrome": None}},
                       description="واجهة التحكّم الخارجية للدش. اختر التشطيب وعدد المخارج. قلب الدفن Rapido SmartBox يُباع بشكل منفصل.",
                       search="كروهي غروهي جروهي بياض سمارت grohe smart control"),
    SMARTBOX: dict(name="Rapido SmartBox", label="قلب دفن سمارت", cover="smartbox",
                   category="grohe", price=130, photo="family-smartbox",
                   description="قلب الدفن الداخلي لنظام Grohtherm SmartControl. يُباع بشكل منفصل عن واجهة التحكّم.",
                   search="كروهي غروهي جروهي سواد داخلي قلب دفن رابيدو grohe smart box"),
    JET: dict(name="Shower Jet", label="بخّاخ مساج جانبي", cover="jet",
              description="بخّاخ جداري يوجّه نفثات الماء إلى الجسم من الجانب لتجربة مساج مائي أثناء الاستحمام. يتوفّر بتصميم مدوّر أو مربّع.",
              forms={"round": "مدوّر", "cube": "مربّع"}, colors=("Chrome", "Black", "Brushed Gold"),
              photos={"round": "jet-round", "cube": "jet-cube"}, old={},
              finish_prices={"chrome": 35, "black": 50, "brushed-gold": 50},
              search="بخاخ مساج جانبي دوش دش شاور body spray shower jet"),
    TANK: dict(name="GROHE", label="خزان دفن", cover="cistern",
               description="خزان دفن بتركيبين، مع قواعد تثبيت أو مع شاسيه. يتوفّر مع كبسة الدفن أو بدونها.",
               forms={"feet": "مع قواعد تثبيت", "frame": "مع شاسيه"},
               photos={"feet": "grohe-cistern-with-feet", "frame": "grohe-cistern"},
               old={"feet": "grohe-concealed-cistern-with-feet", "frame": "grohe-concealed-cistern"},
               prices={"feet": {"without-plate": 100, "with-plate": 125}, "frame": {"without-plate": 115, "with-plate": 140}}, search="غروهي كروهي المانيا ألمانيا"),
    HAND: dict(name="Hand Shower Set", label="طقم دش يدوي", cover="hand",
               description="طقم يضمّ سماعة دش يدوية، وخرطومًا مرنًا، وقاعدة جدارية لحمل السماعة.",
               forms=SHAPES, colors=("Black", "Gold", "Chrome"), photos={"round": "rainround", "cube": "raincube"},
               old={"round": "rain-shower-round", "cube": "rain-shower-cube"},
               prices={"round": 50, "cube": 50}, search="rain shower سماعة دش نربيش"),
    OUTLET: dict(name="Shower Outlet with Holder", label="مخرج دش مع قاعدة سماعة", cover="outlet",
                 description="مخرج مياه جداري لخرطوم الدش، مع حامل مدمج للسماعة.",
                 forms=SHAPES, colors=("Gold", "Black", "Chrome"), photos={"round": "roundoutlet", "cube": "cubeoutlet"},
                 old={"round": "round-shower-outlet", "cube": "cube-shower-outlet"},
                 prices={"round": 40, "cube": 50}, search="وصلة نربيش مخرج"),
    SPOUT: dict(name="Shower Spout", label="مصب دوش", cover="spout",
                description="مصب دوش جداري بتصميم مدوّر أو مربّع، يتوفّر مع تحويلة أو بدونها.",
                forms={"round": "مدوّر", "cube": "مربّع"}, colors=("Chrome", "Gold", "Black"),
                photos={"round": "spout-round", "cube": "spout-cube"}, old={},
                search="مصب دش شاور تحويلة محول diverter wall spout"),
    HEAD: dict(name="Shower Head 304", label="رأس دش مطري", cover="head",
               description="رأس دش مطري من الستانلس ستيل 304، بفوهات مقاومة لتراكم الكلس.",
               forms=SHAPES, colors=("Chrome", "Black", "Gold"), photos={"round": "shower304", "cube": "cubeshower304"},
               old={"round": "shower-head-304", "cube": "shower-head-cube-304"}, search="راس دش شاور تكلس"),
}


def size_text(form, size):
    return f"قطر {size} سم" if form == "round" else f"{size} × {size} سم"


def finish_options(spec):
    return {color.lower().replace(" ", "-"): color for color in spec["colors"]}


def build_family(slug):
    spec = FAMILIES[slug]
    if "photo" in spec:
        return {"standard": (spec["price"], f'/assets/{spec["photo"]}.webp', spec["label"])}, {}
    secondary = PACKAGES if slug == TANK else finish_options(spec)
    variants = {}
    legacy = {}
    third_axis = {HEAD: SIZES, SPOUT: DIVERTERS}.get(slug, ("",))
    for form, choice, option in product(spec["forms"], secondary, third_axis):
        parts = [form, choice] + ([option] if option else [])
        labels = [spec["forms"][form], secondary[choice]]
        old_choice = secondary[choice]
        photo = spec["photos"][form]
        if slug == TANK:
            price = spec["prices"][form][choice]
        else:
            photo += "-" + choice
            if slug == HEAD:
                price = SIZES[option]
                labels.append(size_text(form, option))
                old_choice += f" / {option} cm"
            elif slug == SPOUT:
                price = DIVERTER_PRICES[option]
                labels.append(DIVERTERS[option])
                photo += "-" + option
            elif slug == SMARTCONTROL:
                price = spec["prices"][form][choice]
            elif "finish_prices" in spec:
                price = spec["finish_prices"][choice]
            else:
                price = spec["prices"][form]
        key = "|".join(parts)
        variants[key] = (price, f"/assets/{photo}.webp", " · ".join(labels))
        if form in spec.get("old", {}):
            legacy.setdefault(spec["old"][form], {})[old_choice] = key
    return variants, legacy


def cover(slug):
    return f'/assets/family-{FAMILIES[slug]["cover"]}.webp'


def family_registry(slug, category):
    spec = FAMILIES[slug]
    variants, legacy = build_family(slug)
    words = " ".join(label for _, _, label in variants.values())
    return {
        "name": f'{spec["name"]} · {spec["label"]}', "price": min(v[0] for v in variants.values() if v[0] is not None),
        "category": category, "favoriteKey": "saad-saved-" + slug, "defaultColor": next(iter(variants)),
        "prices": {k: v[0] for k, v in variants.items()}, "images": {k: v[1] for k, v in variants.items()},
        "colorLabels": {k: v[2] for k, v in variants.items()}, "legacyOptions": legacy,
        "search": " ".join((spec["name"], spec["label"], spec["description"], spec["search"], words,
                            " ".join(s.replace("-", " ") for s in legacy),
                            "اسود أسود دهبي ذهبي كروم مربع كيوب" if slug != TANK else "")).lower(),
    }


def family_card(slug, registry, origin_label):
    spec = FAMILIES[slug]
    amounts = {amount for amount in registry["prices"].values() if amount is not None}
    price = f'<bdi dir="ltr">${min(amounts)}</bdi>'
    if len(amounts) > 1:
        price = "من " + price
    name = f'<bdi lang="en" dir="ltr">{spec["name"]}</bdi>'
    heading = (f'<strong>{name}</strong><span>{spec["label"]}</span>' if registry["category"] == "grohe"
               else f'<strong>{spec["label"]}</strong>{name}')
    return (f'<a class="concealed-accessory-card family-listing" href="/{slug}/">'
            f'<span class="concealed-accessory-photo"><img loading="lazy" decoding="async" src="{cover(slug)}" alt=""></span>'
            f'<span class="concealed-accessory-copy">{heading}'
            + (f'<small>{escape(origin_label)}</small>' if origin_label else '')
            + (f'<span class="family-card-forms">{" · ".join(spec["forms"].values())}</span>' if "forms" in spec else "")
            + f'<span class="concealed-accessory-prices"><span class="concealed-accessory-price"><b>{price}</b>'
            '<span class="concealed-accessory-detail">تفاصيل المنتج</span></span></span></span></a>')


def options(slug, group, title, labels, prices=None):
    chips = []
    for index, (value, label) in enumerate(labels.items()):
        swatch = f'<i class="swatch-{value}" aria-hidden="true"></i>' if group == "finish" else ""
        amount = f'<bdi data-option-price dir="ltr">${prices[value]}</bdi>' if prices else ""
        chips.append(f'<label><input type="radio" name="{slug}-{group}" value="{value}"'
                     + (' checked' if index == 0 else '') + f'><span>{swatch}<bdi data-option-label>{label}</bdi>{amount}</span></label>')
    return (f'<fieldset class="family-options" data-axis="{group}"><legend>{title}</legend>'
            f'<div class="family-choices">{"".join(chips)}</div></fieldset>')


def detail(slug, registry, warranty, origin_label, related=""):
    spec = FAMILIES[slug]
    selected = registry["defaultColor"]
    label = registry["colorLabels"][selected]
    price = registry["prices"][selected]
    tank = slug == TANK
    controls = ""
    if "forms" in spec:
        controls = options(slug, "form", "نوع التثبيت" if tank else spec.get("form_title", "الشكل"), spec["forms"],
                           spec["prices"] if slug == OUTLET else None)
        if tank:
            controls += options(slug, "package", "كبسة الدفن", PACKAGES, spec["prices"]["feet"])
        else:
            controls += options(slug, "finish", "التشطيب", finish_options(spec), spec.get("finish_prices"))
        if slug == HEAD:
            controls += options(slug, "size", "مقاس رأس الدش", {s: size_text("round", s) for s in SIZES}, SIZES)
        if slug == SPOUT:
            controls += options(slug, "diverter", "التحويلة", DIVERTERS, DIVERTER_PRICES)
    origin = f'<span class="velato-origin">{escape(origin_label)}</span>' if origin_label else ''
    return f"""
<section id="{slug}" class="vanity-detail family-product" data-nosnippet hidden>
  <div class="product-image"><img src="{registry["images"][selected]}" alt="{spec["label"]} · {label}" width="790" height="988" loading="lazy" decoding="async">
    <button class="circle" data-save type="button" aria-label="إضافة إلى المفضّلة" aria-pressed="false">♡</button></div>
  <div class="product-info"><p class="category">{spec["label"]}</p><h1><bdi dir="ltr">{spec["name"]}</bdi></h1>
    {origin}<p>{spec["description"]}</p>{controls}
    <div class="family-summary" aria-live="polite" aria-atomic="true"><div><strong>سعر القطعة</strong><span data-family-summary>{label}</span></div>
    <bdi dir="ltr" data-unit-price>${price:,}</bdi></div>
    <div class="qty"><span>الكمية</span><button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button><output data-quantity>1</output><button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button></div>
    <button class="action" data-add-cart type="button">أضف إلى السلة — ${price:,}</button>{related}{warranty}
  </div></section>"""


def product_data(slug, registry, origin, country):
    spec = FAMILIES[slug]
    url = f"{origin}/{slug}/"
    axes = ["form", "package" if slug == TANK else "finish", "diverter" if slug == SPOUT else "size"]
    offers = [{"@type": "Offer", "name": registry["colorLabels"][key], "price": amount, "priceCurrency": "USD",
               "url": url if "photo" in spec else url + "?" + urlencode(dict(zip(axes, key.split("|"))))}
              for key, amount in registry["prices"].items() if amount is not None]
    images = dict.fromkeys([cover(slug), *registry["images"].values()])
    data = {"@type": "Product", "@id": url + "#product", "sku": slug,
            "image": [origin + path for path in images], "offers": offers}
    if country:
        data["countryOfOrigin"] = {"@type": "Country", "name": country}
    if "colors" in spec:
        data["color"] = list(spec["colors"])
    return data


def write_legacy_pages(root, origin):
    for slug, spec in FAMILIES.items():
        for form, previous in spec.get("old", {}).items():
            dest = f"/{slug}/?form={form}"
            page = (f'<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>{spec["label"]} {spec["name"]}</title>'
                    f'<link rel="canonical" href="{origin}/{slug}/"><meta http-equiv="refresh" content="0;url={dest}">'
                    f'<a href="{dest}">{escape(spec["label"])}</a></html>')
            folder = root / previous
            folder.mkdir(exist_ok=True)
            (folder / "index.html").write_text(page)
