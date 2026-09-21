#!/usr/bin/env bash
# Build everything that is generated: the meter table and the MkDocs handbook.
# Result is a complete static site in public/.
set -euo pipefail
cd "$(dirname "$0")"
# Source checkout the site is built from: our own clone of QtDMM on master,
# never Sarah's working copy in ../rp-master (that one is usually on a
# feature branch). Cloned on first use, pulled on every build.
RP=${RP_MASTER:-qtdmm-src}
if [ ! -d "$RP/.git" ]; then
  git clone -q git@github.com:redPanther/QtDMM.git "$RP"
fi
git -C "$RP" checkout -q master && git -C "$RP" pull -q --ff-only
[ -d "$RP/build" ] || cmake -S "$RP" -B "$RP/build" -DCMAKE_BUILD_TYPE=Release >/dev/null

# Page bodies live in templates/pages/; the generated ones (meters, news)
# land in src/.gen/. page.sh wraps each in topbar/footer.
rm -rf src/.gen && mkdir -p src/.gen
python3 src/gen_meters.py "$RP/docs/user/supported-devices.md"
python3 src/gen_news.py
NEWS=$(cat src/.gen/news.flag)
export NEWS LATEST_NEWS=src/.gen/latest.html
for body in templates/pages/*.html src/.gen/meters.html src/.gen/news.html; do
  [ -f "$body" ] || continue
  name=$(basename "$body")
  [ "$name" = meters.html ] && [ "$body" != src/.gen/meters.html ] && continue   # the template, not the page
  src/page.sh "$body" "public/$name"
done

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
