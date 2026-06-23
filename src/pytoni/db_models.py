from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pytoni.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_message_id: Mapped[str] = mapped_column(String, nullable=False)
    assistant_message_id: Mapped[str] = mapped_column(String, nullable=False)

    user_message: Mapped[str] = mapped_column(String, nullable=False)
    assistant_message: Mapped[str] = mapped_column(String, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    discord_id: Mapped[str] = mapped_column(String, nullable=False)
    discord_name: Mapped[str] = mapped_column(String, nullable=False)
