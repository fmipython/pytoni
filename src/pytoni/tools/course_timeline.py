import subprocess


def get_calendar() -> str:
    """
    Fetches the calendar of the course, containing all dates relevant to the course.
    Lecture days, homework and project deadlines.
    """
    result = subprocess.run(
        ["uv", "run", "main.py", "get-calendar"],
        check=True,
        cwd="/Users/lyuboslav.karev/fmipython/course-db",
        capture_output=True,
    )

    return result.stdout.decode("utf-8").strip()
