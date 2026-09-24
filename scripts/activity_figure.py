"""Draw assets/fig-4-activity.svg from the public GitHub contribution calendar.

Weekly contribution totals as a bar chart, in the same palette and type as the rest
of the README (see brand.py). No token needed: github.com/users/<user>/contributions
is public. A GitHub Action runs this daily.
"""
import re
import sys
import urllib.request
from collections import OrderedDict
from datetime import date
from pathlib import Path

from brand import INK, INK2, LINE, SURFACE, TONES, font_css

USER = "suryatenz"
OUT = Path(__file__).resolve().parent.parent / "assets" / "fig-4-activity.svg"
W, H = 1200, 500
L, R, T, B = 100, 1140, 176, 412


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


def text(x, y, s, face="body", size=15, fill=INK2, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="f-{face}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


def render(s):
    base, tint, dark = TONES["butter"]
    cobalt = TONES["cobalt"][0]
    wk = s["weeks"]
    top, step = nice_max(max(n for _, n in wk) or 1)
    slot = (R - L) / len(wk)
    y = lambda v: B - v * (B - T) / top
    out = []
    for v in range(0, top + 1, step):
        out.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{R}" y2="{y(v):.1f}" stroke="{LINE}" stroke-width="1"/>')
        out.append(text(L - 14, f"{y(v)+5:.1f}", v, anchor="end", size=14))
    seen = set()
    for i, (d, n) in enumerate(wk):
        x = L + i * slot
        if n:
            out.append(
                f'<rect class="bar" style="animation-delay:{i*0.012:.2f}s" x="{x+2:.1f}" y="{y(n):.1f}" '
                f'width="{slot-4:.1f}" height="{B-y(n):.1f}" rx="3" fill="{cobalt}"/>'
            )
        day = date.fromisoformat(d)
        if d[:7] not in seen and day.day <= 7:
            seen.add(d[:7])
            out.append(text(f"{x:.1f}", B + 28, day.strftime("%b"), anchor="middle", size=14))
    summary = f"{s['total']:,} contributions · {s['active']} active days · longest run {s['longest']} days"
    today = date.today().strftime("%d %B %Y").lstrip("0")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">Figure 4. Weekly public GitHub contributions for {USER} over the last 12 months: {summary}.</title>
  <style>
    {font_css("display", "body", "body-m")}
    .bar {{ transform-box:fill-box; transform-origin:bottom; transform:scaleY(0); animation: up .8s cubic-bezier(.2,.7,.2,1) forwards; }}
    @keyframes up {{ to {{ transform:scaleY(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .bar {{ animation:none; transform:none; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="28" fill="{tint}"/>
  <circle cx="46" cy="44" r="5" fill="{base}"/>
  {text(60, 49, "FIGURE 4 · ACTIVITY", "display", 13, dark, extra='letter-spacing="1.6"')}
  {text(40, 98, "Last 12 months", "display", 44, INK, extra='letter-spacing="-1.6"')}
  {text(W-40, 98, summary, "body", 17, dark, "end")}
  <rect x="24" y="128" width="{W-48}" height="{H-152}" rx="20" fill="{SURFACE}"/>
  {text(L, 162, "weekly public contributions", "body-m", 15, INK2)}
  {text(R, 162, f"redrawn daily · updated {today}", "body", 14, INK2, "end")}
  {''.join(out)}
</svg>
"""


if __name__ == "__main__":
    OUT.write_text(render(summarise(fetch_days())), encoding="utf-8")
    print("wrote", OUT)
