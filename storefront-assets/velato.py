"""Publish concealed fixtures using the storefront's shared cart."""
import json
import re
import shutil
import xml.etree.ElementTree as ET
from hashlib import sha256
from html import escape
from pathlib import Path

FINISH = "Brushed Rose Gold"
WARRANTY = '<p class="velato-warranty"><strong>الكفالة الذهبية</strong><span>كفالة 5 سنوات. تبديل فوري خلال أول سنتين، وصيانة خلال السنوات الثلاث التالية.</span></p>'
SET = "velato-concealed-set"
SET_GROUP = "concealed-sets"
MOUNTED_GROUP = "floor-ceiling-wall-mixers"
MOUNTED_TITLE = "خلاطات من الأرض والسقف والحائط"
MOUNTED_SUBTITLE = "Floor, Ceiling & Wall Mixers"
ST_0047 = "st-0047"
ST_0047_NAME = "S.T 9965"
ST_W101 = "st-w101"
ST_W101_NAME = "S.T 27B"
ST_W102 = "st-w102"
ST_W102_NAME = "S.T 82366"
ST_56560 = "st-56560"
ST_56560_NAME = "S.T 56560"
ST_56570 = "st-56570"
ST_56570_NAME = "S.T 56570"
ST_111000 = "st-111000"
ST_111000_NAME = "S.T 118088"
GROHE_CISTERN = "grohe-concealed-cistern"
GROHE_NAME = "GROHE"
GROHE_PHOTO = "/assets/grohe-cistern.webp"
GROHE_FEET_CISTERN = "grohe-concealed-cistern-with-feet"
GROHE_FLUSH_PLATE = "grohe-flush-plate"
GROHE_FLUSH_PLATE_FINISHES = {
    "مخفية قابلة للتبليط": ("tileable", 155),
    "Brushed Gold": ("brushed-gold", 100),
    "Rose Gold": ("rose-gold", 100),
    "Gray": ("gray", 100),
    "Gold": ("gold", 65),
    "Black": ("black", 65),
    "White": ("white", 50),
    "Chrome": ("chrome", 25),
}
GROHE_CONFIGURATIONS = {
    GROHE_CISTERN: ("خزان دفن مع شاسيه", GROHE_PHOTO, {"مع كبسة الدفن": 140, "بدون كبسة الدفن": 115}),
    GROHE_FEET_CISTERN: ("خزان دفن مع قواعد تثبيت", "/assets/grohe-cistern-with-feet.webp",
                        {"مع كبسة الدفن": 125, "بدون كبسة الدفن": 100}),
}
ACCESSORIES_GROUP = "concealed-accessory"
HEAD_SHOWER = "head-shower"
FERRARI_HEAD_SHOWER = "head-shower-ferrari"
A3_HEAD_SHOWER = "head-shower-a3"
C7_HEAD_SHOWER = "head-shower-c7"
C7_HEAD_DESCRIPTION = "رأس دش جداري بتصميم أسطواني عصري."
RAIN_SHOWER_ROUND = "rain-shower-round"
RAIN_SHOWER_ROUND_DESCRIPTION = "طقم دش يدوي يضمّ سماعة الدش، وخرطومًا مرنًا، وقاعدة تثبيت جدارية للسماعة."
ACCESSORY_COVERS = {
    A3_HEAD_SHOWER: "/assets/a3head-cover.webp",
    RAIN_SHOWER_ROUND: "/assets/rainround-cover.webp",
}
A3_HEAD_DESCRIPTION = "رأس دش سقفي بتصميم انسيابي مستوحى من قطرة الماء."
FERRARI_HEAD_DESCRIPTION = "رأس دش علوي دائري بتصميم عصري."
HEAD_SHOWER_DESCRIPTION = "رأس دش علوي بتصميم عصري، يجمع بين تدفّق الشلال ورذاذ المطر."
ST_122DG = "st-122dg"
ST_122DG_NAME = "S.T 122FG"
ST_307840 = "st-307840"
ST_307840_NAME = "S.T 307840"
ST_GR = "st-gr"
ST_GR_BASIN = f"{ST_GR}-concealed-basin"
ST_GR_TOILET = f"{ST_GR}-concealed-toilet"
SET_PRICES = {SET: 1975, f"{ST_GR}-concealed-set": 1000}
ST_GU = "st-gu-concealed-toilet"
ST_GU_PRICES = {"Brushed Gold": 300, "Gray": 300, "Black": 275, "Chrome": 250}
ST_BL_BASIN = "st-bl-concealed-basin"
ST_R_BASIN = "st-r-concealed-basin"
COORDINATED_GROUPS = (
    (ST_W101, ST_W102),
    ("cube-2-outlet-concealed-shower", "cube-3-outlet-concealed-shower", ST_GR_BASIN, ST_GU),
    ("sphere-2-outlet-concealed-shower", ST_R_BASIN, ST_GR_TOILET),
)
GERMAN_SHOWERS = {
    "cube-3-outlet-concealed-shower": (
        "Cube 3 Outlet", "شاور دفن بثلاثة مخارج", "cube-shower",
        {"Brushed Gold": 600, "Chrome": 350, "Black": 450, "Gold": 500, "Gray": 600},
        "طقم شاور دفن يضمّ رأس دش مطري مربّع بقياس 30 × 30 سم، ودشّاً يدوياً، ومصبّاً سفلياً.",
    ),
    "cube-2-outlet-concealed-shower": (
        "Cube 2 Outlet", "شاور دفن بمخرجين", "cube-2-shower",
        {"Gray": 500, "Chrome": 300, "Black": 400, "Brushed Gold": 500},
        "طقم شاور دفن يضمّ رأس دش مطري مربّع بقياس 30 × 30 سم ودشّاً يدوياً.",
    ),
    "sphere-2-outlet-concealed-shower": (
        "Sphere 2 Outlet", "شاور دفن بمخرجين", "sphere-2-shower",
        {"Brushed Gold": 500, "Gray": 500, "Chrome": 300, "Black": 400},
        "طقم شاور دفن بمخرجين، يضمّ رأس دش مطري دائري بقياس 30 × 30 سم ودشّاً يدوياً.",
    ),
}
CASCATA = "cascata-oro"
CASCATA_CHROME = f"{CASCATA}-chrome"
CASCATA_TOILET = f"{CASCATA}-concealed-toilet"
PARTS = {
    "shower": ("شاور دفن", 1200, 7),
    "basin": ("خلاط مغسلة دفن", 475, 5),
    "toilet": ("خلاط تواليت دفن", 300, 2),
}


# Add a product here only when its price is confirmed to include both parts.
PRICE_INCLUDES_BOTH_PARTS = {
    "cascata-oro-chrome-concealed-basin",
    "cascata-oro-chrome-concealed-shower",
    "cascata-oro-concealed-basin",
    "cascata-oro-concealed-shower",
    "cascata-oro-concealed-toilet",
    "cube-2-outlet-concealed-shower",
    "cube-3-outlet-concealed-shower",
    "eclipse-flow-concealed-basin",
    "eclipse-flow-concealed-shower",
    "lunaire-digital-blus-concealed-basin",
    "lunaire-digital-blus-concealed-shower",
    "octagon-concealed-basin",
    "octagon-concealed-shower",
    "sphere-2-outlet-concealed-shower",
    "st-bl-concealed-basin",
    "st-gr-concealed-basin",
    "st-gr-concealed-shower",
    "st-gr-concealed-toilet",
    "st-gu-concealed-toilet",
    "st-r-concealed-basin",
    "velato-concealed-basin",
    "velato-concealed-shower",
    "velato-concealed-toilet",
}


def publish(root, origin, store, meta, preview, schema_pattern, json_script):
    models = {}
    for kind, (label, price, count) in PARTS.items():
        prefix = f"velato-{kind}-brushed-rose-gold"
        photos = [f"/assets/{prefix}-{i}.webp" for i in range(1, count + 1)]
        models[f"velato-concealed-{kind}"] = (label, price, photos, f"concealed-{kind}-mixer")
    for kind, price in {"shower": 700, "basin": 300}.items():
        photos = [f"/assets/octagon-{kind}-{i}.webp" for i in range(1, 5)]
        models[f"octagon-concealed-{kind}"] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    color_galleries = {}
    for slug, (label, photo, prices) in GROHE_CONFIGURATIONS.items():
        models[slug] = (label, next(iter(prices.values())), [photo], ACCESSORIES_GROUP)
        color_galleries[slug] = {package: [photo] for package in prices}
    plate_galleries = {
        finish: [f"/assets/grohe-flush-plate-{suffix}.webp"]
        for finish, (suffix, _) in GROHE_FLUSH_PLATE_FINISHES.items()
    }
    color_galleries[GROHE_FLUSH_PLATE] = plate_galleries
    models[GROHE_FLUSH_PLATE] = ("كبسة لخزان دفن", next(iter(GROHE_FLUSH_PLATE_FINISHES.values()))[1],
                                [gallery[0] for gallery in plate_galleries.values()], ACCESSORIES_GROUP)

    models[HEAD_SHOWER] = ("رأس دش علوي", 200, ["/assets/headshower-gold.webp"], ACCESSORIES_GROUP)

    ferrari_head_galleries = {finish: [f"/assets/ferrarihead-{finish.lower()}.webp"]
                             for finish in ("Black", "Chrome")}
    color_galleries[FERRARI_HEAD_SHOWER] = ferrari_head_galleries
    models[FERRARI_HEAD_SHOWER] = ("رأس دش علوي", 250,
                                 [photos[0] for photos in ferrari_head_galleries.values()], ACCESSORIES_GROUP)

    a3_head_galleries = {
        "Brushed Gold": ["/assets/a3head-brushed-gold.webp"],
        "Black": ["/assets/a3head-black.webp"],
        "Chrome": ["/assets/a3head-chrome.webp"],
    }
    color_galleries[A3_HEAD_SHOWER] = a3_head_galleries
    models[A3_HEAD_SHOWER] = ("رأس دش سقفي", 200,
                            [photos[0] for photos in a3_head_galleries.values()], ACCESSORIES_GROUP)

    models[C7_HEAD_SHOWER] = ("رأس دش جداري", 150, ["/assets/c7head-black.webp"], ACCESSORIES_GROUP)

    rain_round_galleries = {finish: [f"/assets/rainround-{finish.lower()}.webp"]
                            for finish in ("Black", "Gold", "Chrome")}
    color_galleries[RAIN_SHOWER_ROUND] = rain_round_galleries
    models[RAIN_SHOWER_ROUND] = ("سماعة دش", 50,
                                [photos[0] for photos in rain_round_galleries.values()], ACCESSORIES_GROUP)

    floor_galleries = {
        color: [f"/assets/st0047-{color.lower().replace(' ', '-')}-{index:02}.webp"
                for index in range(1, count + 1)]
        for color, count in ((FINISH, 10), ("Black", 10), ("White", 10), ("Brushed Gold", 10), ("Gray", 9))
    }
    color_galleries[ST_0047] = floor_galleries
    models[ST_0047] = ("خلاط بانيو أرضي", 950,
                       [photo for photos in floor_galleries.values() for photo in photos], MOUNTED_GROUP)
    basin_photos = [f"/assets/stw101-black-portrait-{index:02}.webp" for index in range(1, 5)]
    models[ST_W101] = ("خلاط مغسلة أرضي", 550, basin_photos, MOUNTED_GROUP)
    tub_photos = [f"/assets/stw102-black-{index:02}.webp" for index in range(1, 6)]
    models[ST_W102] = ("خلاط بانيو أرضي", 650, tub_photos, MOUNTED_GROUP)
    light_gray_photos = [f"/assets/st56560-light-gray-{index:02}.webp" for index in range(1, 5)]
    models[ST_56560] = ("خلاط مغسلة أرضي", 375, light_gray_photos, MOUNTED_GROUP)
    brushed_gold_photos = [f"/assets/st56570-brushed-gold-{index:02}.webp" for index in range(1, 8)]
    models[ST_56570] = ("خلاط مغسلة أرضي", 650, brushed_gold_photos, MOUNTED_GROUP)
    ceiling_galleries = {
        color: [f"/assets/st111000-{color.lower()}-{index:02}.webp" for index in range(1, 8)]
        for color in ("Black", "Chrome")
    }
    color_galleries[ST_111000] = ceiling_galleries
    models[ST_111000] = ("خلاط مغسلة بتثبيت سقفي وتحكّم جداري", 500,
                        [photo for gallery in ceiling_galleries.values() for photo in gallery], MOUNTED_GROUP)
    wall_galleries = {
        color: [f"/assets/st307840-{color.lower()}-{index:02}.webp" for index in range(1, 6)]
        for color in ("Gray", "Black", "Chrome", "White")
    }
    color_galleries[ST_307840] = wall_galleries
    models[ST_307840] = ("خلاط مغسلة جداري بفوّهة انسيابية ممتدّة نحو الحوض", 500,
                        [photo for gallery in wall_galleries.values() for photo in gallery], MOUNTED_GROUP)
    st122dg_galleries = {
        color: [f"/assets/st122dg-{color.lower().replace(' ', '-')}-{index:02}.webp"
                for index in range(1, 4)]
        for color in ("Brushed Gold", "White")
    }
    color_galleries[ST_122DG] = st122dg_galleries
    models[ST_122DG] = (PARTS["basin"][0], 350,
                       [photo for gallery in st122dg_galleries.values() for photo in gallery],
                       "concealed-basin-mixer")
    for kind, price, count in [("shower", 700, 5), ("basin", 350, 2)]:
        slug = f"eclipse-flow-concealed-{kind}"
        galleries = {
            color: [f"/assets/eclipse-{kind}-{color.lower()}-{i}.webp" for i in range(1, count + 1)]
            for color in ("Black", "Chrome")
        }
        color_galleries[slug] = galleries
        photos = [photo for gallery in galleries.values() for photo in gallery]
        models[slug] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    for kind, price, count, first_color in [
        ("shower", 950, 1, "Rose Gold"),
        ("basin", 500, 4, "Gray"),
    ]:
        slug = f"lunaire-digital-blus-concealed-{kind}"
        colors = [first_color, *[color for color in ("Chrome", "Rose Gold", "Gray", "White")
                                 if color != first_color]]
        galleries = {
            color: [f"/assets/lunaire-{kind}-{color.lower().replace(' ', '-')}-{i}.webp"
                    for i in range(1, count + 1)]
            for color in colors
        }
        color_galleries[slug] = galleries
        photos = [photo for gallery in galleries.values() for photo in gallery]
        models[slug] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    for kind, price, count in [("shower", 450, 5), ("basin", 225, 3), ("toilet", 200, 4)]:
        photos = [f"/assets/cascata-{kind}-{i}.webp" for i in range(1, count + 1)]
        models[f"{CASCATA}-concealed-{kind}"] = (PARTS[kind][0], price, photos, f"concealed-{kind}-mixer")
    chrome_photos = {
        kind: [f"/assets/cascata-chrome-{kind}-{i}.webp" for i in range(1, count + 1)]
        for kind, count in (("shower", 5), ("basin", 3), ("toilet", 4))
    }
    for kind, price in (("shower", 350), ("basin", 325)):
        models[f"{CASCATA_CHROME}-concealed-{kind}"] = (
            PARTS[kind][0], price, chrome_photos[kind], f"concealed-{kind}-mixer"
        )
    label, price, gold_photos, group = models[CASCATA_TOILET]
    color_galleries[CASCATA_TOILET] = {"Gold": gold_photos, "Chrome": chrome_photos["toilet"]}
    models[CASCATA_TOILET] = (label, price, gold_photos + chrome_photos["toilet"], group)
    models[f"{ST_GR}-concealed-shower"] = (
        PARTS["shower"][0], 500, [f"/assets/stgr-shower-{i}.webp" for i in range(1, 6)],
        "concealed-shower-mixer",
    )
    st_gr_prices = {"Gray": 300, "Brushed Gold": 300, "Black": 275, "Chrome": 250}
    st_gr_galleries = {
        "Gray": ["/assets/stgr-basin-gray-water.webp"],
        "Brushed Gold": ["/assets/stgr-basin-brushed-gold-water.webp"],
        "Black": ["/assets/stgr-basin-black-front.webp", "/assets/stgr-basin-black-water.webp"],
        "Chrome": ["/assets/stgr-basin-chrome-front.webp", "/assets/stgr-basin-chrome-water.webp"],
    }
    color_galleries[ST_GR_BASIN] = st_gr_galleries
    models[ST_GR_BASIN] = (PARTS["basin"][0], st_gr_prices["Gray"],
                          [photo for images in st_gr_galleries.values() for photo in images],
                          "concealed-basin-mixer")
    st_gu_galleries = {
        color: [f"/assets/stgu-toilet-{color.lower().replace(' ', '-')}.webp"]
        for color in ST_GU_PRICES
    }
    color_galleries[ST_GU] = st_gu_galleries
    models[ST_GU] = (PARTS["toilet"][0], next(iter(ST_GU_PRICES.values())),
                     [images[0] for images in st_gu_galleries.values()], "concealed-toilet-mixer")
    st_gr_toilet_galleries = {
        color: [f"/assets/stgr-toilet-{color.lower().replace(' ', '-')}.webp"]
        for color in st_gr_prices
    }
    color_galleries[ST_GR_TOILET] = st_gr_toilet_galleries
    models[ST_GR_TOILET] = (PARTS["toilet"][0], st_gr_prices["Gray"],
                            [images[0] for images in st_gr_toilet_galleries.values()],
                            "concealed-toilet-mixer")
    variant_prices = {ST_GR_BASIN: st_gr_prices, ST_GR_TOILET: st_gr_prices, ST_GU: ST_GU_PRICES}
    variant_prices.update({slug: prices for slug, (_, _, prices) in GROHE_CONFIGURATIONS.items()})
    variant_prices[FERRARI_HEAD_SHOWER] = {finish: models[FERRARI_HEAD_SHOWER][1] for finish in ferrari_head_galleries}
    variant_prices[A3_HEAD_SHOWER] = {finish: models[A3_HEAD_SHOWER][1] for finish in a3_head_galleries}
    variant_prices[RAIN_SHOWER_ROUND] = {finish: models[RAIN_SHOWER_ROUND][1] for finish in rain_round_galleries}
    variant_prices[GROHE_FLUSH_PLATE] = {
        finish: price for finish, (_, price) in GROHE_FLUSH_PLATE_FINISHES.items()
    }
    for slug, folder, count, finishes in (
        (ST_BL_BASIN, "stbl", 3, ("Black", "Gray", "Brushed Gold")),
        (ST_R_BASIN, "str", 5, ("Black", "Gray", "Gold", "Rose Gold", "Chrome")),
    ):
        galleries = {
            color: [f"/assets/{folder}-basin-{color.lower().replace(' ', '-')}-{i}.webp"
                    for i in range(1, count + 1)]
            for color in finishes
        }
        color_galleries[slug] = galleries
        photos = [photo for gallery in galleries.values() for photo in gallery]
        models[slug] = (PARTS["basin"][0], 300, photos, "concealed-basin-mixer")
    for slug, (_, label, photo_prefix, prices, _) in GERMAN_SHOWERS.items():
        variant_prices[slug] = prices
        galleries = {
            color: [f"/assets/{photo_prefix}-{color.lower().replace(' ', '-')}.webp"]
            for color in prices
        }
        color_galleries[slug] = galleries
        models[slug] = (label, next(iter(prices.values())), [images[0] for images in galleries.values()],
                        "concealed-shower-mixer")
    cover_manifest = json.loads(Path(__file__).with_name("cinematic").joinpath("covers.json").read_text())
    cover_paths = {f"/assets/{original}": f"/assets/{replacement['file']}"
                   for original, replacement in cover_manifest.items()}

    def cover_photos(photos):
        return [cover_paths.get(photo, photo) for photo in photos]

    for slug, (label, price, photos, group) in models.items():
        models[slug] = (label, price, cover_photos(photos), group)
    for galleries in color_galleries.values():
        for color, photos in galleries.items():
            galleries[color] = cover_photos(photos)
    chrome_photos = {kind: cover_photos(photos) for kind, photos in chrome_photos.items()}

    sets = {}
    for prefix in ("velato", "octagon", "eclipse-flow", "lunaire-digital-blus", CASCATA, ST_GR):
        slug = f"{prefix}-concealed-set"
        kinds = PARTS if prefix in ("velato", CASCATA, ST_GR) else ("shower", "basin")
        parts = [f"{prefix}-concealed-{kind}" for kind in kinds]
        sets[slug] = parts
        if parts[0] in color_galleries:
            galleries = {
                color: [color_galleries[part][color][0] for part in parts]
                for color in color_galleries[parts[0]]
                if all(color in color_galleries[part] for part in parts)
            }
            color_galleries[slug] = galleries
            photos = [photo for gallery in galleries.values() for photo in gallery]
        else:
            photos = [models[part][2][0] for part in parts]
        price = SET_PRICES.get(slug, sum(models[part][1] for part in parts))
        label = "طقم دفن كامل" if len(parts) == 3 else "طقم شاور ومغسلة دفن"
        models[slug] = (label, price, photos, SET_GROUP)
    chrome_set = f"{CASCATA_CHROME}-concealed-set"
    chrome_parts = [f"{CASCATA_CHROME}-concealed-shower", f"{CASCATA_CHROME}-concealed-basin", CASCATA_TOILET]
    sets[chrome_set] = chrome_parts
    models[chrome_set] = ("طقم دفن كامل", sum(models[part][1] for part in chrome_parts),
                          [chrome_photos[kind][0] for kind in PARTS], SET_GROUP)
    part_sets = {part: slug for slug, parts in sets.items() for part in parts if part != CASCATA_TOILET}
    photo_sizes = {replacement["file"]: replacement["size"] for replacement in cover_manifest.values()}
    photo_sizes["headshower-gold.webp"] = (790, 988)
    photo_sizes["c7head-black.webp"] = (790, 988)
    for photos in (*ferrari_head_galleries.values(), *a3_head_galleries.values(), *rain_round_galleries.values()):
        photo_sizes[Path(photos[0]).name] = (790, 988)
    for folder in ("velato", "eclipse", "lunaire", "cascata", "stgr", "stbl", "str", "cube", "sphere", "stgu", "st0047", "stw101", "stw102", "st56560", "st56570", "st111000", "st307840", "st122dg"):
        photo_sizes.update(json.loads(Path(__file__).with_name(folder).joinpath("sizes.json").read_text()))
    all_photos = dict.fromkeys(photo for model in models.values() for photo in model[2])
    for photo in (*all_photos, *ACCESSORY_COVERS.values()):
        filename = Path(photo).name
        source = Path(__file__).with_name(filename.split("-", 1)[0])
        shutil.copyfile(source / filename, root / photo.lstrip("/"))
    labels = {"encastre": "خلاطات الدفن", SET_GROUP: "أطقم الدفن الكاملة"}
    labels.update({group: label for slug, (label, price, photos, group) in models.items() if slug not in sets})
    labels[ACCESSORIES_GROUP] = "إكسسوارات الدفن"
    labels[MOUNTED_GROUP] = MOUNTED_TITLE
    headings = {
        "encastre": "Encastre",
        SET_GROUP: "Concealed Sets",
        "concealed-shower-mixer": "Concealed Shower Mixer",
        "concealed-basin-mixer": "Concealed Basin Mixer",
        "concealed-toilet-mixer": "Concealed Toilet Mixer",
        "concealed-accessory": "Concealed Accessories",
    }

    encastre_links = {
        "concealed-shower-mixer": "خلاط شاور دفن",
        "concealed-basin-mixer": "خلاط مغسلة دفن",
        "concealed-toilet-mixer": "خلاط تواليت دفن",
        "concealed-accessory": "إكسسوارات الدفن",
    }

    def bilingual_collection_link(match):
        group = match["group"]
        return (f'<a class="encastre-category-link" href="{match["href"]}">'
                f'<span class="encastre-category-name"><span lang="ar">{encastre_links[group]}</span>'
                f'<bdi lang="en" dir="ltr">{headings[group]}</bdi></span></a>')

    def collection_heading(group):
        label = labels.get(group, "إكسسوارات الدفن")
        return (f'<header class="cabinet-heading"><h1><small>{label}</small>'
                f'<bdi lang="en" dir="ltr">{headings[group]}</bdi></h1></header>')

    def picture(photo, alt):
        return f'<img src="{photo}" alt="{escape(alt)}" loading="lazy" decoding="async">'

    def identity(slug):
        if slug == HEAD_SHOWER:
            return "Head Shower 2X", "Gold"
        if slug == FERRARI_HEAD_SHOWER:
            return "Head Shower Ferrari", " / ".join(ferrari_head_galleries)
        if slug == A3_HEAD_SHOWER:
            return "Head Shower A3", " / ".join(a3_head_galleries)
        if slug == C7_HEAD_SHOWER:
            return "Head Shower C7", "Black"
        if slug == RAIN_SHOWER_ROUND:
            return "Rain Shower Round", " / ".join(rain_round_galleries)
        if slug == GROHE_FLUSH_PLATE:
            return GROHE_NAME, " / ".join(GROHE_FLUSH_PLATE_FINISHES)
        if slug in GROHE_CONFIGURATIONS:
            return GROHE_NAME, "مع كبسة الدفن أو بدونها"
        if slug == ST_122DG:
            return ST_122DG_NAME, " / ".join(color_galleries[slug])
        if slug == ST_307840:
            return ST_307840_NAME, " / ".join(color_galleries[slug])
        if slug == ST_111000:
            return ST_111000_NAME, " / ".join(color_galleries[slug])
        if slug == ST_56570:
            return ST_56570_NAME, "Brushed Gold"
        if slug == ST_56560:
            return ST_56560_NAME, "Light Gray"
        if slug == ST_W101:
            return ST_W101_NAME, "Black"
        if slug == ST_W102:
            return ST_W102_NAME, "Black"
        if slug == ST_0047:
            return ST_0047_NAME, " / ".join(color_galleries[slug])
        if slug == ST_GU:
            return "S.T GU", " / ".join(ST_GU_PRICES)
        if slug in GERMAN_SHOWERS:
            name, _, _, prices, _ = GERMAN_SHOWERS[slug]
            return name, " / ".join(prices)
        if slug in (ST_BL_BASIN, ST_R_BASIN):
            name = "S.T M2YH" if slug == ST_BL_BASIN else "S.T 10088"
            return name, " / ".join(color_galleries[slug])
        if slug == f"{ST_GR}-concealed-shower":
            return "S.T Y5279 Smart", "Gray"
        if slug == ST_GR_BASIN:
            return "S.T 20019", " / ".join(color_galleries[slug])
        if slug.startswith(ST_GR + "-"):
            return "S.T Gr", " / ".join(color_galleries.get(slug, ("Gray",)))
        if slug == CASCATA_TOILET:
            return "S.T 80036", "Gold / Chrome"
        if slug.startswith(CASCATA_CHROME + "-"):
            name = {
                f"{CASCATA_CHROME}-concealed-shower": "S.T 723702",
                f"{CASCATA_CHROME}-concealed-basin": "S.T 222",
            }.get(slug, "Cascata Oro")
            return name, "Chrome"
        if slug.startswith(CASCATA + "-"):
            name = {
                f"{CASCATA}-concealed-shower": "S.T G369369",
                f"{CASCATA}-concealed-basin": "S.T AZ-003",
            }.get(slug, "Cascata Oro")
            return name, "Gold"
        if slug.startswith("lunaire-"):
            name = "S.T 202 Smart" if slug == "lunaire-digital-blus-concealed-shower" else "Lunaire Digital blus"
            return name, "Chrome / Rose Gold / Gray / White"
        if slug.startswith("eclipse-"):
            name = {
                "eclipse-flow-concealed-shower": "S.T M6245",
                "eclipse-flow-concealed-basin": "S.T 108003",
            }.get(slug, "Eclipse Flow")
            return name, "Black / Chrome"
        if slug.startswith("octagon-"):
            name = {
                "octagon-concealed-shower": "S.T 6766",
                "octagon-concealed-basin": "S.T 2132",
            }.get(slug, "OCTAGON")
            return name, "Chrome"
        name = {"velato-concealed-shower": "S.T 30008", "velato-concealed-basin": "S.T 30000RU"}.get(slug, "Velato")
        return name, FINISH

    def country_of_origin(slug):
        if slug == RAIN_SHOWER_ROUND:
            return None
        if slug in (HEAD_SHOWER, FERRARI_HEAD_SHOWER, A3_HEAD_SHOWER, C7_HEAD_SHOWER):
            return "Italy", "إيطاليا"
        if slug in GROHE_CONFIGURATIONS or slug in (ST_GU, ST_GR_BASIN, ST_GR_TOILET) or slug in GERMAN_SHOWERS:
            return "Germany", "ألمانيا"
        if slug in (ST_W102, GROHE_FLUSH_PLATE) or slug.startswith(ST_GR + "-"):
            return None
        if not slug.startswith(CASCATA + "-") or slug.startswith(CASCATA_CHROME + "-"):
            return ("Italy", "إيطاليا")
        return None

    def set_part_url(part, set_slug):
        color = "&amp;color=chrome" if part == CASCATA_TOILET and set_slug == chrome_set else ""
        return f"/{part}/?from=set{color}"

    def card(slug, set_slug):
        label, price, photos, group = models[slug]
        model_name, finish = identity(slug)
        photo = photos[0]
        if slug == CASCATA_TOILET:
            finish = "Chrome" if set_slug == chrome_set else "Gold"
            photo = color_galleries[slug][finish][0]
        return (f'<a class="velato-card" href="{set_part_url(slug, set_slug)}">{picture(photo, f"{model_name} · {label} · {finish}")}'
                f'<span><bdi>{model_name}</bdi><br>{label}<br><bdi>${price:,}</bdi></span></a>')

    def gallery_card(slug):
        label, price, photos, group = models[slug]
        model_name, finish = identity(slug)
        if group == ACCESSORIES_GROUP:
            country = country_of_origin(slug)
            origin_badge = f"<small>صُنع في {country[1]}</small>" if country else ""
            options = "".join(
                f'<span class="concealed-accessory-price"><span>{escape(package)}</span>'
                f'<bdi dir="ltr">${amount:,}</bdi></span>'
                for package, amount in variant_prices.get(slug, {finish: price}).items()
            )
            if slug in (FERRARI_HEAD_SHOWER, A3_HEAD_SHOWER, RAIN_SHOWER_ROUND):
                options = (f'<span class="concealed-accessory-price"><bdi>{finish}</bdi>'
                           f'<bdi dir="ltr">${price:,}</bdi></span>')
            if slug == GROHE_FLUSH_PLATE:
                prices = variant_prices[slug].values()
                options = (f'<span class="concealed-accessory-price"><span>٨ خيارات</span>'
                           f'<bdi dir="ltr">${min(prices)}–${max(prices)}</bdi></span>')
            cover = ACCESSORY_COVERS.get(slug, photos[0])
            return (f'<a class="concealed-accessory-card" href="/{slug}/">'
                    f'<span class="concealed-accessory-photo">{picture(cover, "")}</span>'
                    f'<span class="concealed-accessory-copy"><strong>{escape(label)} <bdi>{model_name}</bdi></strong>'
                    f'{origin_badge}<span class="concealed-accessory-prices">{options}</span>'
                    '<span class="concealed-accessory-detail">تفاصيل المنتج</span></span></a>')
        kind_label = f'<small class="mixer-product-kind">{escape(label)}</small>' if group == MOUNTED_GROUP else ""
        price_text = f"${price:,}"
        if slug in variant_prices:
            prices = variant_prices[slug].values()
            price_text = f"${min(prices):,}–${max(prices):,}"
        return (f'<a class="hero mixer-product" href="/{slug}/">'
                f'{picture(photos[0], f"{label} {model_name} · {finish}")}'
                f'<div class="mixer-product-copy"><strong><bdi lang="en" dir="ltr">{model_name}</bdi></strong>'
                f'{kind_label}'
                f'<small><bdi lang="en" dir="ltr">{finish}</bdi></small>'
                f'<span dir="ltr">{price_text}</span></div></a>')

    grids = {
        group: '<div class="cabinet-gallery">' + "".join(
            gallery_card(slug) for slug, model in reversed(models.items()) if model[3] == group
        ) + '</div>'
        for group in labels if group not in ("encastre", ACCESSORIES_GROUP)
    }

    pinned_accessories = (GROHE_FLUSH_PLATE, GROHE_FEET_CISTERN, GROHE_CISTERN)
    accessory_order = [
        *pinned_accessories,
        *(slug for slug, model in models.items()
          if model[3] == ACCESSORIES_GROUP and slug not in pinned_accessories),
    ]
    grids[ACCESSORIES_GROUP] = (
        '<div class="concealed-accessory-list">'
        + "".join(gallery_card(slug) for slug in accessory_order)
        + '</div>'
    )

    hero = (f'<a class="velato-feature" href="/{SET_GROUP}/"><span>أطقم الدفن الكاملة'
            '<br><bdi lang="en">Concealed Sets</bdi><small>استعرض الأطقم</small></span>'
            '<div class="velato-strip">' + "".join(
                picture(models[slug][2][0], models[slug][0]) for slug in sets[SET]
            ) + '</div></a>')
    mounted_card = (
        f'<a class="velato-feature" href="/{MOUNTED_GROUP}/"><span>{MOUNTED_TITLE}'
        f'<br><bdi lang="en" dir="ltr">{escape(MOUNTED_SUBTITLE)}</bdi></span>'
        '<div class="velato-strip mounting-types" aria-hidden="true">'
        '<span>الأرض</span><span>السقف</span><span>الحائط</span></div></a>'
    )
    mounted_panel = (
        f'<section class="panel concealed-gallery" id="{MOUNTED_GROUP}" data-nosnippet hidden>'
        f'<header class="cabinet-heading"><h1><small>{MOUNTED_TITLE}</small>'
        f'<bdi lang="en" dir="ltr">{escape(MOUNTED_SUBTITLE)}</bdi></h1></header>'
        f'{grids[MOUNTED_GROUP]}</section>'
    )
    styles = """<style>
.velato-feature,.velato-card{display:block;color:#f6ebdc;background:#201c19;border:1px solid #9c7656;border-radius:14px;overflow:hidden;text-decoration:none}
.velato-feature{margin:1rem 0}.velato-feature>span,.velato-card>span{display:block;padding:.75rem 1rem}
.encastre-category-link .encastre-category-name{display:grid;gap:.16rem;min-width:0;line-height:1.35;text-align:start}
.encastre-category-name>span{font-weight:600;color:#f6ebdc}
.encastre-category-name>bdi{font-size:.875rem;color:#d5c4b0;text-align:right}
#concealed-accessory .concealed-accessory-list{display:grid;gap:1rem;padding:1rem 0}
.concealed-accessory-card{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,3fr);align-items:center;gap:.75rem;padding:.65rem;border:1px solid #5e4c3a;border-radius:14px;background:#201c19;color:inherit;text-decoration:none}
.concealed-accessory-photo{display:block;border-radius:9px;overflow:hidden;background:#181818}
.concealed-accessory-photo img{display:block;width:100%;height:auto;aspect-ratio:4/5;object-fit:contain}
.concealed-accessory-copy{display:grid;gap:.4rem;min-width:0;line-height:1.4}
.concealed-accessory-copy strong{font-size:1rem}
.concealed-accessory-copy small{color:#d5c4b0}
.concealed-accessory-prices{display:grid;gap:.3rem;margin-top:.2rem;padding-top:.55rem;border-top:1px solid #4f4033}
.concealed-accessory-price{display:flex;justify-content:space-between;align-items:baseline;gap:.35rem;font-size:.875rem}
.concealed-accessory-price>bdi,.concealed-accessory-detail{color:#e4b58d}
.concealed-accessory-detail{font-size:.875rem;margin-top:.2rem}
#grohe-concealed-cistern .velato-gallery,#grohe-concealed-cistern-with-feet .velato-gallery,#grohe-flush-plate .velato-gallery{display:none}
.velato-feature small{display:block;margin-top:.35rem;color:#e4b58d}
.velato-strip,.velato-parts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.45rem}
.mounting-types{gap:0;border-top:1px solid #4f4033}
.mounting-types span{text-align:center;padding:.65rem .25rem;color:#e4b58d}
.mounting-types span+span{border-inline-start:1px solid #4f4033}
#floor-ceiling-wall-mixers .mixer-product-copy .mixer-product-kind{grid-column:1/-1;color:inherit}
.velato-parts-pair{grid-template-columns:repeat(2,minmax(0,1fr))}
.velato-strip img,.velato-card img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover}
.velato-card{max-width:22rem;margin:.6rem 0 1rem}.velato-parts .velato-card>span{padding:.5rem;font-size:.8rem}
.velato-gallery{display:flex;gap:.45rem;overflow-x:auto;padding:.5rem 0}
.velato-gallery button{flex:0 0 4rem;background:transparent;border:1px solid transparent;border-radius:6px;padding:2px}
.velato-gallery button[aria-pressed=true]{border-color:#be9166}.velato-gallery img{display:block;width:100%;border-radius:4px}
.velato-gallery button[hidden]{display:none}
.velato-set-thumbnails{gap:.55rem;align-items:stretch}
.velato-set-thumbnails button{flex-basis:clamp(4.5rem,26%,6.5rem);min-width:0;padding:3px;
display:flex;flex-direction:column;border-color:#d8c9b6;border-radius:8px}
.velato-set-thumbnails button[aria-pressed=true]{border-color:#aa8055;background:#f7efe2}
.velato-set-thumbnails button:focus-visible{outline:2px solid #81591f;outline-offset:-2px}
.velato-set-thumbnails picture{display:block;width:100%}
.velato-set-thumbnails img{aspect-ratio:4/5;object-fit:cover}
.velato-set-thumbnails .velato-thumb-caption{width:100%;padding:.3rem .1rem .15rem;color:#5b462c;
font-family:inherit;font-size:.72rem;font-weight:600;line-height:1.45;text-align:center}
.product-info .velato-origin{display:inline-block;margin:.15rem 0 .7rem;padding:.25rem .65rem;
border:1px solid #aa8a5f;border-radius:100px;color:#5b462c;font-size:.76rem;letter-spacing:.025em}
.product-info .price-tag:has(+ .encastre-price-note){margin-bottom:.25rem!important}
.product-info .encastre-price-note{display:block;margin:0 0 .85rem;color:#685740;font-size:.875rem;line-height:1.5}
.product-info .velato-warranty{display:grid;gap:.2rem;margin:1rem 0;padding:.65rem .85rem;
border-inline-start:2px solid #a67a3d;background:#ebe3d4;color:#35291b;font-size:.86rem}
.velato-warranty strong{color:#684a25}
.product-info a.velato-link:not([hidden]){display:flex;align-items:center;justify-content:space-between;
gap:1rem;min-height:48px;margin:.7rem 0;padding:.55rem .85rem;border:1px solid #aa8a5f;
border-radius:10px;background:#f7f0e3;color:#392b1b;text-decoration:none;font-weight:650}
.velato-link:focus-visible{outline:2px solid #81591f;outline-offset:3px}
</style>"""
    details = []
    registry_additions = []
    search_links = ""
    saved_links = ""
    for slug, (label, price, photos, group) in models.items():
        model_name, finish = identity(slug)
        arabic_name = {"OCTAGON": "أوكتاغون", "Velato": "فيلاتو", "Eclipse Flow": "إكليبس فلو",
                       "Cascata Oro": "كاسكاتا أورو",
                       "S.T Gr": "اس تي جي آر st gr",
                       "S.T GU": "اس تي جي يو st gu",
                       "S.T 10088": "اس تي 10088 st10088",
                       "S.T M2YH": "اس تي إم 2 واي إتش stm2yh",
                       "S.T 20019": "اس تي 20019 st20019",
                       "S.T 222": "اس تي 222 st222",
                       "S.T AZ-003": "اس تي اي زد 003 staz003",
                       "S.T 108003": "اس تي 108003 st108003",
                       "S.T 2132": "اس تي 2132 st2132",
                       "S.T 30000RU": "اس تي 30000 آر يو st30000ru",
                       "Cube 3 Outlet": "كيوب ٣ مخارج",
                       "Cube 2 Outlet": "كيوب مخرجين",
                       "Sphere 2 Outlet": "سفير مخرجين",
                       "S.T 80036": "اس تي 80036 st80036",
                       "S.T 30008": "اس تي 30008 st30008",
                       "S.T 6766": "اس تي 6766 st6766",
                       "S.T 202 Smart": "اس تي 202 سمارت st202",
                       "S.T 723702": "اس تي 723702 st723702",
                       "S.T G369369": "اس تي جي 369369 stg369369",
                       "S.T Y5279 Smart": "اس تي واي 5279 سمارت sty5279",
                       "S.T M6245": "اس تي إم 6245 stm6245",
                       "Rain Shower Round": "سماعة دش يدوي نربيش خرطوم قاعدة اسود ذهبي كروم",
                       "Head Shower C7": "راس دش جداري اسطواني سي 7 اسود",
                       "Head Shower A3": "راس دش سقفي ايه 3 ذهبي مصقول اسود كروم",
                       "Head Shower Ferrari": "راس دش علوي دائري فيراري اسود كروم",
                       "Head Shower 2X": "راس دش علوي شلال مطري ذهبي",
                       GROHE_NAME: "غروهي كروهي خزان دفن شاسيه كبسة المانيا ألمانيا",
                       ST_0047_NAME: "اس تي 9965 st9965",
                       ST_56560_NAME: "اس تي 56560 st56560 رمادي فاتح",
                       ST_56570_NAME: "اس تي 56570 st56570 ذهبي مصقول",
                       ST_122DG_NAME: "اس تي 122 إف جي st122fg ذهبي مصقول أبيض",
                       ST_307840_NAME: "اس تي 307840 st307840 خلاط حائط رمادي أسود كروم أبيض",
                       ST_111000_NAME: "اس تي 118088 st118088 خلاط مغسلة من السقف أسود كروم",
                       ST_W101_NAME: "اس تي 27 بي st27b",
                       ST_W102_NAME: "اس تي 82366 st82366",
                       "Lunaire Digital blus": "لونير ديجيتال بلوس"}[model_name]
        name = f"{model_name} · {label}"
        galleries = color_galleries.get(slug, {finish: photos})
        default_color = next(iter(galleries))
        registry = {"name": name, "search": f"{model_name.lower()} {arabic_name} {label} دفن {finish.lower()} {price}",
                    "price": price, "images": {color: images[0] for color, images in galleries.items()},
                    "defaultColor": default_color,
                    "category": group, "favoriteKey": "saad-saved-" + slug}
        if slug in variant_prices:
            registry["prices"] = variant_prices[slug]
        registry_additions.append(f'  "{slug}": {json.dumps(registry, ensure_ascii=False)},')
        search_links += f'<a href="/{slug}/" data-search-product="{slug}" hidden>{name}</a>'
        saved_links += f'<a href="/{slug}/" data-saved="{slug}" hidden>{name}</a>'
        parts = sets.get(slug, [])
        gallery_class = " velato-set-thumbnails" if parts else ""
        gallery = ""
        for color, images in galleries.items():
            color_attr = f' data-gallery-color="{color}"' if slug in color_galleries else ""
            hidden = "" if color == default_color else " hidden"
            for index, photo in enumerate(images, 1):
                width, height = photo_sizes.get(Path(photo).name, (1050, 1300))
                alt = f"{name} · {color} · صورة {index}"
                caption = ""
                if parts:
                    kind = parts[index - 1].rsplit("-", 1)[1]
                    part_label = "خلاط شاور دفن" if kind == "shower" else PARTS[kind][0]
                    alt = f"{part_label} · {color}"
                    caption = f'<span class="velato-thumb-caption">{part_label}</span>'
                pressed = str(index == 1 and not hidden).lower()
                gallery += (f'<button type="button" data-gallery-src="{photo}" data-width="{width}" data-height="{height}"'
                            f'{color_attr}{hidden} aria-pressed="{pressed}" aria-label="{alt}">'
                            f'{picture(photo, "")}{caption}</button>')
        finishes = f"<p><bdi>{finish}</bdi></p>"
        if slug in color_galleries:
            options = "".join(
                f'<button class="option" type="button" data-color="{color}" '
                f'aria-pressed="{str(color == default_color).lower()}"><bdi>{color}</bdi>'
                + (f' <bdi dir="ltr">${variant_prices[slug][color]}</bdi>' if group == ACCESSORIES_GROUP else "") + "</button>"
                for color in galleries
            )
            option_label = "خيارات الخزان" if slug in GROHE_CONFIGURATIONS else "التشطيب"
            package_attr = " data-package-options" if slug in GROHE_CONFIGURATIONS or slug == GROHE_FLUSH_PLATE else ""
            finishes = f'<div class="options"{package_attr} role="group" aria-label="{option_label}">{options}</div>'
        if slug in sets:
            part_cards = "".join(card(part, slug) for part in parts)
            return_links = "".join(
                f'<a class="velato-link" href="{set_part_url(part, slug)}" data-set-return="{part.rsplit("-", 1)[1]}" hidden>'
                f'<span>الرجوع إلى {models[part][0]}</span><span aria-hidden="true">↶</span></a>'
                for part in parts
            )
            columns = " velato-parts-pair" if len(parts) == 2 else ""
            related = f'{return_links}<h2>مكوّنات الطقم</h2><div class="velato-parts{columns}">{part_cards}</div>'
        elif slug not in part_sets:
            related = ""
        else:
            set_slug = part_sets[slug]
            kind = slug.rsplit("-", 1)[1]
            set_name, _ = identity(set_slug)
            related = (f'<a class="velato-link" data-related-set href="/{set_slug}/?from={kind}">'
                       f'<span>شوف طقم {set_name} الكامل</span><span aria-hidden="true">‹</span></a>')
            if len(sets[set_slug]) == 2:
                other = next(part for part in sets[set_slug] if part != slug)
                other_name, _ = identity(other)
                related += (f'<a class="velato-link" href="/{other}/"><span>شوف {models[other][0]} {other_name}</span>'
                            '<span aria-hidden="true">‹</span></a>')
        coordinated = next((group for group in COORDINATED_GROUPS if slug in group), ())
        if coordinated:
            links = []
            for target in coordinated:
                if target != slug:
                    target_name, _ = identity(target)
                    links.append(f'<a class="velato-link" href="/{target}/">'
                                 f'<span>{models[target][0]} <bdi>{escape(target_name)}</bdi></span></a>')
            related += '<h2>قطع متناسقة</h2>' + "".join(links)
        order = "أضف الطقم للسلة" if slug in sets else "أضف إلى السلة"
        country = country_of_origin(slug)
        origin_badge = f'<span class="velato-origin" lang="en" dir="ltr">Made in {country[0]}</span>' if country else ""
        description_html = f'<p>{escape(GERMAN_SHOWERS[slug][4])}</p>' if slug in GERMAN_SHOWERS else ""
        if slug == HEAD_SHOWER:
            description_html = f"<p>{HEAD_SHOWER_DESCRIPTION}</p>"
        if slug == FERRARI_HEAD_SHOWER:
            description_html = f"<p>{FERRARI_HEAD_DESCRIPTION}</p>"
        if slug == A3_HEAD_SHOWER:
            description_html = f"<p>{A3_HEAD_DESCRIPTION}</p>"
        if slug == C7_HEAD_SHOWER:
            description_html = f"<p>{C7_HEAD_DESCRIPTION}</p>"
        if slug == RAIN_SHOWER_ROUND:
            description_html = f"<p>{RAIN_SHOWER_ROUND_DESCRIPTION}</p>"
        unit_price_attr = " data-unit-price" if slug in variant_prices else ""
        price_note = ""
        if slug in PRICE_INCLUDES_BOTH_PARTS:
            price_note = '<small class="encastre-price-note">السعر يشمل جسم الدفن الداخلي والقطع الخارجية الظاهرة</small>'
        details.append(f"""
<section id="{slug}" class="vanity-detail" data-nosnippet hidden>
  <div class="product-image">{picture(photos[0], name)}
    <button class="circle" data-save type="button" aria-label="إضافة {model_name} إلى المفضّلة" aria-pressed="false">♡</button>
  </div>
  <div class="product-info">
    <p class="category">{label}</p><h1><bdi>{model_name}</bdi></h1>
    {origin_badge}
    <div class="velato-gallery{gallery_class}" aria-label="صور المنتج">{gallery}</div>
    {finishes}
    {description_html}
    <p class="price-tag" dir="ltr"{unit_price_attr}>${price:,}</p>
    {price_note}
    <div class="qty"><span>الكمية</span><button type="button" data-quantity-change="-1" aria-label="تقليل الكمية">−</button><output data-quantity>1</output><button type="button" data-quantity-change="1" aria-label="زيادة الكمية">+</button></div>
    <button class="action" data-add-cart type="button">{order} — ${price:,}</button>
    {related}
    {WARRANTY}
  </div>
</section>""")

    home_path = root / "index.html"
    home = home_path.read_text()
    old_script = re.search(r'<script src="/(assets/storefront-[a-f0-9]+\.js)"', home)[1]
    js = (root / old_script).read_text()
    js = js.replace("const products = {", "const products = {\n" + "\n".join(registry_additions), 1)
    if registry_additions[0] not in js:
        raise ValueError("Missing storefront product registry")
    js = js.replace('const encastreScreens = new Set([', f'const encastreScreens = new Set(["{SET_GROUP}", "{MOUNTED_GROUP}", ', 1)
    quantity_listener = '  for (const button of screen.querySelectorAll("[data-quantity-change]")) {'
    if quantity_listener not in js:
        raise ValueError("Missing storefront quantity controls")
    js = js.replace(quantity_listener,
                    f'  if (id === "{CASCATA_TOILET}" && requestedFinish === "chrome") {{\n'
                    '    choices.find(choice => choice.dataset.color === "Chrome")?.click();\n'
                    '  }\n' + quantity_listener, 1)
    js = js.replace('addButton.textContent = `أضف إلى السلة — ${money(quantity * unitPrice(product, orderColor()))}`;',
                    'addButton.textContent = `${product.category === "concealed-sets" ? "أضف الطقم للسلة" : "أضف إلى السلة"} — ${money(quantity * unitPrice(product, orderColor()))}`;')
    new_script = f"assets/storefront-{sha256(js.encode()).hexdigest()[:12]}.js"
    (root / new_script).write_text(js)

    def add_inside(html, id_, content, after_heading=False):
        pattern = rf'(<(?:div|section)\b[^>]*\bid="{id_}"[^>]*>)'
        if after_heading:
            pattern += r'(.*?</h1>)'
        html, count = re.subn(pattern, lambda m: m[0] + content, html, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Missing storefront element {id_}")
        return html

    for path in root.rglob("index.html"):
        html = path.read_text()
        if old_script not in html:
            continue
        html = html.replace(old_script, new_script).replace("<title>", styles + "<title>", 1)
        html = add_inside(html, "result", search_links)
        html = add_inside(html, "saved", saved_links)
        html = html.replace(":is(#mixers,#showers)", ":is(#mixers,#showers,.concealed-gallery)")
        html = html.replace("#showers .cabinet-heading h1 small", ":is(#showers,.concealed-gallery) .cabinet-heading h1 small")
        html = html.replace("#showers .cabinet-gallery + .contact-card", ":is(#showers,.concealed-gallery) .cabinet-gallery + .contact-card")
        for group in headings:
            if group != SET_GROUP:
                pattern = rf'(<section class="panel" id="{group}"[^>]*>\s*)<h1>.*?</h1>'
                content = hero if group == "encastre" else grids.get(group, "")
                html, count = re.subn(pattern, lambda m: m[1].replace('class="panel"', 'class="panel concealed-gallery"')
                                      + collection_heading(group) + content, html, count=1, flags=re.S)
                if count != 1:
                    raise ValueError(f"Missing concealed collection heading: {group}")
            if group in grids and group != SET_GROUP:
                html = html.replace(f'href="#{group}"', f'href="/{group}/"')
        category_links = "|".join(map(re.escape, encastre_links))
        html = re.sub(
            rf'<a href="(?P<href>(?:/|#)(?P<group>{category_links})/?)">'
            r'<bdi dir="ltr">Concealed [^<]+</bdi></a>',
            bilingual_collection_link, html, flags=re.I,
        )
        catalog_link = r'(<a\b[^>]*\bhref="catalogs/saad-encastre\.pdf")'
        html, count = re.subn(catalog_link, lambda match: mounted_card + match[0], html, count=1)
        if count != 1:
            raise ValueError("Missing Encastre catalog link")
        html = html.replace('href="#encastre"', 'href="/encastre/"')
        html = html.replace("</main>", f'<section class="panel concealed-gallery" id="{SET_GROUP}" data-nosnippet hidden>'
                            f'{collection_heading(SET_GROUP)}{grids[SET_GROUP]}</section>'
                            + mounted_panel + "".join(details) + "</main>", 1)
        path.write_text(html)

    def landing(slug, title, description, photos, data):
        url = f"{origin}/{slug}/"
        full_title = f"{title} | {store}"
        page = home_path.read_text().replace('<html lang="ar" dir="rtl">',
            f'<html lang="ar" dir="rtl" data-screen="{slug}">', 1)
        page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8"><base href="/"> ', 1)
        page = page.replace('<section id="home">', '<section id="home" hidden>', 1)
        pattern = rf'(<section\b[^>]*\bid="{slug}"[^>]*?)(?: data-nosnippet)? hidden>'
        page, count = re.subn(pattern, r'\1>', page, count=1)
        if count != 1:
            raise ValueError(f"Missing page panel {slug}")
        page = re.sub(r"<title>.*?</title>", lambda _: f"<title>{escape(full_title)}</title>", page, count=1)
        page = page.replace(f'rel="canonical" href="{origin}/"', f'rel="canonical" href="{url}"', 1)
        for key, value in {"description": description, "og:title": full_title, "og:description": description,
                           "og:url": url, "twitter:title": full_title, "twitter:description": description}.items():
            page = meta(page, key, value)
        if photos:
            cover = ACCESSORY_COVERS.get(slug, photos[0])
            page = preview(page, title, origin + cover)
        data.update({"@context": "https://schema.org", "url": url, "name": title, "description": description})
        page = schema_pattern.sub(lambda _: json_script(data), page, count=1)
        target = root / slug
        target.mkdir(exist_ok=True)
        (target / "index.html").write_text(page)

    for slug, (label, price, photos, group) in models.items():
        model_name, finish = identity(slug)
        contents = " يشمل " + " و".join(models[part][0] for part in sets[slug]) + "." if slug in sets else ""
        origin_country = country_of_origin(slug)
        origin_text = f"، صنع في {origin_country[1]}" if origin_country else ""
        country = {"countryOfOrigin": {"@type": "Country", "name": origin_country[0]}} if origin_country else {}
        title = f"{label} {model_name}"
        if slug.startswith(CASCATA_CHROME + "-"):
            title += " · Chrome"
        description = f"{label} {model_name} بتشطيب {finish}{origin_text}. ${price:,}.{contents}"
        if slug == HEAD_SHOWER:
            description = f"{HEAD_SHOWER_DESCRIPTION} تشطيب ذهبي، صُنع في إيطاليا. ${price:,}."
        if slug == FERRARI_HEAD_SHOWER:
            description = f"{FERRARI_HEAD_DESCRIPTION} متوفر بالأسود والكروم، صُنع في إيطاليا. ${price:,}."
        offer = {"@type": "Offer", "price": price, "priceCurrency": "USD", "url": f"{origin}/{slug}/"}
        if slug in GERMAN_SHOWERS:
            description = f"{title}{origin_text}. {GERMAN_SHOWERS[slug][4]}"
        if slug == A3_HEAD_SHOWER:
            description = f"{A3_HEAD_DESCRIPTION} صُنع في إيطاليا. ${price:,}."
        if slug == C7_HEAD_SHOWER:
            description = f"{C7_HEAD_DESCRIPTION} باللون الأسود، صُنع في إيطاليا. ${price:,}."
        if slug == RAIN_SHOWER_ROUND:
            description = f"{RAIN_SHOWER_ROUND_DESCRIPTION} {finish}. ${price:,}."
        if slug in variant_prices:
            offer = [{"@type": "Offer", "name": color, "price": amount, "priceCurrency": "USD",
                      "url": f"{origin}/{slug}/"} for color, amount in variant_prices[slug].items()]
        landing(slug, title, description,
                photos, {"@type": "Product", "@id": f"{origin}/{slug}/#product", "sku": slug,
                         "color": finish, **country,
                         "image": [origin + photo for photo in photos],
                         "offers": offer})
    for slug, label in labels.items():
        children = (list(labels)[1:] if slug == "encastre" else
                    [model for model, data in models.items() if data[3] == slug])
        cover = next((data[2] for data in models.values() if data[3] == slug), models[SET][2])
        landing(slug, label, f"تصفّح {label} وشاهد الموديلات والتشطيبات والأسعار.", cover,
                {"@type": "CollectionPage", "mainEntity": {"@type": "ItemList", "itemListElement": [
                    {"@type": "ListItem", "position": index, "url": f"{origin}/{child}/"}
                    for index, child in enumerate(children, 1)]}})

    sitemap = root / "sitemap.xml"
    tree = ET.parse(sitemap)
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    node = tree.getroot()
    existing = {entry.text for entry in node.findall(f"{{{namespace}}}url/{{{namespace}}}loc")}
    for slug in (*labels, *models):
        url = f"{origin}/{slug}/"
        if url not in existing:
            ET.SubElement(ET.SubElement(node, f"{{{namespace}}}url"), f"{{{namespace}}}loc").text = url
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)
