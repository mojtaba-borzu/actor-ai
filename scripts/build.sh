#!/bin/zsh
set -eu
cd "$(dirname "$0")/.."
app="$PWD/.build/Actor.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
compile() {
    swiftc -target "$1-apple-macosx13.0" app/Actor.swift -o "$2" -framework AppKit -framework QuartzCore -O
}

# A local build only has to run on this Mac. A released one has to run on both
# architectures, so CI sets ACTOR_UNIVERSAL and the two slices are lipo'd together.
if [[ -n "${ACTOR_UNIVERSAL:-}" ]]; then
    compile arm64 "$app/Contents/MacOS/Actor.arm64"
    compile x86_64 "$app/Contents/MacOS/Actor.x86_64"
    lipo -create "$app/Contents/MacOS/Actor.arm64" "$app/Contents/MacOS/Actor.x86_64" -output "$app/Contents/MacOS/Actor"
    rm "$app/Contents/MacOS/Actor.arm64" "$app/Contents/MacOS/Actor.x86_64"
else
    compile "$(uname -m)" "$app/Contents/MacOS/Actor"
fi
cp app/bridge.py "$app/Contents/Resources/bridge.py"
if [[ -d app/Skins ]]; then
    mkdir -p "$app/Contents/Resources/Skins"
    cp -R app/Skins/. "$app/Contents/Resources/Skins/"
fi
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>Actor</string>
<key>CFBundleIdentifier</key><string>local.actor.companion</string>
<key>CFBundleName</key><string>Actor</string>
<key>CFBundleVersion</key><string>1</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>LSUIElement</key><true/>
<key>NSHighResolutionCapable</key><true/>
<key>LSMinimumSystemVersion</key><string>13.0</string>
</dict></plist>
PLIST
codesign --force --sign - "$app"
echo "Built $app"
