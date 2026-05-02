from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Survey(TimestampMixin, Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    interest_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    school_condition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extra_learning_intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    convenient_time: Mapped[str | None] = mapped_column(String(64), nullable=True)
    interested_field: Mapped[str | None] = mapped_column(String(64), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="surveys")
