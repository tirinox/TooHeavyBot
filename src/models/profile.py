from models.base import Base
from dataclasses import dataclass


@dataclass
class Profile(Base):
    user_name: str = ""
