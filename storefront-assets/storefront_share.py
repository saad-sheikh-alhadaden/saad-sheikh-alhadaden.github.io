"""Add share controls to storefront pages after all routes have been generated."""
import hashlib
import json
import re
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path("storefront")
SOURCE = Path(__file__).parent

SHARE_BUTTON = '''<button class="share-pill" type="button" data-share-page aria-label="مشاركة المتجر" title="مشاركة المتجر">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M12 15V3m-4 4 4-4 4 4M7 10H5v11h14V10h-2"/>
  </svg>
  <span>شارك</span>
</button>'''

SHARE_DIALOG = '''<dialog class="share-dialog" data-share-dialog dir="rtl" aria-labelledby="share-dialog-title">
  <form method="dialog"><h2 id="share-dialog-title">مشاركة المتجر</h2><button type="submit">إغلاق</button></form>
  <div class="share-preview" data-share-preview>
    <img data-share-image alt="" width="64" height="74" hidden>
    <strong data-share-name></strong>
  </div>
  <div class="share-dialog-actions">
    <a data-share-whatsapp href="https://wa.me/" target="_blank" rel="noopener noreferrer">واتساب</a>
    <button type="button" data-share-copy>نسخ الرابط</button>
    <button type="button" data-share-native hidden>خيارات المشاركة</button>
  </div>
  <div data-share-manual hidden>
    <label for="store-share-link">الرابط</label>
    <input id="store-share-link" data-share-link dir="ltr" type="text" readonly>
  </div>
  <p data-share-status role="status"></p>
</dialog>'''

BACK_LINK = re.compile(r'<a class="circle" id="back"[^>]*>.*?</a>', re.S)


def publish_asset(root, source):
    data = source.read_bytes()
    version = hashlib.sha256(data).hexdigest()[:12]
    asset = f"assets/{source.stem}-{version}{source.suffix}"
    (root / asset).write_bytes(data)
    return "/" + asset


def add_sharing(root):
    pages = {}
    share_pages = {"home": {"path": "/", "title": "متجر شركة سعد شيخ الحدادين", "label": "مشاركة المتجر"}}
    for file in sorted(root.rglob("index.html")):
        markup = file.read_text()
        if not BACK_LINK.search(markup):
            continue
        pages[file] = markup
        screen = re.search(r'<html\b[^>]*\bdata-screen="([^"]+)"', markup)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', markup)
        title = re.search(r"<title>(.*?)</title>", markup, re.S)
        if screen and canonical and title:
            path = urlsplit(canonical[1]).path
            product = bool(re.search(r'"@type"\s*:\s*"Product"', markup))
            share_pages[screen[1]] = {
                "path": path, "title": unescape(title[1]),
                "label": "مشاركة المنتج" if product else "مشاركة المجموعة",
            }

    script = publish_asset(root, SOURCE / "storefront-share.js")
    stylesheet = publish_asset(root, SOURCE / "storefront-share.css")
    nav_script = publish_asset(root, SOURCE / "storefront-navigation.js")
    nav_style = publish_asset(root, SOURCE / "storefront-navigation.css")
    targets = escape(json.dumps(share_pages, ensure_ascii=False, separators=(",", ":")), quote=True)
    button = SHARE_BUTTON.replace("data-share-page ", f'data-share-page data-share-pages="{targets}" ')
    for file, markup in pages.items():
        markup = BACK_LINK.sub(lambda match: f'<div class="share-actions">{button}{match[0]}</div>', markup, count=1)
        markup = re.sub(r'<link rel="stylesheet"[^>]*>',
                        lambda match: match[0] + f'\n<link rel="stylesheet" href="{stylesheet}">\n<link rel="stylesheet" href="{nav_style}">', markup, count=1)
        content = SHARE_DIALOG + f'\n<script src="{script}" defer></script>\n<script src="{nav_script}" defer></script>\n'
        if "</body>" in markup:
            markup = markup.replace("</body>", content + "</body>", 1)
        else:
            markup += "\n" + content
        file.write_text(markup)


if __name__ == "__main__":
    add_sharing(ROOT)
