import os
import zipfile
import subprocess
import re
import shutil
from collections import defaultdict


def get_dependencies(so_path):
    """Runs readelf and parses the NEEDED entries."""
    try:
        # readelf -d is efficient for pulling the dynamic section
        result = subprocess.check_output(
            ["readelf", "-d", so_path], stderr=subprocess.STDOUT
        ).decode()
        deps = re.findall(r"\(NEEDED\)\s+Shared library: \[(.*?)\]", result)
        return deps
    except Exception:
        return []


def process_wheels():
    cwd = os.getcwd()
    wheels = [f for f in os.listdir(cwd) if f.endswith(".whl")]

    if not wheels:
        print("No .whl files found in current directory.")
        return

    arch_summary = defaultdict(set)
    total_wheels = len(wheels)
    temp_dir = "temp_extract"

    for index, whl in enumerate(wheels, 1):
        # Progress calculation
        percent = (index / total_wheels) * 100
        # Dynamic print with \r to overwrite the line
        print(
            f"\rScanning ({percent:3.0f}%): {whl[:70] + '...' if len(whl) > 70 else whl.ljust(70)}",
            end="",
            flush=True,
        )

        # Detect architecture
        arch = "arm64" if "arm64_v8a" in whl else "arm" if "_arm" in whl else "unknown"

        try:
            with zipfile.ZipFile(whl, "r") as z:
                so_files = [name for name in z.namelist() if name.endswith(".so")]

                for so in so_files:
                    extract_path = z.extract(so, path=temp_dir)
                    found_deps = get_dependencies(extract_path)
                    arch_summary[arch].update(found_deps)

                    # Immediate cleanup of the extracted .so
                    os.remove(extract_path)
        except Exception:
            continue

    # Clear the progress line before printing results
    print("\r" + " " * 100 + "\rScan Complete.")

    # Final Consolidated Output
    print("\n" + "=" * 60)
    print("FINAL CONSOLIDATED LIBRARIES PER ARCHITECTURE")
    print("=" * 60)

    for arch in sorted(arch_summary.keys()):
        libs = sorted(list(arch_summary[arch]))
        print(f"\n[{arch.upper()}] - {len(libs)} unique dependencies:")

        # Print libraries in a clean, wrapped format
        line = "  "
        for i, lib in enumerate(libs):
            line += f"{lib}, "
            if (i + 1) % 4 == 0:
                print(line.rstrip(", "))
                line = "  "
        if line != "  ":
            print(line.rstrip(", "))

    # Cleanup temp directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    process_wheels()
