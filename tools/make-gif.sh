#!/bin/zsh
# Renders a looping GIF of the companion using the app's own drawing code.
# usage: ./tools/make-gif.sh [provider] [output.gif]
set -eu
cd "$(dirname "$0")/.."
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
# Strip the app launch so the file has no top-level entry point of its own,
# and ignore the system Reduce Motion setting so the GIF always animates.
sed -e '/^let application = NSApplication.shared$/,$d' \
    -e 's/let still = reduced || NSWorkspace.shared.accessibilityDisplayShouldReduceMotion/let still = reduced/' \
    app/Actor.swift > "$work/main.swift"
cat tools/gif-main.swift >> "$work/main.swift"
swiftc -target "$(uname -m)-apple-macosx13.0" "$work/main.swift" -o "$work/gifmaker" \
    -framework AppKit -framework QuartzCore -framework ImageIO -O
"$work/gifmaker" "${1:-Claude}" "$PWD/${2:-actor.gif}"
