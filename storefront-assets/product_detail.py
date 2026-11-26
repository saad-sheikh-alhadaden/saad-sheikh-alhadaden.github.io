"""Keep product descriptions below the price and make model identifiers legible."""
from functools import lru_cache
import re

from milano_brand import SECTION


INFO = re.compile(r'<div class="product-info"[^>]*>')
HEADING_AND_MODEL = re.compile(
    r'(<h1\b[^>]*>.*?</h1>)\s*'
    r'(?:<p class="product-model-name"(?![^>]*lang="ar")[^>]*>(.*?)</p>'
    r'|<p class="product-description"[^>]*>(<bdi\b[^>]*>[^<]*</bdi>)(?:\s*·\s*([^<]+))?</p>)',
    re.S,
)
DESCRIPTION = re.compile(r'<p class="(?:product-description|vanity-material)"[^>]*>.*?</p>', re.S)
LEGACY_DESCRIPTION = re.compile(r'<p>(?=[^<]*[\u0600-\u06ff])[^<]*[.؟!]\s*</p>', re.S)
PRICE = re.compile(
    r'<div class="milano-price-row(?: with-origin)?"[^>]*>.*?</div>'
    r'|<div class="(?:family-summary|diameter-summary)"[^>]*>'
    r'.*?<bdi\b[^>]*\bdata-unit-price[^>]*>.*?</bdi>\s*</div>'
    r'|<p class="price-tag"[^>]*>.*?</p>',
    re.S,
)
STYLE = """<style id="product-detail-layout">
.product-info .product-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: .35rem .9rem;
  margin-block-end: .6rem;
}
.product-info .product-title-row > h1 { margin: 0; }
.product-info .product-title-row > .product-model-name {
  margin: 0;
  margin-right: auto;
  max-inline-size: 100%;
  overflow-wrap: anywhere;
  text-align: left;
  font-size: clamp(1rem, 3.6vw, 1.2rem);
  font-weight: 700;
  color: #73531f;
}
.product-info h1 > .vessel-model-code {
  display: inline-block;
  margin-inline-start: .28em;
  color: #886125;
  font-size: .82em;
}
.product-info .product-summary { margin-block: .4rem .85rem; }
.product-info .product-summary > :first-child { margin-block-start: 0; }
.product-info .product-summary > :last-child { margin-block-end: 0; }
[data-java-gallery] .java-gallery-model .product-title-row > .product-model-name { color: #e1c296; }
</style>"""


@lru_cache(maxsize=1024)
def format_section(section):
    info = INFO.search(section)
    if not info:
        return section
    prefix, body = section[:info.end()], section[info.end():]
    if 'class="product-title-row"' not in body:
        vessel = '-decorative-vessel-basin"' in section[:section.index(">")]

        def format_heading(match):
            heading, model, alias, notes = match.groups()
            identifier = model or alias
            if vessel:
                code = re.sub(r'<[^>]+>', '', identifier)
                return heading[:-5] + f' <bdi class="vessel-model-code" lang="en" dir="ltr">{code}</bdi></h1>'
            summary = f'<p class="product-description">{notes}</p>' if notes else ""
            return (f'<div class="product-title-row">{heading}'
                    f'<p class="product-model-name" dir="auto">{identifier}</p></div>{summary}')

        body = HEADING_AND_MODEL.sub(format_heading, body, count=1)
    price = PRICE.search(body)
    if not price or 'class="product-summary"' in body:
        return prefix + body

    descriptions = list(DESCRIPTION.finditer(body))
    legacy = LEGACY_DESCRIPTION.search(body, 0, price.start())
    if legacy:
        descriptions.append(legacy)
    if not descriptions:
        return prefix + body

    summary = '<div class="product-summary">' + ''.join(
        match[0] for match in sorted(descriptions, key=lambda match: match.start())
    ) + '</div>'
    before, after = [], []
    boundary = price.end()
    for match in sorted(descriptions, key=lambda match: match.start(), reverse=True):
        target = before if match.start() < boundary else after
        target.append(match)
    left, right = body[:boundary], body[boundary:]
    for match in before:
        left = left[:match.start()] + left[match.end():]
    for match in after:
        right = right[:match.start() - boundary] + right[match.end() - boundary:]
    return prefix + left + "\n" + summary + right


def publish(markup):
    updated = SECTION.sub(lambda match: format_section(match[0]), markup)
    if updated != markup and 'id="product-detail-layout"' not in updated:
        updated = updated.replace('<div class="app">', STYLE + '\n<div class="app">', 1)
    return updated
