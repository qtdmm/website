#!/usr/bin/env bash
# page.sh <out.html> <active-nav-key> <title> <description>  — body from stdin.
# Wraps a page body in the shared topbar/footer. Used once when authoring the
# pages; the generated files in public/ are committed as-is.
set -euo pipefail
out=$1; active=$2; title=$3; desc=$4
nav() { local key=$1 href=$2 label=$3 cls=""; [ "$key" = "$active" ] && cls=' class="active"'; [ "$key" = docs ] && cls="$cls"' target="_blank" rel="noopener"'; printf '        <a href="%s"%s>%s</a>\n' "$href" "$cls" "$label"; }
{
cat <<HEAD
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} – QtDMM</title>
  <meta name="description" content="${desc}">
  <link rel="icon" href="img/qtdmm_128.png" type="image/png">
  <link rel="stylesheet" href="css/site.css">
</head>
<body>
  <header class="topbar">
    <div class="wrap">
      <a class="brand" href="index.html"><img src="img/qtdmm_128.png" alt=""><span>Qt<b>DMM</b></span></a>
      <button class="menu-toggle" aria-label="Menu" onclick="document.querySelector('.nav').classList.toggle('open')">☰</button>
      <nav class="nav">
HEAD
nav home index.html Home
nav features features.html Features
nav meters meters.html "Supported Meters"
nav history history.html History
nav docs docs/ Handbook
nav contact contact.html Contact
printf '        <a class="cta" href="download.html">Download</a>\n'
cat <<HEAD
      </nav>
    </div>
  </header>
HEAD
cat
cat <<FOOT
  <footer>
    <div class="wrap">
      <div>© 2001–2016 Matthias Toussaint · © 2016–2026 tuxmaster and contributors · GPL-3.0</div>
      <nav>
        <a href="https://github.com/tuxmaster/QtDMM">GitHub</a>
        <a href="docs/" target="_blank" rel="noopener">Handbook</a>
        <a href="api/" target="_blank" rel="noopener">API</a>
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
