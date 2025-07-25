from sqlalchemy import Column, String
from config.database import Base

class Setting(Base):
    __tablename__ = "_settings"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

