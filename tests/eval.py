import argparse
import csv
from datetime import datetime
from pathlib import Path

from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openrouter import OpenRouter
from rich.console import Console
from rich.table import Table

from pytoni.agents.course_manager import create_agent
from pytoni.config import get_settings
from tests.mocks import fetch_readme, get_calendar

DATASET_PATH = Path(__file__).parent / "dataset.csv"
with DATASET_PATH.open(newline="", encoding="utf-8") as f:
    COURSE_MANAGER_DATASET = [(row["question"], row["expected_answer"] or None) for row in csv.DictReader(f)]

parser = argparse.ArgumentParser()
parser.add_argument(
    "--verbose", action="store_true", help="Show full agent/judge debug output and per-question detail tables"
)
parser.add_argument("--jev", action="store_true", help="Evaluate the Jev can-Pytoni-answer classifier instead")
args = parser.parse_args()

if args.jev:
    from pytoni.agents.jev import is_question_for_pytoni

    with (Path(__file__).parent / "jev_dataset.csv").open(newline="", encoding="utf-8") as f:
        rows = [(r["question"], r["can_answer"] == "true") for r in csv.DictReader(f)]

    correct = 0
    for q, exp in rows:
        result, confidence = is_question_for_pytoni(q)

        is_correct = result == exp
        correct += 1 if is_correct else 0

        emoji = "✅" if is_correct else "❌"

        if args.verbose:
            print(f"{emoji} Question: {q}\nExpected: {exp}, Got: {result} (confidence: {confidence:.2f})\n")
        else:
            print(f"{emoji} Question: {q}\nExpected: {exp}, Got: {result}\n")

    print(f"Jev accuracy: {correct}/{len(rows)}")

    raise SystemExit

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
        agent=track_usage(create_agent(tools=[fetch_readme, get_calendar], current_date=EVAL_DATE), question_usage),
        name=f"Course Manager Accuracy Eval - {question}",
        num_iterations=iterations,
        input=question,
        expected_output=expected_answer,
        additional_guidelines="If the actual answer contains synonyms or paraphrased information that matches the expected answer, consider it correct. Focus on the correctness of the information rather than exact wording.",
        model=OpenRouter(id="openai/gpt-5.6-luna", api_key=get_settings().openrouter_api_key),
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

if summary_rows:

    def bucket(score: float) -> str:
        if score <= 3:
            return "Bad (0-3)"
        if score <= 6:
            return "Okay (4-6)"
        return "Good (7+)"

    counts = {"Bad (0-3)": 0, "Okay (4-6)": 0, "Good (7+)": 0}
    for _, score, _ in summary_rows:
        counts[bucket(score)] += 1

    grouped_table = Table(title="Score Groups")
    grouped_table.add_column("Group")
    grouped_table.add_column("Count", justify="right")
    grouped_table.add_column("%", justify="right")

    for group, count in counts.items():
        grouped_table.add_row(group, str(count), f"{count / len(summary_rows) * 100:.1f}%")

    console.print(grouped_table)

if args.verbose:
    print(f"Messages sent to model: {total_usage['messages']}")
    print(f"Input tokens:  {total_usage['input_tokens']}")
    print(f"Output tokens: {total_usage['output_tokens']}")
    print(f"Total tokens:  {total_usage['input_tokens'] + total_usage['output_tokens']}")
