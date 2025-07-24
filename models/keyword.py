from sqlalchemy import Column, Integer, String

from config.database import Base


class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Keyword(word='{self.word}')>"
