"""Apply the granite catalog layout to archived storefront pages."""
from pathlib import Path
import re

ORDER = (
    "granite-black-gray-60x50",
    "granite-white-gray",
    "granite-silver-gray",
    "granite-white-gold-gray",
    "granite-travertino",
)
POSITION = {slug: index for index, slug in enumerate(ORDER)}
CARD = re.compile(r'<a class="hero mixer-product" href="/([^"/]+)/">.*?</a>', re.S)
GRID = re.compile(r'(<div class="cabinet-gallery" data-granite-cards>)((?:\s*' + CARD.pattern.replace('([^"/]+)', '[^"/]+') + r')+)(\s*</div>)', re.S)


STYLE = """<style id="granite-card-style">
[data-granite-cards] > .hero.mixer-product {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #15120f;
  border-color: #70593c66;
}
[data-granite-cards] .mixer-product-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: stretch;
  gap: 6px;
  padding: 12px clamp(9px, 2.6vw, 16px) 13px;
  border-top: 1px solid #9d7d4c40;
  border-bottom: 0;
  direction: rtl;
  text-align: right;
}
[data-granite-cards] .mixer-product-copy strong {
  display: block;
  color: #f5eee2;
  font-size: clamp(14px, 3.7vw, 19px);
  font-weight: 650;
  line-height: 1.45;
  overflow-wrap: anywhere;
}
[data-granite-cards] .mixer-product-copy small {
  display: block;
  margin-top: auto;
  color: #bcb2a4;
  white-space: normal;
  font-size: clamp(11px, 2.85vw, 13px);
  font-weight: 400;
  line-height: 1.45;
}
[data-granite-cards] .mixer-product-copy > span {
  display: block;
  margin-top: 2px;
  padding-top: 7px;
  border-top: 1px solid #9d7d4c40;
  color: #e1bd80;
  font-size: clamp(13px, 3.3vw, 16px);
  font-weight: 650;
  line-height: 1.35;
  font-variant-numeric: tabular-nums;
  text-align: right;
  white-space: normal;
}

[data-granite-cards] .granite-card-sizes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
[data-granite-cards] .granite-card-sizes bdi {
  padding: 2px 5px;
  border: 1px solid #9d7d4c65;
  border-radius: 5px;
  white-space: nowrap;
}
[data-granite-basin] > .granite-size-picker {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px 12px;
  padding: 8px 10px;
  background: #15120f;
  color: #f5eee2;
  border-bottom: 1px solid #9d7d4c65;
  font-size: 13px;
}
.granite-size-picker .granite-size-options {
  display: flex;
  gap: 4px;
  padding: 3px;
  border: 1px solid #9d7d4c65;
  border-radius: 10px;
  background: #211c16;
}
.granite-size-options > button {
  min-height: 44px;
  padding: 4px 8px;
  border: 1px solid transparent;
  border-radius: 7px;
  background: #211c16;
  color: #f5eee2;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.granite-size-options > button[aria-pressed="true"] {
  background: #e1bd80;
  border-color: #e1bd80;
  color: #15120f;
}
.granite-size-options > button:focus-visible {
  outline: 2px solid #f5eee2;
  outline-offset: 1px;
}
</style>"""


DETAIL = re.compile(r'<section\b[^>]*\bdata-granite-basin\b[^>]*>.*?</section>', re.S)
SIZE_OPTIONS = re.compile(r'<p>اختر المقاس</p>\s*(<div class="options" aria-label="المقاس">.*?</div>)', re.S)
CARD_MEASUREMENTS = re.compile(r'<small><bdi lang="en" dir="ltr">([\d ×/]+) cm</bdi></small>')


def move_size_picker(match):
    section = match[0]
    options = SIZE_OPTIONS.search(section)
    if not options:
        return section
    buttons = options[1].replace('class="options"', 'class="granite-size-options" role="group"', 1)
    buttons = buttons.replace('class="option" ', '')
    picker = f'<div class="granite-size-picker"><strong>المقاس</strong>{buttons}</div>'
    section = section[:options.start()] + section[options.end():]
    return section.replace('<div class="product-image">', picker + '<div class="product-image">', 1)


def format_card_measurements(match):
    chips = "".join(f'<bdi>{size.strip()} سم</bdi>' for size in match[1].split("/"))
    return f'<small class="granite-card-sizes">{chips}</small>'


def order_cards(match):
    cards = list(CARD.finditer(match[2]))
    cards.sort(key=lambda card: POSITION.get(card[1], len(ORDER)))
    return match[1] + "".join(CARD_MEASUREMENTS.sub(format_card_measurements, card[0]) for card in cards) + match[3]


if __name__ == "__main__":
    for page in Path("storefront").rglob("index.html"):
        original = page.read_text(encoding="utf-8")
        if not GRID.search(original) and not DETAIL.search(original):
            continue
        updated = DETAIL.sub(move_size_picker, GRID.sub(order_cards, original))
        if 'id="granite-card-style"' not in updated:
            updated = updated.replace('<div class="app">', STYLE + '\n<div class="app">', 1)
        if updated != original:
            page.write_text(updated, encoding="utf-8")
