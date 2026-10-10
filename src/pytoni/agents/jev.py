import json
import os

import requests
from dotenv import load_dotenv

from pytoni.prompts.jev import CATEGORIES, JEV_PROMPT, PYTONI_CAN_DO, PYTONI_CANNOT_DO

load_dotenv()  # Load environment variables from .env file


def ask(user_question: str, threshold: float = 0.7) -> tuple[str, float]:
    response = requests.post(
        url="https://openrouter.ai/api/alpha/decisions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": "typesafe/jev-1.13",
                "state": user_question,
                "questions": {
                    "can_answer": {
                        "type": "choice",
                        "instructions": JEV_PROMPT,
                        "criteria": CATEGORIES,
                    }
                },
            }
        ),
    )

    if "answers" not in response.json():
        raise ValueError(f"Unexpected response from OpenRouter: {response.json()}")

    answers = response.json()["answers"]

    print(answers)
    answer = answers["can_answer"]["choice"]
    return answer, answers["can_answer"]["probabilities"][answer]


def call_jev(query: str, questions: dict[str, str]) -> dict:
    pass
