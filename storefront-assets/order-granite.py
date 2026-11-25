"""Restore the established granite card order in archived storefront pages."""
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


def order_cards(match):
    cards = list(CARD.finditer(match[2]))
    cards.sort(key=lambda card: POSITION.get(card[1], len(ORDER)))
    return match[1] + "".join(card[0] for card in cards) + match[3]


if __name__ == "__main__":
    for page in Path("storefront").rglob("index.html"):
        original = page.read_text(encoding="utf-8")
        updated = GRID.sub(order_cards, original)
        if updated != original:
            page.write_text(updated, encoding="utf-8")
