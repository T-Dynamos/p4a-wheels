import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
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


def progress(prefix: str, index: int, total: int, suffix: str = "") -> None:
    bar_width = 30
    name_width = 40
    filled = int(bar_width * index / total) if total else bar_width
    bar = "#" * filled + "-" * (bar_width - filled)
    line = f"{prefix} [{bar}] {index}/{total}"
    if suffix:
        if len(suffix) > name_width:
            suffix = suffix[: name_width - 3] + "..."
        line = f"{line} {suffix:<{name_width}}"
    end = "\n" if index == total else "\r"
    # Clear to end of line so long names don't leave artifacts.
    sys.stdout.write("\r" + line + "\x1b[K" + end)
    sys.stdout.flush()


def run_json(cmd: list[str]):
    output = run(cmd)
    if not output:
        return None
    return json.loads(output)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_remote_asset(url: str) -> str:
    hasher = hashlib.sha256()
    with tempfile.NamedTemporaryFile() as tmp:
        with subprocess.Popen(
            ["gh", "api", "-H", "Accept: application/octet-stream", url],
            stdout=tmp,
            stderr=subprocess.PIPE,
            text=False,
        ) as proc:
            _, stderr = proc.communicate()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, proc.args, stderr)
        tmp.flush()
        tmp.seek(0)
        for chunk in iter(lambda: tmp.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main(tag: str, wheel_dir: Path, dry_run: bool):
    if not wheel_dir.exists() or not wheel_dir.is_dir():
        raise SystemExit(f"Invalid directory: {wheel_dir}")

    wheels = {p.name for p in wheel_dir.glob("*.whl")}
    metadata = {p.name for p in wheel_dir.glob("*.whl.metadata")}
    if not wheels and not metadata:
        print("No .whl or .whl.metadata files found. Nothing to do.")
        return

    repo = run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])

    # Get existing assets and URLs.
    release = run_json(
        ["gh", "api", f"repos/{repo}/releases/tags/{tag}"]
    )
    assets = release.get("assets", []) if release else []
    existing_assets = {
        asset["name"]: asset
        for asset in assets
        if asset["name"].endswith(".whl") or asset["name"].endswith(".whl.metadata")
    }

    # Delete all existing wheel assets: removes stale wheels and avoids upload conflicts.
    local_assets = {**{name: wheel_dir / name for name in wheels}, **{name: wheel_dir / name for name in metadata}}
    to_delete: list[str] = []
    to_upload: list[str] = []

    overlap = sorted(name for name in local_assets if name in existing_assets)
    if overlap:
        for i, name in enumerate(overlap, start=1):
            progress("Checking", i, len(overlap), name)
            local_hash = sha256_file(local_assets[name])
            remote_hash = sha256_remote_asset(existing_assets[name]["url"])
            if local_hash != remote_hash:
                to_delete.append(name)
                to_upload.append(name)
    missing_remote = sorted(name for name in local_assets if name not in existing_assets)
    to_upload.extend(missing_remote)

    stale_remote = sorted(name for name in existing_assets if name not in local_assets)
    to_delete.extend(stale_remote)

    if to_delete:
        for i, name in enumerate(sorted(set(to_delete)), start=1):
            progress("Deleting", i, len(set(to_delete)), name)
            if not dry_run:
                run(["gh", "release", "delete-asset", tag, name, "-y"])
    else:
        print("No existing wheel/metadata assets to delete.")

    # Upload all wheels
    to_upload = sorted(set(to_upload))
    if to_upload:
        for i, name in enumerate(to_upload, start=1):
            progress("Uploading", i, len(to_upload), name)
            if not dry_run:
                run(["gh", "release", "upload", tag, str(wheel_dir / name)])
    else:
        print("No wheel/metadata assets to upload.")

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync wheel assets for a GitHub release."
    )
    parser.add_argument("tag", help="Release tag")
    parser.add_argument("wheel_dir", help="Directory containing .whl files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without deleting or uploading assets",
    )
    args = parser.parse_args()

    main(args.tag, Path(args.wheel_dir), args.dry_run)
