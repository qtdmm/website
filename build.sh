#!/usr/bin/env bash
# Build everything that is generated: the meter table and the MkDocs handbook.
# Result is a complete static site in public/.
set -euo pipefail
cd "$(dirname "$0")"
RP=${RP_MASTER:-../rp-master}   # a checkout of rp-master master, e.g. a worktree

python3 src/gen_meters.py "$RP/docs/user/supported-devices.md"

rm -rf public/docs
# src/mkdocs-site.yml is a template: its INHERIT/docs_dir point at $RP.
# mkdocs resolves those paths relative to the config file, so write the
# filled-in copy next to it.
RPABS=$(cd "$RP" && pwd)
sed "s|@RP@|$RPABS|g" src/mkdocs-site.yml > src/.mkdocs-site.generated.yml
mkdocs build --quiet -f src/.mkdocs-site.generated.yml -d "$PWD/public/docs"
rm -f src/.mkdocs-site.generated.yml
echo "public/docs: $(find public/docs -name '*.html' | wc -l) pages"

# Developer (API) documentation from Doxygen, built via the project's cmake
# target. Needs a configured build dir in rp-master; skipped otherwise.
rm -rf public/api
if [ -d "$RP/build" ] && command -v doxygen >/dev/null; then
  cmake --build "$RP/build" --target doxygen >/dev/null
  cp -r "$RP/build/doxygen/html" public/api
  echo "public/api: $(find public/api -name '*.html' | wc -l) pages"
else
  echo "warning: no $RP/build or doxygen missing - public/api not built" >&2
fi
