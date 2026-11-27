"""Build the exact public storefront for Cloudflare Pages."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

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
            if not content.startswith(b'<!doctype html>') or content.count(charset) != 1:
                raise ValueError("The homepage header changed.")
            content = content.replace(charset, charset + verification, 1)
        path = output / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

print(f"Prepared {len(manifest)} verified storefront files.")
