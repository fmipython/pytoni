import requests


def fetch_readme() -> str:
    response = requests.get("https://raw.githubusercontent.com/fmipython/PythonCourse2026/refs/heads/main/README.md")

    if not response:
        return "Failed to fetch README.md from GitHub."

    return response.text
