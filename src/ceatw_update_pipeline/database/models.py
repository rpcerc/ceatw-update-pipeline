from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils.compat import uuid7

from ceatw_update_pipeline.custom_types import Status
from ceatw_update_pipeline.database.database import Base


# Models
# https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
class Source(Base):
    __tablename__ = "source"
    
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7
    )
    title: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, unique=True)
    country: Mapped[str] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(String(2))
    content_hash: Mapped[str] = mapped_column(Text)
    comments: Mapped[str | None] = mapped_column(Text)
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    current_status: Mapped[Status] = mapped_column(
        default=Status.UNVETTED
    )
    
    highlights: Mapped[list[Highlight]] = relationship(
        "Highlight", back_populates="source",
        lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        display_url = self.source_url[:50] + "..." if len(self.source_url) > 50 else self.source_url
        return f"<Source(source_url='{display_url}', country_code='{self.country_code}'>"

class Highlight(Base):
    __tablename__ = "highlight"
    
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid7
    )
    text: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now()
        )
    source_id: Mapped[UUID] = mapped_column(ForeignKey("source.id"))
    source: Mapped[Source] = relationship(
        "Source", back_populates="highlights"
    )