from typing import Optional
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from q1.repo import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    roles: Mapped[str] = mapped_column(String, default='staff')
    last_login: Mapped[datetime] = mapped_column(DateTime)

    def __init__(self, user_id: str, score: int = 0, roles: str = 'staff', last_login: Optional[datetime] = None):
        self.user_id = user_id
        self.score = score
        self.roles = roles
        self.last_login = last_login or datetime.utcnow()

    def has_role(self, role: str) -> bool:
        # 检查roles中是否包含role
        if not self.roles:
            return False
        return role in self.roles.split(';')
