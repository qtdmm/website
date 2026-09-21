#!/usr/bin/env python3
"""News / announcements for qtdmm.de.

One Markdown file per entry in news/ (see news/README.md). Writes, into
src/.gen/:
  news.html    page body (only if there is at least one entry)
  latest.html  the home-page teaser for the newest entry
  news.flag    "1" when entries exist, "0" otherwise - build.sh reads it
and public/feed.xml (RSS 2.0). Without entries nothing is written and any
stale news.html / feed.xml in public/ are removed, so the site shows no
trace of the section.
"""
import html
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
NEWS = ROOT / "news"
GEN = ROOT / "src" / ".gen"
TEMPLATE = ROOT / "templates" / "news.html.in"
SITE = "https://qtdmm.de/"
FEED_LIMIT = 20


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.split("#")[0].strip() if "#" in v and "http" not in v else v.strip()
    for req in ("title", "date"):
        if req not in meta:
            sys.exit(f"{path}: front matter needs '{req}'")
    date = datetime.strptime(meta["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return {
        "slug": path.stem,
        "title": meta["title"],
        "date": date,
        "link": meta.get("link", ""),
        "body_md": m.group(2).strip(),
        "body_html": markdown.markdown(m.group(2).strip(), extensions=["tables"]),
    }


def main():
    GEN.mkdir(exist_ok=True)
    entries = sorted((parse(p) for p in NEWS.glob("*.md") if p.name != "README.md"),
                     key=lambda e: (e["date"], e["slug"]), reverse=True)
    for stale in (GEN / "news.html", GEN / "latest.html", ROOT / "public" / "news.html", ROOT / "public" / "feed.xml"):
        stale.unlink(missing_ok=True)
    (GEN / "news.flag").write_text("1" if entries else "0")
    if not entries:
        print("news: no entries, section hidden")
        return

    def esc(s): return html.escape(s, quote=True)

    # page body
    items = []
    for e in entries:
        link = f' <a class="news-link" href="{esc(e["link"])}">→ {"GitHub" if "github.com" in e["link"] else "more"}</a>' if e["link"] else ""
        items.append(
            f'      <article class="news-entry" id="{esc(e["slug"])}">\n'
            f'        <time datetime="{e["date"]:%Y-%m-%d}">{e["date"]:%-d %b %Y}</time>\n'
            f'        <h3><a href="#{esc(e["slug"])}">{esc(e["title"])}</a></h3>\n'
            f'        <div class="news-body">{e["body_html"]}</div>{link}\n'
            f'      </article>')
    (GEN / "news.html").write_text(TEMPLATE.read_text(encoding="utf-8").replace("@ENTRIES@", "\n".join(items)), encoding="utf-8")

    # home teaser
    n = entries[0]
    (GEN / "latest.html").write_text(
        '  <div class="news-strip"><div class="wrap">'
        f'<span class="badge">New</span> <time datetime="{n["date"]:%Y-%m-%d}">{n["date"]:%-d %b %Y}</time> '
        f'<a href="news.html#{esc(n["slug"])}">{esc(n["title"])}</a> <a class="muted" href="news.html">all news →</a>'
        '</div></div>\n', encoding="utf-8")

    # RSS
    rss = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
           '  <title>QtDMM news</title>', f'  <link>{SITE}news.html</link>',
           '  <description>Releases and announcements for QtDMM, the digital multimeter readout and recorder.</description>',
           '  <language>en</language>',
           f'  <atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>',
           f'  <lastBuildDate>{format_datetime(entries[0]["date"])}</lastBuildDate>']
    for e in entries[:FEED_LIMIT]:
        rss += ['  <item>', f'    <title>{esc(e["title"])}</title>',
                f'    <link>{SITE}news.html#{esc(e["slug"])}</link>',
                f'    <guid isPermaLink="true">{SITE}news.html#{esc(e["slug"])}</guid>',
                f'    <pubDate>{format_datetime(e["date"])}</pubDate>',
                f'    <description>{esc(e["body_html"])}</description>', '  </item>']
    rss += ['</channel>', '</rss>', '']
    (ROOT / "public" / "feed.xml").write_text("\n".join(rss), encoding="utf-8")
    print(f"news: {len(entries)} entries, newest {entries[0]['date']:%Y-%m-%d} {entries[0]['title']!r}")


if __name__ == "__main__":
    main()
