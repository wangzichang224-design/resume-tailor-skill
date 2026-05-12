#!/bin/bash
# Privacy check: scan repo for real personal info before publishing
set -euo pipefail

REPO_DIR="$(dirname "$0")/.."
ISSUES=0

echo "=== Privacy Check ==="
echo ""

# Patterns to detect
PATTERNS=(
    "wangzichang224"
    "1[3-9][0-9]{9}"  # Chinese phone number
    "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  # email
    "王子畅"
)

for pattern in "${PATTERNS[@]}"; do
    # Exclude known false-positives: .gitignore, README mentions, git config
    RESULTS=$(grep -rn "$pattern" "$REPO_DIR" \
        --include="*.py" --include="*.json" --include="*.md" --include="*.toml" \
        --include="*.yaml" --include="*.yml" --include="*.txt" \
        --exclude-dir=.git \
        --exclude-dir=__pycache__ \
        --exclude="*.local.json" \
        --exclude=".gitignore" \
        --exclude="LICENSE" \
        2>/dev/null || true)
    if [ -n "$RESULTS" ]; then
        echo "WARNING: Pattern '$pattern' found in:"
        echo "$RESULTS"
        echo ""
        ISSUES=$((ISSUES + 1))
    fi
done

if [ "$ISSUES" -eq 0 ]; then
    echo "No obvious privacy issues found."
else
    echo "Found $ISSUES potential privacy issue(s). Review before publishing."
fi
