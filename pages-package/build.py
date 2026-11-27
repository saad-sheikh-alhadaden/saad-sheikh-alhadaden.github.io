"""Verify storefront source files and build the Cloudflare Pages output."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from shutil import copyfile
from zipfile import ZipFile

from optimize import optimize_pages

package = Path(__file__).resolve().parent
repo = package.parent
output = repo / "dist"
manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
archive_data = b"".join(part.read_bytes() for part in sorted(package.glob("part-*")))

with ZipFile(BytesIO(archive_data)) as archive:
    for target, (expected, original) in manifest.items():
        content = (repo / original).read_bytes() if original else archive.read(target)
        if sha256(content).hexdigest() != expected:
            raise ValueError(f"Unexpected file contents: {target}")
        if target == "index.html":
            charset = b'<meta charset="utf-8">\n'
            verification = (
                b'<meta name="google-site-verification" '
                b'content="7H2pFR3kpQIW2QJj-Eic9pC4HMB8ZkY5-nV9VYSVG2w">\n'
            )
            body_start = b'<div class="app">\n'
            if content.count(charset) != 1 or content.count(body_start) != 1:
                raise ValueError("The homepage layout changed.")
            content = content.replace(charset, b"<head>\n" + charset + verification, 1)
            content = content.replace(body_start, b"</head>\n<body>\n" + body_start, 1)
            content += b"</body>\n</html>\n"
        path = output / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

optimize_pages(output)
for name in ("404.html", "_headers"):
    copyfile(package / name, output / name)

print(f"Prepared {len(manifest)} verified storefront files and the custom 404 page.")
