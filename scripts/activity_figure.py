"""Draw assets/fig-4-activity.svg from the public GitHub contribution calendar.

Weekly contribution totals, set as a figure in the same paper style as the rest of
the README. No token needed: github.com/users/<user>/contributions is public.
"""
import re
import sys
import urllib.request
from collections import OrderedDict
from datetime import date
from pathlib import Path

USER = "suryatenz"
OUT = Path(__file__).resolve().parent.parent / "assets" / "fig-4-activity.svg"
W, H = 1200, 400
L, R, T, B = 90, 1150, 60, 320


def fetch_days():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"}
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    ids = dict(
        (cid, d) for d, cid in re.findall(r'<td[^>]*data-date="([\d-]+)"[^>]*id="([^"]+)"', html)
    )
    days = {}
    for cid, tip in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', html):
        if cid in ids:
            m = re.match(r"\s*(\d+)\s+contribution", tip)
            days[ids[cid]] = int(m.group(1)) if m else 0
    if not days:
        sys.exit("no contribution data parsed; page format may have changed")
    return dict(sorted(days.items()))


def summarise(days):
    weeks = OrderedDict()
    for d, n in days.items():
        iso = date.fromisoformat(d).isocalendar()
        key = (iso[0], iso[1])
        if key not in weeks:
            weeks[key] = [d, 0]
        weeks[key][1] += n
    longest = run = 0
    for n in days.values():
        run = run + 1 if n else 0
        longest = max(longest, run)
    return {
        "weeks": list(weeks.values()),
        "total": sum(days.values()),
        "active": sum(1 for n in days.values() if n),
        "longest": longest,
    }


def nice_max(v):
    for step in (5, 10, 20, 25, 50, 100, 200, 250, 500):
        if v <= step * 4:
            return step * 4, step
    return v, v // 4


def render(s):
    wk = s["weeks"]
    top, step = nice_max(max(n for _, n in wk) or 1)
    slot = (R - L) / len(wk)
    y = lambda v: B - v * (B - T) / top
    out = []
    for v in range(0, top + 1, step):
        out.append(f'<line class="grid" x1="{L}" y1="{y(v):.1f}" x2="{R}" y2="{y(v):.1f}"/>')
        out.append(f'<text x="{L-12}" y="{y(v)+5:.1f}" class="serif mut" font-size="14" text-anchor="end">{v}</text>')
    seen = set()
    for i, (d, n) in enumerate(wk):
        x = L + i * slot
        if n:
            out.append(
                f'<rect class="bar" style="animation-delay:{i*0.012:.2f}s" x="{x+1.5:.1f}" y="{y(n):.1f}" width="{slot-3:.1f}" height="{B-y(n):.1f}"/>'
            )
        month = d[:7]
        if month not in seen and date.fromisoformat(d).day <= 7:
            seen.add(month)
            out.append(f'<line class="sk" x1="{x:.1f}" y1="{B}" x2="{x:.1f}" y2="{B+6}"/>')
            out.append(
                f'<text x="{x:.1f}" y="{B+26}" class="serif mut" font-size="13" text-anchor="middle">{date.fromisoformat(d).strftime("%b")}</text>'
            )
    today = date.today().strftime("%d %B %Y").lstrip("0")
    summary = f"{s['total']:,} contributions · {s['active']} active days · longest run {s['longest']} days"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">Figure 4. Weekly public GitHub contributions for {USER} over the last 12 months: {summary}.</title>
  <style>
    .paper {{ fill:#f6f1e7; }} .edge {{ fill:none; stroke:#e2d9c6; stroke-width:1; }}
    .serif {{ font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif; }}
    .mut {{ fill:#6e675b; }} .nav {{ fill:#2d4a73; }}
    .grid {{ stroke:#e4dccb; stroke-width:1; }} .sk {{ stroke:#1c1b19; stroke-width:1.2; fill:none; }}
    .bar {{ fill:#8f2d22; transform-box:fill-box; transform-origin:bottom; transform:scaleY(0); animation: up .7s ease-out forwards; }}
    @keyframes up {{ to {{ transform:scaleY(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .bar {{ animation:none; transform:none; }} }}
  </style>
  <rect class="paper" width="{W}" height="{H}" rx="6"/><rect class="edge" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6"/>
  <text x="40" y="34" class="serif mut" font-size="15" font-style="italic">(d) Weekly public contributions, last 12 months</text>
  <text x="{R}" y="34" class="serif nav" font-size="14" font-style="italic" text-anchor="end">{summary}</text>
  {''.join(out)}
  <line class="sk" x1="{L}" y1="{B}" x2="{R}" y2="{B}"/><line class="sk" x1="{L}" y1="{T}" x2="{L}" y2="{B}"/>
  <text x="{W//2}" y="{H-18}" class="serif mut" font-size="13" font-style="italic" text-anchor="middle">Source: public GitHub contribution calendar · redrawn daily · last updated {today}</text>
</svg>
"""


if __name__ == "__main__":
    OUT.write_text(render(summarise(fetch_days())), encoding="utf-8")
    print("wrote", OUT)
