from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime
from database import Base, engine


class Standup(Base):
    __tablename__ = "standups"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    name = Column(String(100))
    yesterday = Column(Text)
    today = Column(Text)
    blockers = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Member(Base):
    """Everyone who has messaged the bot at least once is a team member."""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    name = Column(String(100))
    joined_at = Column(DateTime, default=datetime.now)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created")
