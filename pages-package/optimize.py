"""Optimize the generated storefront while preserving its navigation markup."""

from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import re


STYLE = re.compile(rb"<style>(.*?)</style>", re.DOTALL)


class DeferredImages(HTMLParser):
    """Find image attributes to insert without reserializing the document."""

    def __init__(self, document):
        super().__init__(convert_charrefs=False)
        self.document = document
        self.line_offsets = [0] + [line.end() for line in re.finditer("\n", document)]
        self.sections = []
        self.edits = []

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == "section":
            self.sections.append("hidden" in values)
        if tag != "img":
            return
        additions = ""
        loading = values.get("loading")
        if "loading" not in values and "fetchpriority" not in values and any(self.sections):
            additions += ' loading="lazy"'
            loading = "lazy"
        if loading == "lazy" and "decoding" not in values:
            additions += ' decoding="async"'
        if additions:
            line, column = self.getpos()
            raw_tag = self.get_starttag_text()
            offset = self.line_offsets[line - 1] + column + len(raw_tag)
            self.edits.append((offset - (2 if raw_tag.endswith("/>") else 1), additions))

    def handle_endtag(self, tag):
        if tag == "section" and self.sections:
            self.sections.pop()

    def optimized(self):
        self.feed(self.document)
        self.close()
        parts = []
        start = 0
        for offset, additions in self.edits:
            parts.extend((self.document[start:offset], additions))
            start = offset
        parts.append(self.document[start:])
        return "".join(parts)


def optimize_pages(output):
    pages = sorted(output.rglob("index.html"))
    shared_styles = Counter()
    for page in pages:
        shared_styles.update(set(STYLE.findall(page.read_bytes())))

    # Styles with page-relative resources must retain their original URL base.
    stylesheets = {}
    for css, occurrences in shared_styles.items():
        if occurrences < 2 or len(css) < 4096 or re.search(rb"url\s*\(|@import", css, re.I):
            continue
        filename = f"storefront-shared-{sha256(css).hexdigest()[:16]}.css"
        (output / "assets" / filename).write_bytes(css)
        stylesheets[css] = f'<link rel="stylesheet" href="/assets/{filename}">'.encode()

    for page in pages:
        original = page.read_bytes()
        updated = STYLE.sub(lambda match: stylesheets.get(match[1], match[0]), original)
        updated = DeferredImages(updated.decode("utf-8")).optimized().encode("utf-8")
        page.write_bytes(updated)
