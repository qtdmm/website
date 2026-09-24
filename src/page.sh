#!/usr/bin/env bash
# page.sh <body.html> <out.html> — wraps a page body in the shared topbar and
# footer. The body's first line names the page:
#   <!-- page: <nav-key> | <title> | <description> -->
# Optional environment (set by build.sh from gen_news.py):
#   NEWS=1        add the "News" entry to topbar and footer and the RSS link
#   LATEST_NEWS   file whose content replaces @LATEST_NEWS@ (home teaser)
set -euo pipefail
body=$1; out=$2
# Canonical URL: one address per page, so search engines stop treating
# www/non-www and http/https as four different sites.
canon="https://www.qtdmm.de/$(basename "$out")"
[ "$(basename "$out")" = index.html ] && canon="https://www.qtdmm.de/"
IFS='|' read -r active title desc < <(head -1 "$body" | sed -E 's/^<!-- page: *(.*) -->$/\1/; s/ *\| */|/g')
nav() { local key=$1 href=$2 label=$3 cls=""; [ "$key" = "$active" ] && cls=' class="active"'; printf '        <a href="%s"%s>%s</a>\n' "$href" "$cls" "$label"; }
{
cat <<HEAD
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} – QtDMM</title>
  <meta name="description" content="${desc}">
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" href="img/qtdmm_128.png" type="image/png">
  <link rel="stylesheet" href="css/site.css">
  <link rel="canonical" href="${canon}">
  <link rel="stylesheet" href="css/style.php">
HEAD
[ "${NEWS:-0}" = 1 ] && printf '  <link rel="alternate" type="application/rss+xml" title="QtDMM news" href="feed.xml">\n'
cat <<HEAD
</head>
<body>
  <header class="topbar">
    <div class="wrap">
      <a class="brand" href="index.html"><img src="img/qtdmm_128.png" alt="QtDMM logo"><span>Qt<b>DMM</b></span></a>
      <button class="menu-toggle" aria-label="Menu" onclick="document.querySelector('.nav').classList.toggle('open')">☰</button>
      <nav class="nav">
HEAD
nav home index.html Home
nav features features.html Features
nav meters meters.html "Supported Meters"
[ "${NEWS:-0}" = 1 ] && nav news news.html News
nav history history.html History
nav devdocs devdocs.html "Docs &amp; Dev"
nav contact contact.html Contact
printf '        <a class="cta" href="download.html">Download</a>\n'
cat <<HEAD
      </nav>
    </div>
  </header>
HEAD
if [ -n "${LATEST_NEWS:-}" ] && [ -s "$LATEST_NEWS" ]; then
  tail -n +2 "$body" | python3 -c 'import sys; sys.stdout.write(sys.stdin.read().replace("@LATEST_NEWS@\n", open(sys.argv[1]).read()))' "$LATEST_NEWS"
else
  tail -n +2 "$body" | grep -v '^@LATEST_NEWS@$' || true
fi
cat <<FOOT
  <footer>
    <div class="wrap">
      <div>QtDMM © 2016–2024 tuxmaster · © 2025–2026 redPanther and contributors · GPL-3.0</div>
      <nav>
        <a href="https://github.com/tuxmaster/QtDMM">GitHub</a>
        <a href="docs/" target="_blank" rel="noopener">Handbook</a>
        <a href="api/" target="_blank" rel="noopener">API</a>
        <a href="devdocs.html#build">Build</a>
FOOT
[ "${NEWS:-0}" = 1 ] && printf '        <a href="news.html">News</a>\n        <a href="feed.xml">RSS</a>\n'
cat <<FOOT
        <a href="contact.html">Contact</a>
        <a href="impressum.html">Impressum</a>
        <a href="datenschutz.html">Datenschutz</a>
      </nav>
    </div>
  </footer>
</body>
</html>
FOOT
} > "$out"
