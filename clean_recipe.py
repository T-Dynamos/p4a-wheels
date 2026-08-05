#!/usr/bin/python3

from configparser import ConfigParser
import os
import sys
from shutil import rmtree
from glob import glob

recipes = sys.argv[1:]

config = ConfigParser()
# config.read("buildozer.spec")

pkg_name = "sdl3" # config["app"]["package.name"] 
archs = ["arm64-v8a", "armeabi-v7a", "x86", "x86_64"] # list(_.strip() for _ in config["app"]["android.archs"].split(","))
# build_folder_name = f"build-{'_'.join(archs)}"

base_folder = "/home/tdynamos/p4acache/"# os.path.realpath(f".buildozer/android/platform/{build_folder_name}/")

build_folder = os.path.join(base_folder, "build")


def remove(dir):
    if os.path.exists(dir):
        print(f"Removing: {dir}")
        rmtree(dir)
    else:
        print(f"Not found : {dir}")

# remove(os.path.join(base_folder, f"dists/{pkg_name}/dist_info.json"))

for recipe in recipes:
    rbf = os.path.join(build_folder, f"other_builds/{recipe}")
    if os.path.isdir(rbf):
        remove(rbf)

    # like android-sdl3 etc
    df = glob(os.path.join(base_folder, "packages", f"{recipe}*"))
    [remove(d) for d in df]

    for arch in archs: 
        glob_str = os.path.join(build_folder, f"python-installs/{pkg_name}/{arch}/*{recipe}*")
        try:
            dirs = glob(glob_str)
            [remove(dir) for dir in dirs]
        except:
            pass
