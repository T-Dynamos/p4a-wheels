import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main(tag: str, wheel_dir: Path):
    if not wheel_dir.exists() or not wheel_dir.is_dir():
        raise SystemExit(f"Invalid directory: {wheel_dir}")

    wheels = {p.name for p in wheel_dir.glob("*.whl")}
    if not wheels:
        print("No .whl files found. Nothing to do.")
        return

    # Get existing assets
    existing = set(
        run(
            ["gh", "release", "view", tag, "--json", "assets", "--jq", ".assets[].name"]
        ).splitlines()
    )

    # Delete matching assets
    for name in wheels & existing:
        print(f"Deleting existing asset: {name}")
        run(["gh", "release", "delete-asset", tag, name, "-y"])

    # Upload all wheels
    print("Uploading wheels...")
    run(["gh", "release", "upload", tag, *map(str, wheel_dir.glob("*.whl"))])

    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python update_release_assets.py <tag> <wheel_dir>")

    main(sys.argv[1], Path(sys.argv[2]))
