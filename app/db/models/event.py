import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.place import Place


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    name: Mapped[str] = mapped_column(String(250))

    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("places.id"),
    )
    place: Mapped["Place"] = relationship()

    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    status: Mapped[str] = mapped_column(String(50))

    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
