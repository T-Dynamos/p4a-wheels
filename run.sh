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
pip3 install git+https://github.com/kivy/python-for-android

cd "$GITHUB_WORKSPACE"
mkdir p4aworkdir
python3 recipebuild.py -a arm64-v8a -a armeabi-v7a -r numpy -w p4aworkdir
ls p4aworkdir/output/
