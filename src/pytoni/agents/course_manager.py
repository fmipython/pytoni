from collections.abc import Callable
from datetime import datetime

from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from pytoni import tools as default_tools
from pytoni.config import get_settings
from pytoni.prompts.course_manager import COURSE_MANAGER_PROMPT

# from agno.tracing import setup_tracing


def create_agent(tools: list[Callable] | None = None, current_date: datetime | None = None) -> Agent:
    settings = get_settings()
    if tools is None:
        tools = [default_tools.fetch_readme, default_tools.get_calendar]
    if current_date is None:
        current_date = datetime.now()

    course_manager = Agent(
        id="course_manager",
        name="Course Manager",
        role="Manage the course timelines and deadlines. Provide information about important dates and deadlines for the course.",
        model=OpenRouter(id=settings.course_manager_model, api_key=settings.openrouter_api_key),
        markdown=True,
        system_message=COURSE_MANAGER_PROMPT.format(
            current_date=current_date.strftime("%Y-%m-%d"),
            current_day_of_week=current_date.strftime("%A"),
        ),
        system_message_role="system",
        tools=tools,
    )

    return course_manager
