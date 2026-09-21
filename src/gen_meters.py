#!/usr/bin/env python3
"""Generate the Supported-meters page body from rp-master/docs/user/supported-devices.md.

The Markdown table there is itself generated from the decoder registrations,
so this is the only place on the website that needs to follow the code.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT.parent / "rp-master" / "docs" / "user" / "supported-devices.md"
TEMPLATE = ROOT / "templates" / "pages" / "meters.html"
OUT = ROOT / "src" / ".gen" / "meters.html"   # page body; page.sh wraps it


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
            "model": model.replace("¹", "").strip(),
            "unconfirmed": "¹" in model,
            "chip": d.get("chip", "-"),
            "proto": d.get("protocol", "").strip("`"),
            "serial": d.get("serial", ""),
            "lines": d.get("lines", ""),
            "counts": d.get("counts", ""),
        })
    return rows


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC
    rows = parse(src.read_text(encoding="utf-8"))
    if not rows:
        sys.exit(f"no table rows found in {src}")
    vendors = sorted({r["vendor"] for r in rows}, key=str.lower)
    protos = sorted({r["proto"] for r in rows})

    tr = []
    for r in rows:
        mark = ' <sup title="added from chip data, not yet confirmed with QtDMM">?</sup>' if r["unconfirmed"] else ""
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
                .replace("@N_UNCONFIRMED@", str(sum(r["unconfirmed"] for r in rows))))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(rows)} meters, {len(vendors)} vendors, {len(protos)} protocols")


if __name__ == "__main__":
    main()
