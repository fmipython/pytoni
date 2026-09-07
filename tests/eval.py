import argparse
from datetime import datetime

import dotenv
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openrouter import OpenRouter
from rich.console import Console
from rich.table import Table

from pytoni.agents.course_manager import create_agent
from tests.dataset import COURSE_MANAGER_DATASET
from tests.mocks import fetch_readme, get_calendar

dotenv.load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--verbose", action="store_true", help="Show full agent/judge debug output and per-question detail tables"
)
args = parser.parse_args()

iterations = 1
EVAL_DATE = datetime(2025, 6, 5)  # fixed "current day" so results are reproducible
summary_rows: list[tuple[str, float, float]] = []  # (question, score, cost)
total_usage = {"messages": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def track_usage(agent, bucket):
    """Wrap agent.run so every call adds to `bucket`."""
    original_run = agent.run

    def run(*args, **kwargs):
        response = original_run(*args, **kwargs)
        bucket["messages"] += len(response.messages or [])
        if response.metrics:
            bucket["input_tokens"] += response.metrics.input_tokens
            bucket["output_tokens"] += response.metrics.output_tokens
            bucket["cost"] += response.metrics.cost or 0.0
        return response

    agent.run = run
    return agent


for question, expected_answer in COURSE_MANAGER_DATASET:
    if expected_answer is None:
        if args.verbose:
            print(f"Skipping question: '{question}' (no expected answer provided)")
        continue

    question_usage = {"messages": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}

    evaluation = AccuracyEval(
        agent=track_usage(
            create_agent(tools=[fetch_readme, get_calendar], current_date=EVAL_DATE), question_usage
        ),
        name=f"Course Manager Accuracy Eval - {question}",
        num_iterations=iterations,
        input=question,
        expected_output=expected_answer,
        additional_guidelines="If the actual answer contains synonyms or paraphrased information that matches the expected answer, consider it correct. Focus on the correctness of the information rather than exact wording.",
        model=OpenRouter(id="openai/gpt-5.2"),
    )

    result: AccuracyResult | None = evaluation.run(print_results=args.verbose, print_summary=args.verbose)

    summary_rows.append((question, result.avg_score, question_usage["cost"]))
    for key in total_usage:
        total_usage[key] += question_usage[key]

console = Console()
table = Table(title="Evaluation Summary")
table.add_column("Question")
table.add_column("Score", justify="right")
table.add_column("Cost ($)", justify="right")

for question, score, cost in summary_rows:
    table.add_row(question, f"{score:.1f}", f"{cost:.6f}")

if summary_rows:
    avg_score = sum(score for _, score, _ in summary_rows) / len(summary_rows)
    table.add_section()
    table.add_row("TOTAL / AVERAGE", f"{avg_score:.2f}", f"{total_usage['cost']:.6f}")

console.print(table)

if args.verbose:
    print(f"Messages sent to model: {total_usage['messages']}")
    print(f"Input tokens:  {total_usage['input_tokens']}")
    print(f"Output tokens: {total_usage['output_tokens']}")
    print(f"Total tokens:  {total_usage['input_tokens'] + total_usage['output_tokens']}")
