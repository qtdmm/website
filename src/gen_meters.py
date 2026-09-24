#!/usr/bin/env python3
"""Generate the Supported-meters page body from rp-master/docs/user/supported-devices.md.

The Markdown table there is itself generated from the decoder registrations,
so this is the only place on the website that needs to follow the code.
"""
import re
from urllib.parse import quote
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT.parent / "rp-master" / "docs" / "user" / "supported-devices.md"
TEMPLATE = ROOT / "templates" / "pages" / "meters.html"
OUT = ROOT / "src" / ".gen" / "meters.html"   # page body; page.sh wraps it


# Home's vendor cloud: best-known brands first, the rest alphabetically.
CLOUD_ORDER = ["Uni-Trend", "Voltcraft", "Metex", "MASTECH", "PeakTech", "Tenma",
               "Keysight", "Agilent", "HP", "Siglent", "Fluke", "Victron", "Brymen",
               "APPA", "GW Instek", "Metrel", "Protek", "Velleman", "PCE", "Digitech",
               "Digitek", "Radioshack", "ELV", "McVoice", "Vichy", "TekPower",
               "HoldPeak", "Iso-Tech", "Duratool", "Tecpel", "Pro'sKit", "V&A",
               "Wintex", "SparkFun"]
CLOUD_LABEL = {"Uni-Trend": "Uni\u2011Trend", "Iso-Tech": "Iso\u2011Tech",
               "Pro'sKit": "Pro\u2019sKit", "Generic": "DTM0660 generic"}
CLOUD_SKIP = {"sigrok"}   # not a brand: "any meter sigrok-cli supports"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse(md: str):
    """Reads the table by its header, so added columns (Chip) do not shift
    the others. Models marked with the footnote sign are unconfirmed."""
    rows = []
    header = None
    for line in md.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Vendor":
            header = [c.lower() for c in cells]
            continue
        if header is None or set(cells[0]) <= {"-"}:
            continue
        d = dict(zip(header, cells))
        model = d.get("model", "")
        rows.append({
            "vendor": d.get("vendor", ""),
            "model": model.replace("¹", "").replace("²", "").strip(),
            "unconfirmed": "¹" in model,
            "hwmod": "²" in model,
            "chip": d.get("chip", "-"),
            "proto": d.get("protocol", "").strip("`"),
            "serial": d.get("serial", ""),
            "lines": d.get("lines", ""),
            "counts": d.get("counts", ""),
        })
    return rows


LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
STRONG = re.compile(r"\*\*([^*]+)\*\*")
EM = re.compile(r"\*([^*]+)\*")


def md_inline(text: str) -> str:
    """The little Markdown the footnotes use: links, **bold**, *em*."""
    text = esc(text)
    text = LINK.sub(r'<a href="\2">\1</a>', text)
    text = STRONG.sub(r"<b>\1</b>", text)
    return EM.sub(r"<em>\1</em>", text)


def hwmod_notes(text: str) -> list[str]:
    """Bullet list following the '² needs a hardware modification' footnote."""
    notes, inside = [], False
    for line in text.splitlines():
        if line.startswith("²"):
            inside = True
            continue
        if inside and line.startswith("- "):
            notes.append(md_inline(line[2:].strip()))
        elif inside and notes and not line.strip():
            break
    return notes


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    rows = parse(src.read_text(encoding="utf-8"))
    if not rows:
        sys.exit(f"no table rows found in {src}")
    vendors = sorted({r["vendor"] for r in rows}, key=str.lower)
    protos = sorted({r["proto"] for r in rows})

    notes = hwmod_notes(src.read_text(encoding="utf-8"))
    tr = []
    for r in rows:
        mark = ' <sup title="added from chip data, not yet confirmed with QtDMM">?</sup>' if r["unconfirmed"] else ""
        if r["hwmod"]:
            mark += ' <a class="mod" href="#hwmod" title="needs a hardware modification – the meter has no interface as sold">mod</a>'
        tr.append(
            f'        <tr data-vendor="{esc(r["vendor"])}">'
            f'<td>{esc(r["vendor"])}</td><td>{esc(r["model"])}{mark}</td>'
            f'<td>{esc(r["chip"])}</td>'
            f'<td><code>{esc(r["proto"])}</code></td><td>{esc(r["serial"])}</td>'
            f'<td>{esc(r["lines"])}</td><td>{esc(r["counts"])}</td></tr>'
        )
    opts = "".join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in vendors)

    html = TEMPLATE.read_text(encoding="utf-8")
    html = (html.replace("@ROWS@", "\n".join(tr))
                .replace("@VENDOR_OPTIONS@", opts)
                .replace("@N_METERS@", str(len(rows)))
                .replace("@N_VENDORS@", str(len(vendors)))
                .replace("@N_PROTOS@", str(len(protos)))
                .replace("@N_UNCONFIRMED@", str(sum(r["unconfirmed"] for r in rows)))
                .replace("@HWMOD_NOTES@", "".join(f"<li>{n}</li>" for n in notes)))
    if not notes:   # no such footnote in the source yet: drop the legend row
        html = re.sub(r'\s*<div id="hwmod">.*?</div>\n', "\n", html, count=1, flags=re.S)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    # Figures and the vendor cloud for the other pages: build.sh replaces
    # @N_METERS@, @N_VENDORS@, @N_PROTOS@ and @VENDOR_CLOUD@ in every page, so
    # Home, descriptions and headings follow the table instead of drifting.
    (OUT.parent / "counts.env").write_text(
        f"N_METERS={len(rows)}\nN_VENDORS={len(vendors)}\nN_PROTOS={len(protos)}\n",
        encoding="utf-8")
    ordered = [v for v in CLOUD_ORDER if v in vendors]
    ordered += [v for v in vendors if v not in CLOUD_ORDER and v not in CLOUD_SKIP]
    (OUT.parent / "vendor-cloud.html").write_text("".join(
        f'<a href="meters.html?vendor={quote(v)}">{esc(CLOUD_LABEL.get(v, v))}</a>'
        for v in ordered), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(rows)} meters, {len(vendors)} vendors, {len(protos)} protocols")


if __name__ == "__main__":
    main()
