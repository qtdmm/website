# qtdmm.de

Static website for [QtDMM](https://github.com/qtdmm/QtDMM). Plain HTML/CSS,
no framework.

```
public/            the site as served (commit it)
public/docs/       MkDocs handbook, built from qtdmm-src — not committed
public/api/        Doxygen developer docs (cmake target in qtdmm-src/build) — not committed
src/gen_meters.py  supported-devices.md → public/meters.html
src/page.sh        wraps a page body (templates/pages/*.html) in topbar/footer
src/gen_news.py    news/*.md → news page, RSS feed, home teaser (hidden while news/ is empty)
templates/pages/   the page bodies — edit these, not public/*.html
news/              announcements, one Markdown file each (see news/README.md)
public/scripts/style.php  visitor counter: every page links it as a stylesheet
public/conf/              its SQLite database and the protected evaluation page
qtdmm-src/         own clone of QtDMM (master), created by build.sh — not committed
build.sh           pull qtdmm-src, assemble all pages, meters, news, mkdocs, doxygen
deploy.sh          lftp mirror to the host (credentials from ~/.netrc or env)
```

Colours come from the program's analog meter (anthracite bezel) and LCD
display (`#dadc77`), red as accent. Impressum/Datenschutz are German as
required for a .de domain — fill in the bracketed placeholders before going
live.

Screenshots: `public/img/meter*.png` / `display*.png` are rendered by the test
suite (`TEST_METER_DUMP`, `TEST_DISPLAY_DUMP`). Dashed boxes on the pages mark
where full-window screenshots still need to go; the file name shown is the
expected path under `tmp/screenshots/`.

## Visitor counter

Every page links `scripts/style.php` as a stylesheet (added by `src/page.sh`). The
script answers with empty CSS and records date, time and a salted hash of the
IP address in `conf/stats.sqlite`, so repeat views on the same day count once.
The salt (`conf/salt.txt`) and the database are created on the server on first
use, are not in the repository, and are excluded from the deploy mirror — do
not delete them there, or the numbers start over. `conf/stats.php` shows the
figures and is behind HTTP basic auth (`conf/.htaccess`, user file in the
hosting account). Entries older than 12 months are deleted, which is what
section 4 of the Datenschutz page promises: **change one, change the other.**

```bash
./build.sh                                   # needs mkdocs
FTP_HOST=ftp.example.net FTP_DIR=/ ./deploy.sh --dry-run
```
