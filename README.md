# P4A Wheel Index

This repo hosts Android wheels built with python-for-android and publishes a
PEP 503 “simple” index so `pip` can install them directly. Wheels are hosted on
GitHub Releases, and the index includes PEP 658 metadata sidecar files.

## Quick Start

1. Build wheels with python-for-android.
2. Upload the wheels to a GitHub Release.
3. Generate the index into `docs/` and publish via GitHub Pages.

Example:
```bash
NDK_DIR=~/.buildozer/android/platform/android-ndk-r28c \
python3 recipebuild.py -a x86 -r <recipe list> -w ~/p4acache

python3 gen_pip_index.py \
  ~/p4a_raw_wheels/ \
  https://github.com/T-Dynamos/p4a-wheels/releases/download/1.2/ \
  docs/
```

## Project Layout

- `docs/`: Generated PEP 503 index (served by GitHub Pages).
- `*.whl`: Built wheels (local build artifacts or release uploads).

## Scripts

1. `recipebuild.py`

Builds wheels using python-for-android.

Example:
```bash
NDK_DIR=~/.buildozer/android/platform/android-ndk-r28c \
python3 recipebuild.py -a x86 -r <recipe list> -w ~/p4acache
```

2. `gen_pip_index.py`

Reads a directory of wheels, generates PEP 658 metadata sidecars, and writes a
complete PEP 503 “simple” index into the output directory.

Example:
```bash
python3 gen_pip_index.py \
  ~/p4a_raw_wheels/ \
  https://github.com/T-Dynamos/p4a-wheels/releases/download/1.2/ \
  docs/
```

3. `recipe_list.py`

Lists all `PyProjectRecipe` entries.

4. `get_wheel_lib_dep.py`

Scans wheels for `.so` dependencies and prints a consolidated list per
architecture.

Example:
```bash
python3 get_wheel_lib_dep.py ~/p4a_raw_wheels/
```

Sample output:
```text
Scan Complete.

============================================================
FINAL CONSOLIDATED LIBRARIES PER ARCHITECTURE
============================================================

[ANDROID_24_ARM] - 20 unique dependencies:
  libEGL.so, libGLESv2.so, libSDL3.so, libSDL3_image.so
  libSDL3_mixer.so, libSDL3_ttf.so, libc++_shared.so, libc.so
  libcairo.so, libcrypto.so, libdl.so, libffi.so
  libfreetype.so, liblog.so, libm.so, libpython3.14.so
  libsodium.so, libsqlite3.so, libssl.so, libz.so
```

5. `release.py`

Uploads wheels to a GitHub Release and syncs the release contents 1:1 with the
local directory.

## Using the Index with pip

You can install from the index with:
```bash
pip install \
  --disable-pip-version-check \
  --platform=android_24_arm64_v8a \
  --ignore-installed \
  --only-binary=:all: \
  --extra-index-url https://anshdadwal.is-a.dev/p4a-wheels/p4a \
  --target . <package>
```

## Supported Platform Tags

Wheels are built for the following platform tags (derived from the wheel
filenames). The tag `android_24_aarch64` is supported as an alias for
`android_24_arm64_v8a`.

Example tags:
- android_24_arm64_v8a
- android_24_aarch64
- android_24_arm
- android_24_i686
- android_24_x86_64

## Notes

- This repo assumes you already have python-for-android working locally.
- The index is static HTML. Regenerate it any time wheel contents change.
