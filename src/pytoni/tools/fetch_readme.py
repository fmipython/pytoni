def fetch_readme() -> str:
    with open("COURSE_README.md", "r") as f:
        return f.read()
