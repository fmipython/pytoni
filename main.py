from fastapi import FastAPI


from pytoni.agents.course_manager import create_agent
from pytoni.models import UserMessage, AssistantMessage

app = FastAPI(title="pytoni")


@app.post("/chat")
def chat(user_message: UserMessage) -> AssistantMessage:
    agent = create_agent()
    response = agent.run(user_message.message)

    return AssistantMessage(message=response.content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
