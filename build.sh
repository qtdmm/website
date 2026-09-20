#!/usr/bin/env bash
# Build everything that is generated: the meter table and the MkDocs handbook.
# Result is a complete static site in public/.
set -euo pipefail
cd "$(dirname "$0")"
RP=${RP_MASTER:-../rp-master}

python3 src/gen_meters.py "$RP/docs/user/supported-devices.md"

rm -rf public/docs
# src/mkdocs-site.yml inherits $RP/mkdocs.yml (path is relative to that file)
mkdocs build --quiet -f src/mkdocs-site.yml -d "$PWD/public/docs"
echo "public/docs: $(find public/docs -name '*.html' | wc -l) pages"
