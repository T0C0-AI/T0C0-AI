#!/usr/bin/env python3
"""
T0C0 AI — Operator Activity Telemetry Generator

Generates:
  - assets/activity-telemetry.svg  (시간대별 커밋 활동)
  - assets/weekly-activity.svg     (이번 주 활동 리포트)
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
            for c in commits:
                c["_repo_name"] = name.split("/")[-1]
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


def analyze_daily(commits):
    daily = {d: 0 for d in DAY_NAMES_KR}
    for item in commits:
        date_str = item["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        local = dt.astimezone(LOCAL_TZ)
        day_name = DAY_NAMES_KR[local.weekday()]
        daily[day_name] += 1
    return daily


def analyze_repos(commits):
    repo_counts = {}
    for item in commits:
        name = item.get("_repo_name", "unknown")
        repo_counts[name] = repo_counts.get(name, 0) + 1
    return sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)[:3]


# ── SVG: 시간대별 커밋 활동 ────────────────────────────

PERIOD_META = [
    ("dawn",    "\uc0c8\ubcbd", "00:00 - 06:00"),
    ("morning", "\uc544\uce68", "06:00 - 12:00"),
    ("lunch",   "\uc810\uc2ec", "12:00 - 14:00"),
    ("evening", "\uc800\ub141", "14:00 - 18:00"),
    ("night",   "\ubc24",       "18:00 - 24:00"),
]

FONT = "'Segoe UI', 'Apple SD Gothic Neo', sans-serif"


def generate_time_svg(periods, total):
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
        font-family="{FONT}" font-size="12">\ucd5c\uadfc 7\uc77c \u00b7 \ucd1d {total}\uac74</text>
  <line x1="20" y1="58" x2="{svg_w - 20}" y2="58" stroke="#21262d" stroke-width="1"/>
{rows_svg}  <text x="{svg_w // 2}" y="{svg_h - 10}" text-anchor="middle" fill="#484f58"
        font-family="{FONT}" font-size="10">{now_kst}</text>
</svg>'''


# ── SVG: 이번 주 활동 리포트 ────────────────────────────

def generate_weekly_svg(daily, repo_ranking, total):
    now_kst = datetime.now(LOCAL_TZ)
    now_str = now_kst.strftime("%Y-%m-%d %H:%M KST")

    week_end = now_kst
    week_start = week_end - timedelta(days=6)
    range_str = (
        f"{week_start.month}/{week_start.day} ({DAY_NAMES_KR[week_start.weekday()]}) "
        f"\u2014 {week_end.month}/{week_end.day} ({DAY_NAMES_KR[week_end.weekday()]})"
    )

    active_days = sum(1 for v in daily.values() if v > 0)
    busiest_day = max(daily, key=daily.get) if total > 0 else "-"

    max_daily = max(daily.values()) if any(daily.values()) else 1
    max_repo = repo_ranking[0][1] if repo_ranking else 1

    svg_w = 480
    bar_max_w = 250
    bar_x = 120

    # Layout
    top_pad = 68
    daily_row_h = 34
    daily_section_h = 7 * daily_row_h
    divider_y = top_pad + daily_section_h + 10
    repo_header_y = divider_y + 22
    repo_row_h = 30
    repo_section_h = len(repo_ranking) * repo_row_h if repo_ranking else 30
    summary_y = repo_header_y + repo_section_h + 25
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

    # ── Divider ──
    daily_svg += (
        f'  <line x1="20" y1="{divider_y}" x2="{svg_w - 20}" y2="{divider_y}" '
        f'stroke="#21262d" stroke-width="1"/>\n'
    )

    # ── Repo section header ──
    daily_svg += (
        f'  <text x="30" y="{repo_header_y}" fill="#8b949e" '
        f'font-family="{FONT}" font-size="12" font-weight="bold">\uc9d1\uc911 \ub808\ud3ec</text>\n'
    )

    # ── Repo bars ──
    medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
    repo_bar_x = 120
    repo_bar_max_w = 230

    for i, (repo_name, count) in enumerate(repo_ranking):
        y = repo_header_y + 8 + i * repo_row_h
        w = round((count / max_repo) * repo_bar_max_w) if max_repo > 0 else 0
        medal = medals[i] if i < len(medals) else "\u25cf"

        daily_svg += (
            f'  <text x="110" y="{y + 17}" text-anchor="end" '
            f'fill="#c9d1d9" font-family="{FONT}" font-size="12">{repo_name}</text>\n'
            f'  <rect x="{repo_bar_x}" y="{y + 2}" width="{repo_bar_max_w}" height="18" fill="#161b22" rx="4"/>\n'
        )
        if w > 0:
            daily_svg += (
                f'  <rect x="{repo_bar_x}" y="{y + 2}" width="{w}" height="18" fill="url(#grad_cyan)" rx="4"/>\n'
            )
        daily_svg += (
            f'  <text x="{repo_bar_x + repo_bar_max_w + 10}" y="{y + 16}" fill="#ffffff" '
            f'font-family="{FONT}" font-size="12" font-weight="bold">{count}</text>\n'
        )

    if not repo_ranking:
        y = repo_header_y + 8
        daily_svg += (
            f'  <text x="{svg_w // 2}" y="{y + 17}" text-anchor="middle" '
            f'fill="#484f58" font-family="{FONT}" font-size="12">\uc774\ubc88 \uc8fc \ucee4\ubc0b \uc5c6\uc74c</text>\n'
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
    <linearGradient id="grad_cyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#0ea5e9"/>
    </linearGradient>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="12"/>
  <text x="{svg_w // 2}" y="28" text-anchor="middle" fill="#ffffff"
        font-family="{FONT}" font-size="17" font-weight="bold"
        filter="url(#glow2)">\uc774\ubc88 \uc8fc \ud65c\ub3d9 \ub9ac\ud3ec\ud2b8</text>
  <text x="{svg_w // 2}" y="48" text-anchor="middle" fill="#8b949e"
        font-family="{FONT}" font-size="12">{range_str}</text>
  <line x1="20" y1="58" x2="{svg_w - 20}" y2="58" stroke="#21262d" stroke-width="1"/>
{daily_svg}  <text x="{svg_w // 2}" y="{svg_h - 10}" text-anchor="middle" fill="#484f58"
        font-family="{FONT}" font-size="10">{now_str}</text>
</svg>'''


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
        f'<picture>\n'
        f'  <img src="./assets/activity-telemetry.svg" width="480" />\n'
        f'</picture>\n'
        f"\n"
        f"<br><br>\n"
        f"\n"
        f'<picture>\n'
        f'  <img src="./assets/weekly-activity.svg" width="480" />\n'
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

    print("[INFO] Fetching commits (last 7 days)...")
    commits = fetch_all_commits(repos, GITHUB_USERNAME, days=7)
    total = len(commits)
    print(f"[INFO] Total: {total} commits")

    periods = analyze_commits(commits)
    daily = analyze_daily(commits)
    repo_ranking = analyze_repos(commits)

    print(
        f"[INFO] Dawn={periods['dawn']} Morning={periods['morning']} "
        f"Lunch={periods['lunch']} Evening={periods['evening']} Night={periods['night']}"
    )
    print(f"[INFO] Daily: {daily}")
    print(f"[INFO] Top repos: {repo_ranking}")

    print("[INFO] Fetching code reviews...")
    reviews = fetch_all_reviews(repos, GITHUB_USERNAME, days=7)
    print(f"[INFO] Reviews: {reviews}")

    time_svg = generate_time_svg(periods, total)
    save_svg(os.path.join(SVG_DIR, "activity-telemetry.svg"), time_svg)

    weekly_svg = generate_weekly_svg(daily, repo_ranking, total)
    save_svg(os.path.join(SVG_DIR, "weekly-activity.svg"), weekly_svg)

    section = generate_section(total, reviews)
    update_readme(section)


if __name__ == "__main__":
    main()
