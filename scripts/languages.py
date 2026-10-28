"""Regenerate the language charts in assets/.

Counts bytes per language across every repo you own, private included, which is
why this runs locally instead of pulling a public stats card. Requires a GitHub
token with repo scope:

    set GITHUB_TOKEN=...  &&  python scripts/languages.py
"""
import json, os, urllib.request

TOKEN = os.environ["GITHUB_TOKEN"]
USER = "dutaalamin"

LABEL = {"Blade": "Blade (Laravel)", "Jupyter Notebook": "Jupyter"}
COLOR = {"Blade": "#F7523F", "JavaScript": "#F1E05A", "HTML": "#E34C26", "PHP": "#4F5D95",
         "TypeScript": "#3178C6", "Jupyter Notebook": "#DA5B0B", "CSS": "#563D7C",
         "Dart": "#00B4AB", "C++": "#f34b7d", "Python": "#3572A5", "Vue": "#41b883"}


def api(url):
    req = urllib.request.Request(url, headers={"Authorization": "token " + TOKEN})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def collect():
    repos, page = [], 1
    while True:
        batch = api(f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner")
        if not batch:
            break
        repos += batch
        page += 1
        if len(batch) < 100:
            break
    totals = {}
    for r in repos:
        if r["fork"] or r["size"] == 0:
            continue
        for name, size in api(f"https://api.github.com/repos/{USER}/{r['name']}/languages").items():
            totals[name] = totals.get(name, 0) + size
    return totals


def render(rows, fg, track, muted):
    w, row, top = 495, 26, 8
    h = top + row * len(rows) + 4
    label_w, pad = 122, 4
    bar_x = label_w + pad
    bar_max = w - bar_x - 44 - pad
    out, y = [], top
    for name, pct in rows:
        cy = y + 15
        out.append(f'<text x="{pad}" y="{cy}" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="12" fill="{fg}">{LABEL.get(name, name)}</text>')
        bw = max(2, bar_max * pct / 24.0)
        out.append(f'<rect x="{bar_x}" y="{y+8}" width="{bar_max}" height="8" rx="4" fill="{track}"/>')
        out.append(f'<rect x="{bar_x}" y="{y+8}" width="{bw:.1f}" height="8" rx="4" fill="{COLOR.get(name, "#8b949e")}"/>')
        out.append(f'<text x="{w-pad}" y="{cy}" text-anchor="end" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="11" fill="{muted}">{pct:.1f}%</text>')
        y += row
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + "".join(out) + "</svg>")


if __name__ == "__main__":
    totals = collect()
    grand = sum(totals.values())
    rows = [(k, 100 * v / grand) for k, v in sorted(totals.items(), key=lambda x: -x[1])[:7]]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    open(os.path.join(here, "assets", "languages-dark.svg"), "w", encoding="utf8", newline="\n").write(
        render(rows, "#c9d1d9", "#21262D", "#8b949e"))
    open(os.path.join(here, "assets", "languages-light.svg"), "w", encoding="utf8", newline="\n").write(
        render(rows, "#24292f", "#eaeef2", "#57606a"))
    for k, p in rows:
        print(f"{k:18} {p:5.1f}%")
