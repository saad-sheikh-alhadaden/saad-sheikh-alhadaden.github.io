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
ESSENCE = "grohe-essence-basin-mixer"
ESSENCE_BODY = "grohe-universal-concealed-body"
SMARTCONTROL = "grohtherm-smartcontrol"
SMARTACTIVE = "rainshower-smartactive"
SMARTACTIVE_HAND = "rainshower-smartactive-hand-shower"
GROHE_WALL_OUTLET = "grohe-wall-outlet"
GROHE_BATH_SPOUT = "grohe-bath-spout"
SMARTBOX = "rapido-smartbox"
GROHE_SHOWER_BODY = "grohe-concealed-shower-mixer-body"
GROHE_TOILET_BODY = "grohe-concealed-toilet-mixer-body"
SIZES = {"20": 25, "25": 50, "30": 75, "40": 100}
SHAPES = {"round": "دائري", "cube": "مربّع"}
PACKAGES = {"without-plate": "بدون كبسة الدفن", "with-plate": "مع كبسة الدفن"}

SMARTCONTROL_OUTLETS = {"1": "مخرج واحد", "2": "مخرجان", "3": "٣ مخارج"}

DIVERTERS = {"without-diverter": "بدون تحويلة", "with-diverter": "مع تحويلة"}
DIVERTER_PRICES = {"without-diverter": 50, "with-diverter": 75}

# The first entry in each group is the initial selection.
FAMILIES = {
    ESSENCE: dict(
        name="GROHE Essence Basin Mixer", label="خلاط مغسلة دفن", cover="essence-mixer",
        category="grohe", colors=("Brushed Gold", "Black", "Chrome"),
        finish_photos={finish: f"essence-{finish}" for finish in ("brushed-gold", "black", "chrome")},
        finish_prices={"brushed-gold": 450, "black": 350, "chrome": 250},
        required_body=ESSENCE_BODY, card_note="الجزء الظاهر · قلب الدفن يُباع منفصلاً",
        description="خلاط مغسلة جداري من مجموعة Essence، بمصبّ انسيابي ومقبض منفصل للتحكّم بالمياه.",
        search="غروهي كروهي جروهي ايسنس خلاط مغسلة دفن بياض basin mixer essence",
    ),
    ESSENCE_BODY: dict(
        name="Universal Concealed Body", label="قلب دفن خلاط المغسلة", cover="essence-body",
        category="grohe", price=160, photo="family-essence-body",
        description="قلب الدفن الداخلي اللازم لتركيب خلاط مغسلة GROHE Essence، ويُباع بشكل منفصل عن الجزء الظاهر.",
        search="غروهي كروهي جروهي سواد قلب دفن خلاط المغسلة rough-in universal concealed body",
    ),
    SMARTCONTROL: dict(name="Grohtherm SmartControl", label="بياض كروهي سمارت", cover="smartcontrol",
                       category="grohe", forms=SMARTCONTROL_OUTLETS, form_title="عدد المخارج",
                       colors=("Brushed Gold", "Black", "Chrome"),
                       photos={outlet: f"smartcontrol-{outlet}" for outlet in SMARTCONTROL_OUTLETS},
                       prices={"1": {"brushed-gold": 530, "black": 460, "chrome": None},
                               "2": {"brushed-gold": 1025, "black": 925, "chrome": None},
                               "3": {"brushed-gold": 1150, "black": 1050, "chrome": None}},
                       description="واجهة التحكّم الخارجية للدش. اختر التشطيب وعدد المخارج. قلب الدفن Rapido SmartBox يُباع بشكل منفصل.",
                       search="كروهي غروهي جروهي بياض سمارت grohe smart control"),
    SMARTACTIVE: dict(name="Rainshower SmartActive", label="طاسة دش جروهي", cover="smartactive",
                      category="grohe", colors=("Brushed Gold", "Black", "Chrome"),
                      finish_photos={finish: f"smartactive-{finish}" for finish in ("brushed-gold", "black", "chrome")},
                      finish_prices={"brushed-gold": 750, "black": 450, "chrome": None},
                      card_note="قطر 30 سم · السعر يشمل ساعد الدش",
                      detail_photo=dict(file="smartactive-face", size=(774, 1000),
                                        title="تفاصيل وجه الطاسة",
                                        caption="لقطة مقرّبة لفوّهات الرش الخارجية والفتحات الطولية في المنتصف.",
                                        alt="لقطة مقرّبة لوجه طاسة الدش تُظهر الفوّهات الخارجية وفتحات الرش الوسطى"),
                      description="رأس دش دائري بقطر 30 سم، بتصميم نحيف وعصري. السعر يشمل ساعد الدش.",
                      sprays={
                          "PureRain": "رذاذ مطري ناعم وواسع ينساب من الفوّهات الخارجية ليغطّي الجسم بالكامل.",
                          "ActiveRain": "تدفّق قوي ومركّز من ثماني فتحات طولية في المنتصف، مناسب للتدليك المائي وشطف الشامبو بسرعة.",
                      },
                      control_note="لاختيار نمط الرش، يلزم خلاط SmartControl أو محوّل ثنائي المخارج (2-way diverter). يمكن تشغيل النمطين معًا إذا كانت وحدة التحكّم تدعم ذلك.",
                      search="كروهي غروهي جروهي طاسة رأس راس دش مطري ساعد 30 cm rain shower pure rain active rain"),
    SMARTACTIVE_HAND: dict(
        name="Rainshower SmartActive", label="سماعة دش", cover="smartactive-hand",
        category="grohe", colors=("Brushed Gold", "Black", "Chrome"),
        finish_photos={finish: f"smartactive-hand-{finish}" for finish in ("brushed-gold", "black", "chrome")},
        finish_prices={"brushed-gold": 450, "black": 250, "chrome": None},
        card_note="٣ أنماط للرش · زر SmartTip",
        detail_photo=dict(file="smartactive-hand-spray-guide", size=(790, 988),
                          title="تفاصيل الرش وزر SmartTip",
                          caption="رسم يوضّح فتحات الرش من الأمام ومكان زرّ التبديل خلف المقبض.",
                          alt="رسم لسماعة الدش من الأمام والخلف يحدّد فتحات Rain وJet وActiveMassage ومكان زر SmartTip",
                          wide=True),
        description="سماعة دش يدوية بثلاثة أنماط للرش، مع زر SmartTip مدمج خلف المقبض.",
        spray_title="ثلاثة أنماط للرش",
        sprays={
            "Rain": "رذاذ مطري لطيف.",
            "Jet": "رشّ مركّز.",
            "ActiveMassage": "تدفّق مائي للتدليك.",
        },
        control_note="زر SmartTip خلف المقبض يتيح التبديل بين أنماط الرش بلمسة إصبع واحدة.",
        search="جروهي غروهي كروهي سماعة شاور دوش دش يدوي rain shower hand shower smart tip massage",
    ),
    GROHE_WALL_OUTLET: dict(
        name="GROHE Wall Outlet", label="مخرج دفن", cover="grohe-wall-outlet",
        category="grohe", colors=("Brushed Gold", "Black", "Chrome"),
        finish_photos={finish: f"groheoutlet-{finish}" for finish in ("brushed-gold", "black", "chrome")},
        finish_prices={"brushed-gold": 150, "black": 125, "chrome": None},
        description="مخرج مياه جداري بتصميم انسيابي، يصل قلب الدفن داخل الجدار بخرطوم سماعة الدش أو الشطّاف.",
        search="كروهي غروهي جروهي مخرج دفن وصلة جداري سماعة دش مسكة شطاف hose connection wall outlet",
    ),
    GROHE_BATH_SPOUT: dict(
        name="GROHE Bath Spout", label="مصب بانيو كروهي", cover="grohe-bath-spout",
        category="grohe", colors=("Chrome", "Brushed Gold", "Black"),
        finish_photos={finish: f"grohebathspout-{finish}" for finish in ("chrome", "brushed-gold", "black")},
        finish_prices={"chrome": 125, "brushed-gold": 175, "black": 150},
        description="مصبّ جداري لملء البانيو، بتصميم نحيف وقاعدة مربّعة.",
        search="كروهي غروهي جروهي مصب بانيو حوض استحمام جداري bath spout tub filler",
    ),
    SMARTBOX: dict(name="Rapido SmartBox", label="قلب دفن سمارت", cover="smartbox",
                   category="grohe", price=130, photo="family-smartbox",
                   outlet_support="يدعم مخرجًا واحدًا أو مخرجين أو ثلاثة مخارج",
                   description="قلب الدفن الداخلي لنظام Grohtherm SmartControl. يُباع بشكل منفصل عن واجهة التحكّم.",
                   search="كروهي غروهي جروهي سواد داخلي قلب دفن رابيدو grohe smart box"),
    GROHE_SHOWER_BODY: dict(name="GROHE Concealed Shower Mixer Body", label="قلب خلاط شاور دفن",
                            cover="grohe-shower-body", category="grohe", price=100, photo="family-grohe-shower-body", outlets=2,
                            description="الجسم الداخلي لخلاط الشاور الدفن، يُركّب داخل الحائط.",
                            search="قلب خلاط شاور دش دفن سواد كروهي غروهي جروهي concealed shower mixer rough-in"),
    GROHE_TOILET_BODY: dict(name="GROHE Concealed Toilet Mixer Body", label="قلب خلاط تواليت دفن",
                            cover="grohe-toilet-body", category="grohe", price=75, photo="family-grohe-toilet-body", outlets=1,
                            description="الجسم الداخلي لخلاط التواليت الدفن، يُركّب داخل الحائط.",
                            search="قلب خلاط تواليت دفن سواد كروهي غروهي جروهي concealed toilet mixer rough-in"),
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
               grohe_photos={"feet": "grohe-cistern-feet-navy", "frame": "grohe-cistern-frame-navy"},
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
    if "finish_photos" in spec:
        return {
            finish: (spec["finish_prices"][finish], f'/assets/{spec["finish_photos"][finish]}.webp', label)
            for finish, label in finish_options(spec).items()
        }, {}
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
    registry = {
        "name": f'{spec["name"]} · {spec["label"]}', "price": min(v[0] for v in variants.values() if v[0] is not None),
        "category": category, "favoriteKey": "saad-saved-" + slug, "defaultColor": next(iter(variants)),
        "prices": {k: v[0] for k, v in variants.items()}, "images": {k: v[1] for k, v in variants.items()},
        "colorLabels": {k: v[2] for k, v in variants.items()}, "legacyOptions": legacy,
        "search": " ".join((spec["name"], spec["label"], spec["description"], spec["search"], words,
                            " ".join(s.replace("-", " ") for s in legacy),
                            "اسود أسود دهبي ذهبي كروم مربع كيوب" if slug != TANK else "")).lower(),
    }
    if "grohe_photos" in spec:
        registry["collectionImages"] = {
            "grohe": {key: f'/assets/{spec["grohe_photos"][key.split("|")[0]]}.webp' for key in variants}
        }
    return registry


def outlet_label(spec):
    count = spec.get("outlets")
    if count is None:
        return escape(spec.get("outlet_support", ""))
    return f'{SMARTCONTROL_OUTLETS[str(count)]} · <bdi lang="en" dir="ltr">{count} Outlet</bdi>'


def family_card(slug, registry, origin_label, *, cover_photo=None, collection=None):
    spec = FAMILIES[slug]
    amounts = {amount for amount in registry["prices"].values() if amount is not None}
    price = f'<bdi dir="ltr">${min(amounts)}</bdi>'
    if len(amounts) > 1:
        price = "من " + price
    name = f'<bdi lang="en" dir="ltr">{spec["name"]}</bdi>'
    heading = (f'<strong>{name}</strong><span>{spec["label"]}</span>' if registry["category"] == "grohe"
               else f'<strong>{spec["label"]}</strong>{name}')
    note = outlet_label(spec) or escape(spec.get("card_note", ""))
    link = f"/{slug}/" + ("?" + urlencode({"from": collection}) if collection else "")
    return (f'<a class="concealed-accessory-card family-listing" href="{link}">'
            f'<span class="concealed-accessory-photo"><img loading="lazy" decoding="async" src="{cover_photo or cover(slug)}" alt=""></span>'
            f'<span class="concealed-accessory-copy">{heading}'
            + (f'<small>{escape(origin_label)}</small>' if origin_label else '')
            + (f'<span class="family-card-forms">{note}</span>' if note else "")
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
    elif "finish_photos" in spec:
        controls = options(slug, "finish", "التشطيب", finish_options(spec))
    spray_details = ""
    if "sprays" in spec:
        spray_items = "".join(
            f'<li><strong><bdi lang="en" dir="ltr">{escape(mode)}</bdi></strong> · {escape(description)}</li>'
            for mode, description in spec["sprays"].items()
        )
        spray_title = escape(spec.get("spray_title", "نمطان للرش"))
        spray_details = (f'<p><strong>{spray_title}</strong></p><ul>{spray_items}</ul>'
                         f'<p>{escape(spec["control_note"])}</p>')
    detail_photo = ""
    if photo := spec.get("detail_photo"):
        width, height = photo["size"]
        modifier = " family-detail-photo--wide" if photo.get("wide") else ""
        detail_photo = f"""
        <figure class="family-detail-photo{modifier}">
          <img src="/assets/{photo['file']}.webp" alt="{escape(photo['alt'])}"
               width="{width}" height="{height}" loading="lazy" decoding="async">
          <figcaption><strong>{escape(photo['title'])}</strong>
            <span>{escape(photo['caption'])}</span>
          </figcaption>
        </figure>"""
    origin = f'<span class="velato-origin">{escape(origin_label)}</span>' if origin_label else ''
    outlets = outlet_label(spec)
    outlet_note = f'<p><strong>{outlets}</strong></p>' if outlets else ""
    price_title = "سعر القطعة"
    body_card = ""
    if body_slug := spec.get("required_body"):
        body = FAMILIES[body_slug]
        price_title = "سعر البياض · الجزء الظاهر"
        body_card = f"""
    <aside class="family-required-body" aria-label="قلب الدفن المطلوب">
      <h2>قلب الدفن ضروري للتركيب</h2>
      <p>سعر البياض للجزء الظاهر فقط. قلب الدفن يُباع بشكل منفصل.</p>
      <div class="family-required-item">
        <a href="/{body_slug}/"><img src="{cover(body_slug)}" alt="قلب دفن خلاط المغسلة"
            width="790" height="988" loading="lazy" decoding="async"></a>
        <div>
          <a class="family-required-name" href="/{body_slug}/"><bdi lang="en" dir="ltr">{body['name']}</bdi></a>
          <button class="action" data-add-required-body="{body_slug}" type="button">
            <span data-required-body-add>أضف قلب الدفن · <bdi dir="ltr">${body['price']:,}</bdi></span>
            <span data-required-body-added hidden>✓ موجود بالسلة</span>
          </button>
          <div class="family-required-cart">
            <span data-required-body-status role="status"></span>
            <a href="#cart" data-required-body-cart hidden>عرض السلة</a>
          </div>
        </div>
      </div>
    </aside>"""
    return f"""
<section id="{slug}" class="vanity-detail family-product" data-nosnippet hidden>
  <div class="product-image"><img src="{registry["images"][selected]}" alt="{spec["label"]} · {label}" width="790" height="988" loading="lazy" decoding="async">
    <button class="circle" data-save type="button" aria-label="إضافة إلى المفضّلة" aria-pressed="false">♡</button></div>
  <div class="product-info"><p class="category">{spec["label"]}</p><h1><bdi dir="ltr">{spec["name"]}</bdi></h1>
    {origin}<p>{spec["description"]}</p>{outlet_note}{spray_details}{detail_photo}{controls}
    <div class="family-summary" aria-live="polite" aria-atomic="true"><div><strong>{price_title}</strong><span data-family-summary>{label}</span></div>
    <bdi dir="ltr" data-unit-price>${price:,}</bdi></div>{body_card}
    <div class="qty"><span>الكمية</span><button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button><output data-quantity>1</output><button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button></div>
    <button class="action" data-add-cart type="button">أضف إلى السلة — ${price:,}</button>{related}{warranty}
  </div></section>"""


def product_data(slug, registry, origin, country):
    spec = FAMILIES[slug]
    url = f"{origin}/{slug}/"
    axes = ["form", "package" if slug == TANK else "finish", "diverter" if slug == SPOUT else "size"]
    if "finish_photos" in spec:
        axes = ["finish"]
    offers = [{"@type": "Offer", "name": registry["colorLabels"][key], "price": amount, "priceCurrency": "USD",
               "url": url if "photo" in spec else url + "?" + urlencode(dict(zip(axes, key.split("|"))))}
              for key, amount in registry["prices"].items() if amount is not None]
    images = dict.fromkeys([cover(slug), *registry["images"].values()])
    if "detail_photo" in spec:
        images[f'/assets/{spec["detail_photo"]["file"]}.webp'] = None
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
