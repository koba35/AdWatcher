__author__ = 'koba'
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, VARCHAR, DateTime

Base = declarative_base()


class Spamer(Base):
    __tablename__ = 'spamers'
    id = Column(Integer, primary_key=True)
    phone = Column(VARCHAR)

    def __init__(self, phone):
        self.phone = phone

    def __repr__(self):
        return "<Номер: %s>" % self.phone


class Core(Base):
    __tablename__ = 'core'
    id = Column(Integer, primary_key=True)
    last_visit = Column(DateTime)
    name = Column(VARCHAR)

    def __init__(self, name,last_visit):
        self.last_visit = last_visit
        self.name = name

    def __repr__(self):
        return "<Бот %s, последнее посещение: %s>" % (self.name, self.last_visit)