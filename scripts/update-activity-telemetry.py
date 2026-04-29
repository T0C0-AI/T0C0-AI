#!/usr/bin/env python3
"""
T0C0 AI — Operator Activity Telemetry Generator

Generates:
  - assets/activity-telemetry.svg  (시간대별 커밋 활동)
  - assets/overall-activity.svg    (전체 활동 리포트)
  - README telemetry section

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
SVG_DIR = os.environ.get("SVG_DIR", "assets")
UTC_OFFSET = int(os.environ.get("UTC_OFFSET", "9"))

START_MARKER = "<!-- ACTIVITY-TELEMETRY:START -->"
END_MARKER = "<!-- ACTIVITY-TELEMETRY:END -->"

LOCAL_TZ = timezone(timedelta(hours=UTC_OFFSET))
DAY_NAMES_KR = ["\uc6d4", "\ud654", "\uc218", "\ubaa9", "\uae08", "\ud1a0", "\uc77c"]


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
            body = resp.read().decode()
            if not body:
                return None
            return json.loads(body)
    except (HTTPError, json.JSONDecodeError) as e:
        print(f"[WARN] GitHub API {e}: {url}", file=sys.stderr)
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


def fetch_total_commits(repos, username):
    """Get all-time total commit count via contributors endpoint."""
    total = 0
    for repo in repos:
        name = repo["full_name"]
        contributors = github_api(
            f"https://api.github.com/repos/{name}/contributors?per_page=100"
        )
        if contributors and isinstance(contributors, list):
            for c in contributors:
                if c.get("login") == username:
                    total += c.get("contributions", 0)
                    break
    return total


def format_range_label():
    return "전체 누적"


def fetch_all_commits(repos, username):
    all_commits = []
    for repo in repos:
        name = repo["full_name"]
        url = f"https://api.github.com/repos/{name}/commits?author={username}"
        commits = github_api_paginate(url, max_pages=100)
        if commits:
            for c in commits:
                c["_repo_name"] = name.split("/")[-1]
            print(f"[INFO]   {name}: {len(commits)} commits")
            all_commits.extend(commits)
    return all_commits


def fetch_all_reviews(repos, username):
    total = 0
    for repo in repos:
        name = repo["full_name"]
        prs = github_api_paginate(
            f"https://api.github.com/repos/{name}/pulls?state=all&sort=updated&direction=desc",
            max_pages=20,
        )
        if not prs:
            continue
        for pr in prs:
            reviews = github_api(
                f"https://api.github.com/repos/{name}/pulls/{pr['number']}/reviews"
            )
            if reviews:
                for r in reviews:
                    if r.get("user", {}).get("login") == username and r.get("submitted_at"):
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


def analyze_daily(commits):
    daily = {d: 0 for d in DAY_NAMES_KR}
    for item in commits:
        date_str = item["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        local = dt.astimezone(LOCAL_TZ)
        day_name = DAY_NAMES_KR[local.weekday()]
        daily[day_name] += 1
    return daily


# ── SVG: 시간대별 커밋 활동 ────────────────────────────

PERIOD_META = [
    ("dawn",    "\uc0c8\ubcbd", "00:00 - 06:00"),
    ("morning", "\uc544\uce68", "06:00 - 12:00"),
    ("lunch",   "\uc810\uc2ec", "12:00 - 14:00"),
    ("evening", "\uc800\ub141", "14:00 - 18:00"),
    ("night",   "\ubc24",       "18:00 - 24:00"),
]

FONT = "'Segoe UI', 'Apple SD Gothic Neo', sans-serif"


def generate_time_svg(periods, total, range_label):
    max_val = max(periods.values()) if any(periods.values()) else 1
    now_kst = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M KST")

    bar_max_w = 260
    row_h = 44
    top_pad = 70
    bar_x = 120
    svg_w = 480
    svg_h = top_pad + len(PERIOD_META) * row_h + 35

    rows_svg = ""
    for i, (key, label, hours) in enumerate(PERIOD_META):
        count = periods[key]
        y = top_pad + i * row_h
        w = round((count / max_val) * bar_max_w) if max_val > 0 and count > 0 else 0

        rows_svg += (
            f'  <text x="110" y="{y + 18}" text-anchor="end" '
            f'fill="#c9d1d9" font-family="{FONT}" font-size="13">{label}</text>\n'
            f'  <text x="110" y="{y + 32}" text-anchor="end" '
            f'fill="#484f58" font-family="{FONT}" font-size="10">{hours}</text>\n'
            f'  <rect x="{bar_x}" y="{y + 4}" width="{bar_max_w}" height="24" fill="#161b22" rx="6"/>\n'
        )
        if w > 0:
            rows_svg += (
                f'  <rect x="{bar_x}" y="{y + 4}" width="{w}" height="24" fill="url(#grad)" rx="6"/>\n'
            )
        rows_svg += (
            f'  <text x="{bar_x + bar_max_w + 12}" y="{y + 22}" fill="#ffffff" '
            f'font-family="{FONT}" font-size="14" font-weight="bold">{count}</text>\n'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#bd00ff"/><stop offset="100%" stop-color="#ff0080"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="12"/>
  <text x="{svg_w // 2}" y="28" text-anchor="middle" fill="#ffffff"
        font-family="{FONT}" font-size="17" font-weight="bold"
        filter="url(#glow)">\ucee4\ubc0b \ud65c\ub3d9 \uc2dc\uac04\ub300 (KST)</text>
  <text x="{svg_w // 2}" y="48" text-anchor="middle" fill="#8b949e"
        font-family="{FONT}" font-size="12">{range_label} \u00b7 \ucd1d {total}\uac74</text>
  <line x1="20" y1="58" x2="{svg_w - 20}" y2="58" stroke="#21262d" stroke-width="1"/>
{rows_svg}  <text x="{svg_w // 2}" y="{svg_h - 10}" text-anchor="middle" fill="#484f58"
        font-family="{FONT}" font-size="10">{now_kst}</text>
</svg>'''


# ── SVG: 전체 활동 리포트 ──────────────────────────────

def generate_overall_svg(daily, total, range_label):
    now_kst = datetime.now(LOCAL_TZ)
    now_str = now_kst.strftime("%Y-%m-%d %H:%M KST")

    active_days = sum(1 for v in daily.values() if v > 0)
    busiest_day = max(daily, key=daily.get) if total > 0 else "-"

    max_daily = max(daily.values()) if any(daily.values()) else 1

    svg_w = 480
    bar_max_w = 250
    bar_x = 120

    # Layout
    top_pad = 68
    daily_row_h = 34
    daily_section_h = 7 * daily_row_h
    summary_y = top_pad + daily_section_h + 28
    svg_h = summary_y + 35

    # ── Daily bars ──
    daily_svg = ""
    for i, day in enumerate(DAY_NAMES_KR):
        count = daily[day]
        y = top_pad + i * daily_row_h
        w = round((count / max_daily) * bar_max_w) if max_daily > 0 and count > 0 else 0

        daily_svg += (
            f'  <text x="110" y="{y + 20}" text-anchor="end" '
            f'fill="#c9d1d9" font-family="{FONT}" font-size="14">{day}</text>\n'
            f'  <rect x="{bar_x}" y="{y + 4}" width="{bar_max_w}" height="22" fill="#161b22" rx="5"/>\n'
        )
        if w > 0:
            daily_svg += (
                f'  <rect x="{bar_x}" y="{y + 4}" width="{w}" height="22" fill="url(#grad_weekly)" rx="5"/>\n'
            )
        daily_svg += (
            f'  <text x="{bar_x + bar_max_w + 12}" y="{y + 20}" fill="#ffffff" '
            f'font-family="{FONT}" font-size="13" font-weight="bold">{count}</text>\n'
        )

    # ── Summary line ──
    daily_svg += (
        f'  <text x="{svg_w // 2}" y="{summary_y}" text-anchor="middle" '
        f'fill="#8b949e" font-family="{FONT}" font-size="11">'
        f'\ud65c\ub3d9\uc77c {active_days}/7  \u00b7  '
        f'\uac00\uc7a5 \ud65c\ubc1c: {busiest_day}\uc694\uc77c  \u00b7  '
        f'\ucd1d {total}\uac74</text>\n'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}">
  <defs>
    <linearGradient id="grad_weekly" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#bd00ff"/><stop offset="100%" stop-color="#ff0080"/>
    </linearGradient>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="12"/>
  <text x="{svg_w // 2}" y="28" text-anchor="middle" fill="#ffffff"
        font-family="{FONT}" font-size="17" font-weight="bold"
        filter="url(#glow2)">\uc804\uccb4 \ud65c\ub3d9 \ub9ac\ud3ec\ud2b8</text>
  <text x="{svg_w // 2}" y="48" text-anchor="middle" fill="#8b949e"
        font-family="{FONT}" font-size="12">{range_label}</text>
  <line x1="20" y1="58" x2="{svg_w - 20}" y2="58" stroke="#21262d" stroke-width="1"/>
{daily_svg}  <text x="{svg_w // 2}" y="{svg_h - 10}" text-anchor="middle" fill="#484f58"
        font-family="{FONT}" font-size="10">{now_str}</text>
</svg>'''


# ── README Section Generation ──────────────────────────

def generate_section(total, reviews, total_all_time, range_label):
    now_kst = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M KST")

    return (
        f"{START_MARKER}\n"
        f"\n"
        f'<div align="center">\n'
        f"\n"
        f"<h3>\U0001f550 \uc2dc\uac04\ub300\ubcc4 \ucee4\ubc0b \ud65c\ub3d9</h3>\n"
        f"<sub>{range_label}</sub>\n"
        f"\n"
        f'<img src="https://img.shields.io/badge/%EC%A0%84%EC%B2%B4_%EC%BB%A4%EB%B0%8B-{total_all_time:,}-ffffff?style=for-the-badge&logo=git&logoColor=white" />\n'
        f'<img src="https://img.shields.io/badge/%EB%88%84%EC%A0%81_%EC%BB%A4%EB%B0%8B-{total}-bd00ff?style=for-the-badge&logo=github&logoColor=white" />\n'
        f'<img src="https://img.shields.io/badge/%EC%BD%94%EB%93%9C_%EB%A6%AC%EB%B7%B0-{reviews}-06b6d4?style=for-the-badge&logo=codereview&logoColor=white" />\n'
        f"\n"
        f"<br><br>\n"
        f"\n"
        f'<picture>\n'
        f'  <img src="./assets/activity-telemetry.svg" width="480" />\n'
        f'</picture>\n'
        f"\n"
        f"<br><br>\n"
        f"\n"
        f'<picture>\n'
        f'  <img src="./assets/overall-activity.svg" width="480" />\n'
        f'</picture>\n'
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

def save_svg(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] SVG saved: {path}")


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

    range_label = format_range_label()

    print("[INFO] Fetching all-time commits...")
    commits = fetch_all_commits(repos, GITHUB_USERNAME)
    total = len(commits)
    print(f"[INFO] Total: {total} commits")

    periods = analyze_commits(commits)
    daily = analyze_daily(commits)

    print(
        f"[INFO] Dawn={periods['dawn']} Morning={periods['morning']} "
        f"Lunch={periods['lunch']} Evening={periods['evening']} Night={periods['night']}"
    )
    print(f"[INFO] Daily: {daily}")

    print("[INFO] Fetching total all-time commits...")
    total_all_time = fetch_total_commits(repos, GITHUB_USERNAME)
    print(f"[INFO] All-time: {total_all_time} commits")

    print("[INFO] Fetching code reviews...")
    reviews = fetch_all_reviews(repos, GITHUB_USERNAME)
    print(f"[INFO] Reviews: {reviews}")

    time_svg = generate_time_svg(periods, total, range_label)
    save_svg(os.path.join(SVG_DIR, "activity-telemetry.svg"), time_svg)

    overall_svg = generate_overall_svg(daily, total, range_label)
    save_svg(os.path.join(SVG_DIR, "overall-activity.svg"), overall_svg)

    section = generate_section(total, reviews, total_all_time, range_label)
    update_readme(section)


if __name__ == "__main__":
    main()
