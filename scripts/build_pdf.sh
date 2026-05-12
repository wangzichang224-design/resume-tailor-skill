#!/bin/bash
# Build PDF from Markdown resume using Pandoc + Chromium/Chrome
# Usage: ./build_pdf.sh <input.md> [output.pdf]

set -euo pipefail

INPUT="${1:-draft_resume.md}"
OUTPUT="${2:-resume.pdf}"

if [ ! -f "$INPUT" ]; then
    echo "Error: input file '$INPUT' not found"
    echo "Usage: $0 <input.md> [output.pdf]"
    exit 1
fi

# Check available renderers
HAS_PANDOC=$(command -v pandoc &>/dev/null && echo 1 || echo 0)
HAS_CHROME=$(command -v google-chrome &>/dev/null && echo 1 || echo 0)
HAS_CHROMIUM=$(command -v chromium &>/dev/null && echo 1 || echo 0)
HAS_EDGE=$(command -v msedge &>/dev/null && echo 1 || echo 0)

# Prefer Chrome headless → Chromium → Pandoc weasyprint
if [ "$HAS_CHROME" = "1" ] || [ "$HAS_CHROMIUM" = "1" ] || [ "$HAS_EDGE" = "1" ]; then
    BROWSER="google-chrome"
    [ "$HAS_CHROMIUM" = "1" ] && BROWSER="chromium"
    [ "$HAS_EDGE" = "1" ] && BROWSER="msedge"

    # Convert Markdown to HTML first
    if [ "$HAS_PANDOC" = "1" ]; then
        pandoc "$INPUT" -o "${OUTPUT%.pdf}.html" --self-contained
        "$BROWSER" --headless --disable-gpu --print-to-pdf="$OUTPUT" "${OUTPUT%.pdf}.html" 2>/dev/null
        rm -f "${OUTPUT%.pdf}.html"
    else
        echo "Pandoc not found; install pandoc for better Markdown→HTML conversion"
        exit 1
    fi
elif [ "$HAS_PANDOC" = "1" ]; then
    # Fallback: Pandoc + weasyprint
    pandoc "$INPUT" -o "$OUTPUT" --pdf-engine=weasyprint
else
    echo "Error: no PDF renderer found."
    echo "Install one of:"
    echo "  - Google Chrome / Chromium (recommended)"
    echo "  - Pandoc + weasyprint"
    echo "  - Pandoc + prince"
    exit 1
fi

echo "PDF generated: $OUTPUT"
