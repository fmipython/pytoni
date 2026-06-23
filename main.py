from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from pytoni.agents.course_manager import create_agent
from pytoni.auth import TokenClaims, verify_token
from pytoni.database import get_db
from pytoni.db_models import Message
from pytoni.models import UserMessage, AssistantMessage

app = FastAPI(title="pytoni")


@app.post("/chat")
def chat(
    user_message: UserMessage,
    claims: TokenClaims = Depends(verify_token),
    db: Session = Depends(get_db),
) -> AssistantMessage:
    agent = create_agent()
    response = agent.run(user_message.message)

    assistant_message = AssistantMessage(message=response.content)

    db.add(
        Message(
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            user_message=user_message.message,
            assistant_message=assistant_message.message,
            discord_id=claims.discord_id,
            discord_name=claims.discord_name,
        )
    )
    db.commit()

    return assistant_message


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
