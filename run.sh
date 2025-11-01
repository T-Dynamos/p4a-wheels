RECIPES="Pillow android apsw atom aubio cffi cryptography ffpyplayer flask freetype-py gevent greenlet grpcio httpx kivy kiwisolver matplotlib numpy pandas primp pycairo pydantic-core pyjnius pynacl setuptools sqlalchemy tiktoken uvloop"
export PATH=$PATH:~/.local/bin/

sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-virtualenv autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev automake autopoint gettext libltdl-dev

# setup ndk
ver=${1:-r28c}
url="https://dl.google.com/android/repository/android-ndk-${ver}-linux.zip"
dir=${2:-$HOME/Android}
mkdir -p "$dir" && cd "$dir"
echo "Downloading NDK $ver..."
curl -LO "$url" || wget "$url"
echo "Unpacking..."
unzip -q "android-ndk-${ver}-linux.zip"
rm "android-ndk-${ver}-linux.zip"
echo "Installed to $dir/android-ndk-${ver}"

export NDK_DIR="$dir/android-ndk-${ver}"

# setup rust
curl https://sh.rustup.rs -sSf | sh -s -- -y

# if we use buildozer
export APP_ANDROID_ACCEPT_SDK_LICENSE=1
export BUILDOZER_WARN_ON_ROOT=0

# setup p4a 
pip3 install --user --upgrade buildozer cython virtualenv
pip3 install git+https://github.com/kivy/python-for-android@develop

cd "$GITHUB_WORKSPACE"

mkdir p4aworkdir
mkdir p4aworkdir/output

WORKDIR=$(realpath p4aworkdir)
P4A_WHEEL_DIR=$WORKDIR/output

# build
P4A_WHEEL_DIR=$WORKDIR/output python3 recipebuild.py -a $1 -r $RECIPES -w $WORKDIR
ls $P4A_WHEEL_DIR
