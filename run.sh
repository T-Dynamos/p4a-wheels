RECIPES="Pillow android apsw atom cffi cryptography flask freetype-py gevent httpx kivy kiwisolver matplotlib numpy pandas primp pycairo pydantic-core pyjnius pynacl scipy setuptools sqlalchemy tiktoken"

set -e

export PATH=$PATH:~/.local/bin/
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-virtualenv autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev automake autopoint gettext libltdl-dev po4a

# --- constant NDK setup ---
NDK_VERSION="r28c"
NDK_URL="https://dl.google.com/android/repository/android-ndk-${NDK_VERSION}-linux.zip"
NDK_DIR="$HOME/Android/android-ndk-${NDK_VERSION}"

if [ ! -d "$NDK_DIR" ]; then
    mkdir -p "$HOME/Android" && cd "$HOME/Android"
    echo "Downloading NDK $NDK_VERSION..."
    curl -LO "$NDK_URL" || wget "$NDK_URL"
    echo "Unpacking..."
    unzip -q "android-ndk-${NDK_VERSION}-linux.zip"
    rm "android-ndk-${NDK_VERSION}-linux.zip"
    echo "Installed to $NDK_DIR"
fi

export NDK_DIR

# --- rust setup ---
curl https://sh.rustup.rs -sSf | sh -s -- -y

# --- buildozer / p4a setup ---
export APP_ANDROID_ACCEPT_SDK_LICENSE=1
export BUILDOZER_WARN_ON_ROOT=0

pip3 install --user --upgrade buildozer cython virtualenv
pip3 install git+https://github.com/T-Dynamos/python-for-android@sdl_build_optimize

# https://github.com/kivy/python-for-android@develop

cd "$GITHUB_WORKSPACE"

mkdir -p p4aworkdir/output
WORKDIR=$(realpath p4aworkdir)
# --- build ---
ARCH=${1:-arm64-v8a}
P4A_WHEEL_DIR="$WORKDIR/output" TERM=xterm-256color python3 recipebuild.py -a "$ARCH" -r $RECIPES -w "$WORKDIR"

ls "$P4A_WHEEL_DIR"
