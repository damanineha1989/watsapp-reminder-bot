from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    phone = Column(String)
    task = Column(String)
    reminder_time = Column(DateTime)

    def __repr__(self):
        return f"{self.id} - {self.task}"

Base.metadata.create_all(engine)
