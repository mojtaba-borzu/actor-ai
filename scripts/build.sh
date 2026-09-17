#!/bin/zsh
set -eu
cd "$(dirname "$0")/.."
app="$PWD/.build/Actor.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
swiftc -target "$(uname -m)-apple-macosx13.0" app/Actor.swift -o "$app/Contents/MacOS/Actor" -framework AppKit -framework QuartzCore -O
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
