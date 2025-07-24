from sqlalchemy import Column, Integer, String

from config.database import Base


class Subreddit(Base):
    __tablename__ = "subreddits"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Subreddit(name='{self.name}')>"
