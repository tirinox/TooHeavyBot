from models.base import Base
from dataclasses import dataclass


@dataclass
class TimePoint(Base):
    date: int = 0
