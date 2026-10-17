from datetime import datetime

import requests


def fetch_readme() -> str:
    response = requests.get("https://raw.githubusercontent.com/fmipython/PythonCourse2026/refs/heads/main/README.md")

    if not response:
        return "Failed to fetch README.md from GitHub."

    # GET https://api.github.com/repos/fmipython/PythonCourse2026/commits/{ref}
    return response.text


def fetch_readme_diff():
    hashes = __get_last_commits_hashes()

    patches = [__get_commit_diff(_hash) for _hash in hashes]

    return "\n".join(patches)


def __get_last_commits_hashes() -> list[str]:
    response = requests.get("https://api.github.com/repos/fmipython/PythonCourse2026/commits?path=README.md")

    last_10_commits = [
        (commit["sha"], datetime.fromisoformat(commit["commit"]["author"]["date"])) for commit in response.json()[:10]
    ]
    latest_commits = [
        commit_hash
        for commit_hash, commit_date in last_10_commits
        if commit_date.date() == last_10_commits[0][1].date()
    ]

    return latest_commits


def __get_commit_diff(commit_hash: str) -> str:
    response = requests.get(f"https://api.github.com/repos/fmipython/PythonCourse2026/commits/{commit_hash}")

    patch = next(_file["patch"] for _file in response.json()["files"] if _file["filename"] == "README.md")

    return patch
