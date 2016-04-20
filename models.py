from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    category = Column(String, unique=False)
    name = Column(String, unique=False)
    start = Column(Integer)
    stop = Column(Integer)
    time = Column(Integer)  # value in seconds

    def __init__(self, category, name, start, stop, time):
        self.category = category
        self.name = name
        self.start = start
        self.stop = stop
        self.time = time
