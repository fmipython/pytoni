import json

import requests

from pytoni.config import get_settings
from pytoni.prompts.jev import JEV_PROMPT, PYTONI_CAN_DO, PYTONI_CANNOT_DO


def is_question_for_pytoni(user_question: str, threshold: float = 0.7) -> tuple[bool, float]:
    question = {
        "can_answer": {
            "type": "noul",
            "instructions": JEV_PROMPT,
            "criteria": {"true": PYTONI_CAN_DO, "false": PYTONI_CANNOT_DO},
        }
    }

    answers = call_jev(user_question, question)

    confidence = float(answers["can_answer"]["noul"])
    return confidence >= threshold, confidence


def call_jev(query: str, questions: dict[str, dict]) -> dict:
    settings = get_settings()
    response = requests.post(
        url=settings.jev_endpoint,
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": settings.jev_model,
                "state": query,
                "questions": questions,
            }
        ),
    )

    if "answers" not in response.json():
        raise ValueError(f"Unexpected response from OpenRouter: {response.json()}")

    answers = response.json()["answers"]
    return answers
