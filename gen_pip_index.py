import sys
from pathlib import Path
from collections import defaultdict

from packaging.utils import parse_wheel_filename


if len(sys.argv) != 4:
    print(
        "usage:\n"
        "  p4a_index_gen.py <wheel_root> <release_base_url> <output_dir>\n"
        "\nexample:\n"
        "  p4a_index_gen.py wheels "
        "https://github.com/user/repo/releases/download/v1.2.0 docs"
    )
    sys.exit(1)

wheel_root = Path(sys.argv[1])
base_url = sys.argv[2].rstrip("/")
out_root = Path(sys.argv[3])

if not wheel_root.is_dir():
    raise SystemExit("wheel_root is not a directory")


def pkg_name_from_wheel(filename: str) -> str:
    # packaging does PEP 427 + normalization correctly
    name, _, _, _ = parse_wheel_filename(filename)
    return name.lower().replace("_", "-")


packages = defaultdict(list)

for whl in wheel_root.rglob("*.whl"):
    try:
        pkg = pkg_name_from_wheel(whl.name)
    except Exception as e:
        raise SystemExit(f"invalid wheel filename: {whl.name}") from e

    packages[pkg].append(whl.name)


p4a_root = out_root / "p4a"
p4a_root.mkdir(parents=True, exist_ok=True)

for pkg, wheels in packages.items():
    pkg_dir = p4a_root / pkg
    pkg_dir.mkdir(parents=True, exist_ok=True)  # safe if exists

    wheels.sort()

    index_path = pkg_dir / "index.html"
    with index_path.open("w", encoding="utf-8") as f:
        f.write("<!doctype html>\n<html><body>\n")
        for w in wheels:
            f.write(f'<a href="{base_url}/{w}">{w}</a><br>\n')
        f.write("</body></html>\n")

print(f"p4a: updated indexes for {len(packages)} packages")
