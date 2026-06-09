"""
Pilot participant counter for the Social Influence Task.

Maintains a persistent counter in the DB (single-row table).
Each new pilot participant gets the next index.
Index drives artwork-condition assignment (participant_index mod 12).
"""

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class ParticipantCounter(Base):
    __tablename__ = "participant_counter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    next_index: Mapped[int] = mapped_column(Integer, default=0)


def assign_participant_index(db: DBSession) -> int:
    counter = db.get(ParticipantCounter, 1)
    if counter is None:
        counter = ParticipantCounter(id=1, next_index=0)
        db.add(counter)
        db.flush()

    index = counter.next_index
    counter.next_index = index + 1
    db.commit()

    return index
