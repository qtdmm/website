# qtdmm.de

Static website for [QtDMM](https://github.com/tuxmaster/QtDMM). Plain HTML/CSS,
no framework.

```
public/            the site as served (commit it)
public/docs/       MkDocs handbook, built from ../rp-master — not committed
public/api/        Doxygen developer docs (cmake target in ../rp-master/build) — not committed
src/gen_meters.py  supported-devices.md → public/meters.html
src/page.sh        wraps a page body (templates/pages/*.html) in topbar/footer
src/gen_news.py    news/*.md → news page, RSS feed, home teaser (hidden while news/ is empty)
templates/pages/   the page bodies — edit these, not public/*.html
news/              announcements, one Markdown file each (see news/README.md)
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

```bash
./build.sh                                   # needs mkdocs
FTP_HOST=ftp.example.net FTP_DIR=/ ./deploy.sh --dry-run
```
