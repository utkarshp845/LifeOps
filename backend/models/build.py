import uuid

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database import Base


class BuildProject(Base):
    __tablename__ = "build_projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(80), nullable=False, default="building")
    shipped_at: Mapped[object | None] = mapped_column(Date)
    url: Mapped[str | None] = mapped_column(String(500))
    repository_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
