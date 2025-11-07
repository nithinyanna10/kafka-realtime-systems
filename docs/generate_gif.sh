#!/usr/bin/env bash
set -euo pipefail

# Requirements:
# - mermaid-cli (mmdc)
# - ImageMagick (convert)
#
# Install on macOS:
#   brew install node imagemagick
#   npm install -g @mermaid-js/mermaid-cli

DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/message_flow.mmd"
PNG_OUT="$DIR/message_flow.png"
GIF_OUT="$DIR/message_flow.gif"

if ! command -v mmdc >/dev/null 2>&1; then
  echo "Error: mermaid-cli (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli" >&2
  exit 1
fi

# Render Mermaid to PNG (transparent background looks better when gif-converted)
mmdc -i "$SRC" -o "$PNG_OUT" -b transparent -s 1.2

if ! command -v convert >/dev/null 2>&1; then
  echo "Warning: ImageMagick 'convert' not found. Skipping GIF creation. PNG generated at $PNG_OUT" >&2
  exit 0
fi

# Create a simple animated GIF by fading in the PNG (2 frames)
convert -delay 20 -loop 0 \
  \( -size 1200x50 xc:none -gravity center -pointsize 28 \
     -fill "#333333" -annotate +0+0 "Kafka Message Flow" \) \
  "$PNG_OUT" "$GIF_OUT"

echo "Generated: $PNG_OUT"
if [ -f "$GIF_OUT" ]; then
  echo "Generated: $GIF_OUT"
fi

