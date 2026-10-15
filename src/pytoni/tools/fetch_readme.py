from datetime import datetime

import requests


def fetch_readme() -> str:
    response = requests.get(
        "https://raw.githubusercontent.com/fmipython/PythonCourse2026/refs/heads/main/README.md"
    )

    if not response:
        return "Failed to fetch README.md from GitHub."

    # GET https://api.github.com/repos/fmipython/PythonCourse2026/commits/{ref}
    return response.text


def get_last_commits() -> list[dict[str, datetime]]:
    response = requests.get(
        "https://api.github.com/repos/fmipython/PythonCourse2026/commits?path=README.md"
    )

    commits = [
        (commit["sha"], datetime.fromisoformat(commit["commit"]["author"]["date"]))
        for commit in response.json()[:10]
    ]

    latest_commit_date = commits[0][1]

    print(commits)

    # return commits


if __name__ == "__main__":
    print(get_last_commits())
    # print(fetch_readme())
