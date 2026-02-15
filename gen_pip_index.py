#!/usr/bin/env python3

import sys
import hashlib
import zipfile
from pathlib import Path
from collections import defaultdict
from packaging.utils import parse_wheel_filename

if len(sys.argv) != 4:
    print(
        "usage:\n"
        "  p4a_index_gen.py <wheel_root_dir> <release_base_url> <output_dir>\n"
        "\nexample:\n"
        "  p4a_index_gen.py wheels "
        "https://github.com/user/repo/releases/download/v1.2.0 docs"
    )
    sys.exit(1)

wheel_root = Path(sys.argv[1])
base_url = sys.argv[2].rstrip("/")
if base_url in ("", ".", "./"):
    base_url = None
out_root = Path(sys.argv[3])

if not wheel_root.is_dir():
    raise SystemExit("wheel_root_dir is not a directory")


def pkg_name_from_wheel(filename: str) -> str:
    """Extract normalized package name from wheel using packaging."""
    name, _, _, _ = parse_wheel_filename(filename)
    return name.lower().replace("_", "-")


def extract_wheel_metadata_bytes(whl_path: Path) -> bytes | None:
    """Return the METADATA bytes from a wheel, or None if not found."""
    try:
        with zipfile.ZipFile(whl_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".dist-info/METADATA"):
                    return zf.read(name)
    except Exception as e:
        raise SystemExit(f"Failed to read wheel metadata: {whl_path.name} because {e}") from e
    return None


def iter_wheels_with_progress(root: Path):
    wheels = sorted(root.glob("*.whl"))
    total = len(wheels)
    if total == 0:
        return []
    width = 30
    for i, whl in enumerate(wheels, 1):
        filled = int(width * i / total)
        bar = "#" * filled + "-" * (width - filled)
        print(f"\rCollecting wheels [{bar}] {i}/{total}", end="", flush=True)
        yield whl
    print()


# Collect wheels by package
packages = defaultdict(list)
for whl in iter_wheels_with_progress(wheel_root):
    try:
        pkg = pkg_name_from_wheel(whl.name)
    except Exception as e:
        raise SystemExit(f"Invalid wheel filename: {whl.name} because {e}") from e
    packages[pkg].append(whl.name)
# p4a root
p4a_root = out_root / "p4a"
p4a_root.mkdir(parents=True, exist_ok=True)

# Generate pip-compatible package indexes
for pkg, wheels in packages.items():
    pkg_dir = p4a_root / pkg
    pkg_dir.mkdir(parents=True, exist_ok=True)
    wheels.sort()
    index_path = pkg_dir / "index.html"
    with index_path.open("w", encoding="utf-8") as f:
        f.write("<!doctype html>\n<html><body>\n")
        for w in wheels:
            whl_path = wheel_root / w
            metadata_bytes = extract_wheel_metadata_bytes(whl_path)
            metadata_attr = ""
            if metadata_bytes is not None:
                metadata_path = whl_path.with_name(whl_path.name + ".metadata")
                metadata_path.write_bytes(metadata_bytes)
                metadata_hash = hashlib.sha256(metadata_bytes).hexdigest()
                metadata_attr = f' data-dist-info-metadata="sha256={metadata_hash}"'
            href = f"{base_url}/{w}" if base_url else w
            f.write(f'<a href="{href}"{metadata_attr}>{w}</a><br>\n')
        f.write("</body></html>\n")

# Generate human-friendly landing page at p4a/index.html
landing_path = p4a_root / "index.html"
with landing_path.open("w", encoding="utf-8") as f:
    f.write(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>p4a Python Package Index</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  color-scheme: dark;
  --bg: #0d1117;
  --fg: #c9d1d9;
  --muted: #8b949e;
  --accent: #58a6ff;
  --border: #30363d;
  --code-bg: #161b22;
}}
html, body {{ margin:0; background: var(--bg); color: var(--fg); font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
main {{ max-width:720px; margin:4rem auto; padding:0 1.25rem; }}
h1 {{ font-size:1.8rem; margin-bottom:0.25rem; }}
p {{ line-height:1.6; color: var(--muted); }}
hr {{ border:none; border-top:1px solid var(--border); margin:2rem 0; }}
code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; background: var(--code-bg); color: var(--fg); }}
pre {{ padding:1rem; border-radius:6px; overflow-x:auto; border:1px solid var(--border); }}
a {{ color: var(--accent); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
footer {{ margin-top:3rem; font-size:0.85rem; color: var(--muted); }}
</style>
</head>
<body>
<main>
<h1>p4a Python Package Index</h1>
<p>This is a <strong>PEP 503 “simple” Python package index</strong> for use with <code>pip</code>.</p>
<hr>

<p>To install a package from this index:</p>
<pre><code>pip install \\
  --disable-pip-version-check \\
  --platform=android_24_aarch64 \\
  --only-binary=:all: \\
  --extra-index-url https://anshdadwal.is-a.dev/p4a-wheels/p4a \\
  --target . &lt;package&gt;
</code></pre>

<p>Available packages:</p>
<ul>
"""
    )
    for pkg in sorted(packages):
        f.write(f'<li><a href="{pkg}/">{pkg}</a></li>\n')
    f.write(
        """</ul>
<footer>
<p>Static p4a index · GitHub Pages</p>
</footer>
</main>
</body>
</html>
"""
    )

print(f"p4a: updated indexes for {len(packages)} packages + landing page")
