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
</style>"""


def order_cards(match):
    cards = list(CARD.finditer(match[2]))
    cards.sort(key=lambda card: POSITION.get(card[1], len(ORDER)))
    return match[1] + "".join(card[0] for card in cards) + match[3]


if __name__ == "__main__":
    for page in Path("storefront").rglob("index.html"):
        original = page.read_text(encoding="utf-8")
        if not GRID.search(original):
            continue
        updated = GRID.sub(order_cards, original)
        if 'id="granite-card-style"' not in updated:
            updated = updated.replace('<div class="app">', STYLE + '\n<div class="app">', 1)
        if updated != original:
            page.write_text(updated, encoding="utf-8")
