#!/usr/bin/env bash
# sitemap.xml and robots.txt for the pages in public/ (not docs/ or api/,
# those bring their own). Run by build.sh after the pages are assembled.
set -euo pipefail
cd "$(dirname "$0")/.."
base="https://www.qtdmm.de"
today=$(date +%F)
{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  for f in public/*.html; do
    name=${f#public/}
    case $name in google*.html) continue;; esac
    loc="$base/$name"
    [ "$name" = index.html ] && loc="$base/"
    printf '  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' "$loc" "$today"
  done
  printf '  <url><loc>%s/docs/</loc><lastmod>%s</lastmod></url>\n' "$base" "$today"
  echo '</urlset>'
} > public/sitemap.xml
cat > public/robots.txt <<ROBOTS
User-agent: *
Allow: /
Disallow: /stats/
Disallow: /css/style.php

Sitemap: $base/sitemap.xml
ROBOTS
echo "public/sitemap.xml: $(grep -c '<url>' public/sitemap.xml) urls"
