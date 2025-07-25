import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from config.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    reddit_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    author = Column(String(100), nullable=False)
    subreddit = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
    created_utc = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Job(reddit_id='{self.reddit_id}', title='{self.title[:50]}...')>"
