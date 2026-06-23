from datetime import datetime

from agno.agent import Agent

# from agno.db.sqlite import SqliteDb
from agno.models.openrouter import OpenRouter

# from agno.tracing import setup_tracing

from pytoni.prompts.course_manager import COURSE_MANAGER_PROMPT
import pytoni.tools as tools


def create_agent() -> Agent:

    course_manager = Agent(
        id="course_manager",
        name="Course Manager",
        role="Manage the course timelines and deadlines. Provide information about important dates and deadlines for the course.",
        model=OpenRouter(id="google/gemma-3-12b-it"),
        markdown=True,
        system_message=COURSE_MANAGER_PROMPT.format(
            current_date=datetime.now().strftime("%Y-%m-%d"),
            current_day_of_week=datetime.now().strftime("%A"),
        ),
        system_message_role="system",
        tools=[
            tools.fetch_readme,
            tools.get_calendar,
        ],
        # add_history_to_context=True,
        # num_history_runs=5,
        # db=db,
    )

    return course_manager
