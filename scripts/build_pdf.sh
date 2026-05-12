#!/bin/bash
# Build PDF from Markdown resume using Pandoc + weasyprint with HTML/CSS template
# Usage: ./build_pdf.sh <input.md> [output.pdf] [--template <html-template>]

set -euo pipefail

INPUT="${1:-draft_resume.md}"
OUTPUT="${2:-resume.pdf}"
TEMPLATE=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_TEMPLATE="$SCRIPT_DIR/../assets/resume-template/template.html"
DEFAULT_CSS="$SCRIPT_DIR/../assets/resume-template/style.css"

# Parse optional --template flag
EXTRA_ARGS=()
if [ $# -ge 3 ]; then
    if [ "$3" = "--template" ] && [ $# -ge 4 ]; then
        TEMPLATE="$4"
    fi
fi

if [ ! -f "$INPUT" ]; then
    echo "Error: input file '$INPUT' not found"
    echo "Usage: $0 <input.md> [output.pdf] [--template <html-template>]"
    exit 1
fi

# Check pandoc
if ! command -v pandoc &>/dev/null; then
    echo "Error: pandoc not found. Install it first."
    exit 1
fi

# Use CSS template if available
CSS_FLAG=""
if [ -f "$DEFAULT_CSS" ]; then
    CSS_FLAG="--css $DEFAULT_CSS"
fi

# Prefer weasyprint for styled output
if command -v weasyprint &>/dev/null; then
    echo "Using Pandoc + weasyprint..."
    if [ -f "$DEFAULT_TEMPLATE" ]; then
        # Convert MD -> HTML with CSS, then wrap in template
        BODY_HTML=$(pandoc "$INPUT" $CSS_FLAG -f markdown -t html --self-contained 2>/dev/null)
        CSS_CONTENT=$(cat "$DEFAULT_CSS")
        FULL_HTML=$(cat "$DEFAULT_TEMPLATE" | sed "s|{{CSS}}|$CSS_CONTENT|g" | sed "s|{{CONTENT}}|$BODY_HTML|g")
        echo "$FULL_HTML" | pandoc -f html -o "$OUTPUT" --pdf-engine=weasyprint
    else
        pandoc "$INPUT" $CSS_FLAG -o "$OUTPUT" --pdf-engine=weasyprint
    fi
    echo "PDF generated: $OUTPUT"
    exit 0
fi

# Fallback: Chrome headless
HAS_CHROME=$(command -v google-chrome &>/dev/null && echo 1 || echo 0)
HAS_CHROMIUM=$(command -v chromium &>/dev/null && echo 1 || echo 0)
HAS_EDGE=$(command -v msedge &>/dev/null && echo 1 || echo 0)

if [ "$HAS_CHROME" = "1" ] || [ "$HAS_CHROMIUM" = "1" ] || [ "$HAS_EDGE" = "1" ]; then
    BROWSER="google-chrome"
    [ "$HAS_CHROMIUM" = "1" ] && BROWSER="chromium"
    [ "$HAS_EDGE" = "1" ] && BROWSER="msedge"

    HTML_FILE="${OUTPUT%.pdf}.html"
    pandoc "$INPUT" $CSS_FLAG -o "$HTML_FILE" --self-contained
    "$BROWSER" --headless --disable-gpu --print-to-pdf="$OUTPUT" "$HTML_FILE" 2>/dev/null
    rm -f "$HTML_FILE"
    echo "PDF generated: $OUTPUT"
    exit 0
fi

echo "Error: no PDF renderer found."
echo "Install one of:"
echo "  - weasyprint (recommended): pip install weasyprint"
echo "  - Google Chrome / Chromium"
exit 1
