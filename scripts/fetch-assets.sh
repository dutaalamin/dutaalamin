#!/usr/bin/env bash
# fetch-assets.sh - download semua gambar profil ke folder assets/
# supaya README nggak fetch dari server luar (cegah 504).
set -u
U="${GITHUB_USER:-dutaalamin}"
OUT="assets"
mkdir -p "$OUT"

dl() {
  local name="$1"; local url="$2"
  local min="${3:-400}"
  for i in 1 2 3; do
    if curl -sL --max-time 40 -o "$OUT/$name" "$url"; then
      local sz=$(wc -c < "$OUT/$name")
      # valid: is SVG/GIF/PNG, size >= min, and not an error page
      if head -c 120 "$OUT/$name" | grep -qiE "<svg|^<\?xml|GIF8|PNG" \
         && [ "$sz" -ge "$min" ] \
         && ! grep -qiE "Something went wrong|Could not fetch|rate limit|429" "$OUT/$name"; then
        echo "OK  $name ($sz bytes)"
        return 0
      fi
    fi
    echo "retry $name ($i) - invalid/too small"
    sleep 4
  done
  echo "GAGAL $name (dibiarkan pakai versi lama)"
  return 1
}

# stats
dl stats.svg "https://github-readme-stats.vercel.app/api/?username=$U&show_icons=true&include_all_commits=true&count_private=true&theme=react&hide_border=true&bg_color=0D1117&title_color=58A6FF&icon_color=58A6FF"
dl top-langs.svg "https://github-readme-stats.vercel.app/api/top-langs/?username=$U&langs_count=8&layout=compact&theme=react&hide_border=true&bg_color=0D1117&title_color=58A6FF&icon_color=58A6FF"
dl streak.svg "https://github-readme-streak-stats-eight.vercel.app/?user=$U&theme=react&hide_border=true&background=0D1117&ring=58A6FF&fire=58A6FF&currStreakLabel=58A6FF"
# summary cards
dl summary-profile.svg "https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=$U&theme=github_dark"
dl summary-repos.svg "https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=$U&theme=github_dark"
dl summary-commit.svg "https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=$U&theme=github_dark"
dl summary-stats.svg "https://github-profile-summary-cards.vercel.app/api/cards/stats?username=$U&theme=github_dark"
dl summary-prod.svg "https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=$U&theme=github_dark&utcOffset=7"
# badges
dl stars.svg "https://custom-icon-badges.demolab.com/github/stars/$U?color=4CAF50&labelColor=2E7D32&style=for-the-badge&logo=star&logoColor=white"
dl followers.svg "https://custom-icon-badges.demolab.com/github/followers/$U?color=1F6FEB&labelColor=0D419D&style=for-the-badge&logo=person-add&label=Follow&logoColor=white"
dl views.svg "https://komarev.com/ghpvc/?username=$U&style=for-the-badge&color=555555&label=PROFILE+VIEWS"
# pacman
dl pacman-dark.svg "https://raw.githubusercontent.com/$U/$U/output/pacman-contribution-graph-dark.svg"
dl pacman-light.svg "https://raw.githubusercontent.com/$U/$U/output/pacman-contribution-graph.svg"

echo "--- selesai ---"
ls -la "$OUT"
