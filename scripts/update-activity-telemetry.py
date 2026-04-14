#!/usr/bin/env python3
"""
T0C0 AI — Operator Activity Telemetry Generator

Fetches GitHub activity data and generates:
  - Custom SVG bar chart (assets/activity-telemetry.svg)
  - README telemetry section with badges + chart

Runs in GitHub Actions on a daily schedule.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "T0C0-AI")
README_PATH = os.environ.get("README_PATH", "README.md")
SVG_PATH = os.environ.get("SVG_PATH", "assets/activity-telemetry.svg")
UTC_OFFSET = int(os.environ.get("UTC_OFFSET", "9"))

START_MARKER = "<!-- ACTIVITY-TELEMETRY:START -->"
END_MARKER = "<!-- ACTIVITY-TELEMETRY:END -->"

LOCAL_TZ = timezone(timedelta(hours=UTC_OFFSET))


# ── GitHub API ──────────────────────────────────────────

def github_api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"[WARN] GitHub API {e.code}: {url}", file=sys.stderr)
        return None


def github_api_paginate(url_template, per_page=100, max_pages=10):
    all_items = []
    for page in range(1, max_pages + 1):
        sep = "&" if "?" in url_template else "?"
        url = f"{url_template}{sep}per_page={per_page}&page={page}"
        data = github_api(url)
        if not data or not isinstance(data, list):
            break
        all_items.extend(data)
        if len(data) < per_page:
            break
    return all_items


def fetch_repos(username):
    repos = github_api_paginate(
        "https://api.github.com/user/repos?affiliation=owner&sort=pushed"
    )
    if not repos:
        repos = github_api_paginate(
            f"https://api.github.com/users/{username}/repos?sort=pushed"
        )
    return repos or []


def fetch_all_commits(repos, username, days=7):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    all_commits = []
    for repo in repos:
        name = repo["full_name"]
        url = f"https://api.github.com/repos/{name}/commits?author={username}&since={since}"
        commits = github_api_paginate(url)
        if commits:
            print(f"[INFO]   {name}: {len(commits)} commits")
            all_commits.extend(commits)
    return all_commits


def fetch_all_reviews(repos, username, days=7):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    total = 0
    for repo in repos:
        name = repo["full_name"]
        prs = github_api_paginate(
            f"https://api.github.com/repos/{name}/pulls?state=all&sort=updated&direction=desc",
            max_pages=2,
        )
        if not prs:
            continue
        for pr in prs:
            updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
            if updated < since:
                break
            reviews = github_api(
                f"https://api.github.com/repos/{name}/pulls/{pr['number']}/reviews"
            )
            if reviews:
                for r in reviews:
                    if r.get("user", {}).get("login") == username and r.get("submitted_at"):
                        rd = datetime.fromisoformat(r["submitted_at"].replace("Z", "+00:00"))
                        if rd >= since:
                            total += 1
    return total


# ── Analysis ────────────────────────────────────────────

def analyze_commits(commits):
    periods = {"dawn": 0, "morning": 0, "lunch": 0, "evening": 0, "night": 0}
    for item in commits:
        date_str = item["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        h = dt.astimezone(LOCAL_TZ).hour
        if h < 6:
            periods["dawn"] += 1
        elif h < 12:
            periods["morning"] += 1
        elif h < 14:
            periods["lunch"] += 1
        elif h < 18:
            periods["evening"] += 1
        else:
            periods["night"] += 1
    return periods


# ── SVG Chart Generation ───────────────────────────────

PERIOD_META = [
    ("dawn",    "\uc0c8\ubcbd", "00:00 - 06:00"),
    ("morning", "\uc544\uce68", "06:00 - 12:00"),
    ("lunch",   "\uc810\uc2ec", "12:00 - 14:00"),
    ("evening", "\uc800\ub141", "14:00 - 18:00"),
    ("night",   "\ubc24",       "18:00 - 24:00"),
]


def generate_svg(periods, total):
    max_val = max(periods.values()) if any(periods.values()) else 1
    now_kst = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M KST")

    bar_max_w = 260
    row_h = 44
    top_pad = 70
    left_label = 110
    bar_x = 120
    svg_w = 480
    svg_h = top_pad + len(PERIOD_META) * row_h + 35

    rows_svg = ""
    for i, (key, label, hours) in enumerate(PERIOD_META):
        count = periods[key]
        y = top_pad + i * row_h
        w = round((count / max_val) * bar_max_w) if max_val > 0 and count > 0 else 0

        # Label
        rows_svg += (
            f'  <text x="{left_label}" y="{y + 18}" text-anchor="end" '
            f'fill="#c9d1d9" font-family="\'Segoe UI\', sans-serif" font-size="13">'
            f'{label}</text>\n'
        )
        rows_svg += (
            f'  <text x="{left_label}" y="{y + 32}" text-anchor="end" '
            f'fill="#484f58" font-family="\'Segoe UI\', sans-serif" font-size="10">'
            f'{hours}</text>\n'
        )

        # Background track
        rows_svg += (
            f'  <rect x="{bar_x}" y="{y + 4}" width="{bar_max_w}" height="24" '
            f'fill="#161b22" rx="6"/>\n'
        )

        # Filled bar
        if w > 0:
            rows_svg += (
                f'  <rect x="{bar_x}" y="{y + 4}" width="{w}" height="24" '
                f'fill="url(#grad)" rx="6"/>\n'
            )

        # Count
        count_x = bar_x + bar_max_w + 12
        rows_svg += (
            f'  <text x="{count_x}" y="{y + 22}" fill="#ffffff" '
            f'font-family="\'Segoe UI\', sans-serif" font-size="14" font-weight="bold">'
            f'{count}</text>\n'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#bd00ff"/>
      <stop offset="100%" stop-color="#ff0080"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="12"/>

  <text x="{svg_w // 2}" y="28" text-anchor="middle" fill="#ffffff"
        font-family="'Segoe UI', sans-serif" font-size="17" font-weight="bold"
        filter="url(#glow)">\ucee4\ubc0b \ud65c\ub3d9 \uc2dc\uac04\ub300 (KST)</text>

  <text x="{svg_w // 2}" y="48" text-anchor="middle" fill="#8b949e"
        font-family="'Segoe UI', sans-serif" font-size="12">\ucd5c\uadfc 7\uc77c \u00b7 \ucd1d {total}\uac74</text>

  <line x1="20" y1="58" x2="{svg_w - 20}" y2="58" stroke="#21262d" stroke-width="1"/>

{rows_svg}
  <text x="{svg_w // 2}" y="{svg_h - 10}" text-anchor="middle" fill="#484f58"
        font-family="'Segoe UI', sans-serif" font-size="10">{now_kst}</text>
</svg>'''

    return svg


# ── README Section Generation ──────────────────────────

def generate_section(total, reviews):
    now_kst = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M KST")

    return (
        f"{START_MARKER}\n"
        f"\n"
        f'<div align="center">\n'
        f"\n"
        f"<h3>\U0001f550 \uc2dc\uac04\ub300\ubcc4 \ucee4\ubc0b \ud65c\ub3d9</h3>\n"
        f"\n"
        f'<img src="https://img.shields.io/badge/%EC%A3%BC%EA%B0%84_%EC%BB%A4%EB%B0%8B-{total}-bd00ff?style=for-the-badge&logo=github&logoColor=white" />\n'
        f'<img src="https://img.shields.io/badge/%EC%BD%94%EB%93%9C_%EB%A6%AC%EB%B7%B0-{reviews}-06b6d4?style=for-the-badge&logo=codereview&logoColor=white" />\n'
        f"\n"
        f"<br><br>\n"
        f"\n"
        f'<img src="assets/activity-telemetry.svg" width="480" />\n'
        f"\n"
        f"<br>\n"
        f"\n"
        f"<sub>\ub9c8\uc9c0\ub9c9 \uac31\uc2e0: {now_kst} \u00b7 GitHub Actions \uc790\ub3d9 \uc0dd\uc131</sub>\n"
        f"\n"
        f"</div>\n"
        f"\n"
        f"{END_MARKER}"
    )


# ── File Updates ───────────────────────────────────────

def save_svg(svg_content):
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[INFO] SVG saved: {SVG_PATH}")


def update_readme(section):
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    if pattern.search(readme):
        new_readme = pattern.sub(section, readme)
    else:
        print(f"[ERROR] Markers not found in {README_PATH}", file=sys.stderr)
        sys.exit(1)

    if new_readme == readme:
        print("[INFO] README.md \u2014 no changes.")
    else:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("[INFO] README.md updated.")


# ── Main ───────────────────────────────────────────────

def main():
    print(f"[INFO] Fetching repos for {GITHUB_USERNAME}...")
    repos = fetch_repos(GITHUB_USERNAME)
    print(f"[INFO] Found {len(repos)} repos")

    print("[INFO] Fetching commits (last 7 days)...")
    commits = fetch_all_commits(repos, GITHUB_USERNAME, days=7)
    total = len(commits)
    print(f"[INFO] Total: {total} commits")

    periods = analyze_commits(commits)
    print(
        f"[INFO] Dawn={periods['dawn']} Morning={periods['morning']} "
        f"Lunch={periods['lunch']} Evening={periods['evening']} Night={periods['night']}"
    )

    print("[INFO] Fetching code reviews...")
    reviews = fetch_all_reviews(repos, GITHUB_USERNAME, days=7)
    print(f"[INFO] Reviews: {reviews}")

    svg = generate_svg(periods, total)
    save_svg(svg)

    section = generate_section(total, reviews)
    update_readme(section)


if __name__ == "__main__":
    main()
