"""Place the Milano signature next to prices on products labelled Made in Italy."""
import re


SECTION = re.compile(r'<section\b[^>]*>.*?</section>', re.S | re.I)
ITALIAN_ORIGIN = re.compile(
    r'<(?P<tag>p|span|small)\b[^>]*>\s*(?:made\s+in\s+italy|'
    r'ص[\u064b-\u0652]*ن[\u064b-\u0652]*ع\s+في\s+[إا]يطاليا)\s*</(?P=tag)>', re.I)
PRICE = re.compile(r'<p\b[^>]*\bclass="price-tag"[^>]*>.*?</p>', re.S)


def add_to_products(markup, logo_url):
    logo = (f'<img class="milano-brand" src="{logo_url}" alt="Milano Italy" '
            'lang="en" width="679" height="328">')

    def brand_section(match):
        section = match[0]
        info = section.find('class="product-info"')
        if info < 0 or 'class="milano-brand"' in section:
            return section
        origin = ITALIAN_ORIGIN.search(section, info)
        if not origin:
            return section
        price = PRICE.search(section, info)
        if not price:
            return section[:origin.end()] + logo + section[origin.end():]

        # Preserve the approved kitchen layout, with the mark between origin and price.
        if origin.end() <= price.start() and not section[origin.end():price.start()].strip():
            return section[:price.start()] + logo + section[price.start():]

        # Some templates print the origin immediately after the price. Keep the two
        # together, with the signature below the origin and clear of finish controls.
        if price.end() <= origin.start() and not section[price.end():origin.start()].strip():
            row = f'<div class="milano-price-row with-origin">{price[0]}{origin[0]}{logo}</div>'
            return section[:price.start()] + row + section[origin.end():]
        row = f'<div class="milano-price-row">{price[0]}{logo}</div>'
        return section[:price.start()] + row + section[price.end():]

    return SECTION.sub(brand_section, markup)
