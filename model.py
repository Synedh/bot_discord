from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Image(Base):
    __tablename__ = 'Image'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    name = Column(String)
    date = Column(DateTime)
    sender = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<Image (name='%s', date='%s', sender='%s')>" % (self.name, str(self.date), self.sender)