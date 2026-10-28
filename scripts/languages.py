"""Regenerate the language charts in assets/.

Counts bytes per language across every repo you own, private included, which is
why this runs locally instead of pulling a public stats card. Dependencies,
lockfiles and build output are excluded so the chart reflects written code.

    set GITHUB_TOKEN=...  &&  python scripts/languages.py
"""
import json, os, urllib.request

USER = "dutaalamin"

SKIP = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "composer.lock",
        ".min.js", ".min.css", "node_modules/", "dist/", "build/", "vendor/",
        "coverage/", "playwright-report/", "test-results/", ".next/", ".nuxt/",
        "third_party/", "public/js/", "public/draco/", "public/css/",
        "assets/models/", ".phar", ".zip", ".rar", ".mp3", ".mp4", ".fbx", ".glb",
        "assets/index-")   # Vite/Webpack build bundles carry a content hash

# Whole repos that hold other people's code rather than mine: game builds,
# coursework archives, template collections.
SKIP_REPOS = {"game", "Prak-TPM", "award-winning-website", "praktikum2020",
              "company-profile-templates"}

EXT = {".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".mjs": "JavaScript",
       ".jsx": "JavaScript", ".cjs": "JavaScript", ".vue": "Vue", ".php": "PHP / Laravel",
       ".html": "HTML", ".css": "CSS", ".scss": "CSS", ".sass": "CSS", ".less": "CSS",
       ".py": "Python", ".cpp": "C++", ".cc": "C++", ".h": "C++", ".hpp": "C++", ".c": "C",
       ".dart": "Dart", ".rs": "Rust", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
       ".sh": "Shell", ".swift": "Swift", ".lua": "Lua"}

COLOR = {"PHP / Laravel": "#4F5D95", "JavaScript": "#F1E05A", "HTML": "#E34C26",
         "TypeScript": "#3178C6", "CSS": "#563D7C", "Dart": "#00B4AB", "C++": "#f34b7d",
         "Vue": "#41b883", "Python": "#3572A5"}


def api(url):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(url, headers={"Authorization": "token " + token})
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

    totals, counted = {}, 0
    for repo in repos:
        if repo["fork"] or repo["size"] == 0 or repo["name"] in SKIP_REPOS:
            continue
        try:
            tree = api(f"https://api.github.com/repos/{USER}/{repo['name']}/git/trees/HEAD?recursive=1")
        except Exception:
            continue
        if "tree" not in tree:
            continue
        counted += 1
        for item in tree["tree"]:
            if item["type"] != "blob":
                continue
            low = item["path"].lower()
            if any(k in low for k in SKIP):
                continue
            if low.endswith(".blade.php"):
                totals["PHP / Laravel"] = totals.get("PHP / Laravel", 0) + item.get("size", 0)
                continue
            lang = EXT.get(os.path.splitext(low)[1])
            if lang:
                totals[lang] = totals.get(lang, 0) + item.get("size", 0)
    return totals, counted


def render(rows, counted, fg, muted, dim, track):
    w, row, top, pad = 495, 26, 46, 4
    h = top + row * len(rows) + 8
    bar_x = 112
    bar_max = w - bar_x - 46 - pad
    peak = max(pct for _, pct in rows) * 1.06

    out = [
        f'<text x="{pad}" y="14" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="13" font-weight="600" fill="{fg}">Languages</text>',
        f'<text x="{pad}" y="30" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="10" fill="{dim}">Across {counted} projects, dependencies excluded</text>',
    ]
    y = top
    for name, pct in rows:
        cy = y + 15
        out.append(f'<text x="{pad}" y="{cy}" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="12" fill="{fg}">{name}</text>')
        bw = max(2, bar_max * pct / peak)
        out.append(f'<rect x="{bar_x}" y="{y+8}" width="{bar_max}" height="8" rx="4" fill="{track}"/>')
        out.append(f'<rect x="{bar_x}" y="{y+8}" width="{bw:.1f}" height="8" rx="4" fill="{COLOR.get(name, "#8b949e")}"/>')
        out.append(f'<text x="{w-pad}" y="{cy}" text-anchor="end" font-family="Segoe UI,Ubuntu,Sans-Serif" font-size="11" fill="{muted}">{pct:.1f}%</text>')
        y += row
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + "".join(out) + "</svg>")


if __name__ == "__main__":
    totals, counted = collect()
    grand = sum(totals.values())
    rows = [(k, 100 * v / grand) for k, v in sorted(totals.items(), key=lambda x: -x[1])[:7]]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    open(os.path.join(here, "assets", "languages-chart-dark.svg"), "w", encoding="utf8", newline="\n").write(
        render(rows, counted, "#c9d1d9", "#8b949e", "#6e7681", "#21262D"))
    open(os.path.join(here, "assets", "languages-chart-light.svg"), "w", encoding="utf8", newline="\n").write(
        render(rows, counted, "#24292f", "#57606a", "#6e7781", "#eaeef2"))
    for name, pct in rows:
        print(f"{name:16} {pct:5.1f}%")
