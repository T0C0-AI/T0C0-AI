#!/usr/bin/env python3
"""
T0C0 AI — Operator Activity Telemetry Generator

Fetches GitHub activity data and generates a telemetry section for README.md.
Runs in GitHub Actions on a daily schedule.

Metrics:
  - Weekly commit count (Search Commits API)
  - Time-of-day commit distribution (KST)
  - Code review count (Search Issues API)
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import quote

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "T0C0-AI")
README_PATH = os.environ.get("README_PATH", "README.md")
UTC_OFFSET = int(os.environ.get("UTC_OFFSET", "9"))

START_MARKER = "<!-- ACTIVITY-TELEMETRY:START -->"
END_MARKER = "<!-- ACTIVITY-TELEMETRY:END -->"

LOCAL_TZ = timezone(timedelta(hours=UTC_OFFSET))


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


def fetch_commits(username, days=7):
    """Fetch commits via GitHub Search Commits API."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    commits = []
    for page in range(1, 11):  # max 1000 results (10 pages x 100)
        q = quote(f"author:{username} committer-date:>={since}")
        url = (
            f"https://api.github.com/search/commits"
            f"?q={q}&sort=committer-date&per_page=100&page={page}"
        )
        data = github_api(url)
        if not data or "items" not in data:
            break
        commits.extend(data["items"])
        if len(data["items"]) < 100:
            break
    return commits


def fetch_reviews(username, days=7):
    """Fetch PR review count via GitHub Search Issues API."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    q = quote(f"type:pr reviewed-by:{username} updated:>={since}")
    url = f"https://api.github.com/search/issues?q={q}&per_page=1"
    data = github_api(url)
    if data and "total_count" in data:
        return data["total_count"]
    return 0


def analyze_commits(commits):
    """Categorize commits by time of day (local timezone)."""
    periods = {"dawn": 0, "morning": 0, "afternoon": 0, "night": 0}

    for item in commits:
        date_str = item["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        local_hour = dt.astimezone(LOCAL_TZ).hour

        if local_hour < 6:
            periods["dawn"] += 1
        elif local_hour < 12:
            periods["morning"] += 1
        elif local_hour < 18:
            periods["afternoon"] += 1
        else:
            periods["night"] += 1

    return periods


def make_bar(count, max_val, width=15):
    if max_val == 0:
        return "\u2591" * width
    filled = round((count / max_val) * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def generate_section(periods, total, reviews):
    max_val = max(periods.values()) if any(periods.values()) else 1

    rows = [
        ("\U0001f30c", "\uc0c8\ubcbd", "00-06", periods["dawn"]),
        ("\U0001f305", "\uc544\uce68", "06-12", periods["morning"]),
        ("\U0001f307", "\uc800\ub141", "12-18", periods["afternoon"]),
        ("\U0001f319", "\ubc24", "18-24", periods["night"]),
    ]

    table_rows = ""
    for emoji, name, hours, count in rows:
        bar = make_bar(count, max_val)
        table_rows += (
            f"  <tr>\n"
            f"    <td>{emoji} {name} ({hours})</td>\n"
            f"    <td><code>{bar}</code></td>\n"
            f"    <td><b>{count}</b></td>\n"
            f"  </tr>\n"
        )

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

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
        f'<img src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username={GITHUB_USERNAME}&theme=nord_dark&utcOffset={UTC_OFFSET}" height="180" />\n'
        f"\n"
        f"<br><br>\n"
        f"\n"
        f"<table>\n"
        f"  <tr>\n"
        f"    <th>\uc2dc\uac04\ub300</th>\n"
        f"    <th>\ud65c\ub3d9 \ubd84\ud3ec</th>\n"
        f"    <th>\ucee4\ubc0b</th>\n"
        f"  </tr>\n"
        f"{table_rows}"
        f"</table>\n"
        f"\n"
        f"<br>\n"
        f"\n"
        f"<sub>\ub9c8\uc9c0\ub9c9 \uac31\uc2e0: {now_utc} \u00b7 GitHub Actions \uc790\ub3d9 \uc0dd\uc131</sub>\n"
        f"\n"
        f"</div>\n"
        f"\n"
        f"{END_MARKER}"
    )


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
        print("[INFO] No changes \u2014 skipping write.")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("[INFO] README.md updated.")


def main():
    print(f"[INFO] Fetching commits for {GITHUB_USERNAME} (last 7 days)...")
    commits = fetch_commits(GITHUB_USERNAME, days=7)
    total = len(commits)
    print(f"[INFO] Found {total} commits")

    periods = analyze_commits(commits)
    print(
        f"[INFO] Dawn={periods['dawn']} Morning={periods['morning']} "
        f"Afternoon={periods['afternoon']} Night={periods['night']}"
    )

    print(f"[INFO] Fetching code reviews...")
    reviews = fetch_reviews(GITHUB_USERNAME, days=7)
    print(f"[INFO] Reviews: {reviews}")

    section = generate_section(periods, total, reviews)
    update_readme(section)


if __name__ == "__main__":
    main()
