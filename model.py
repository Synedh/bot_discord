from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method

Base = declarative_base()

association_image_user = Table('association_image_user', Base.metadata,
    Column('image_id', Integer, ForeignKey('Image.id')),
    Column('user_id', Integer, ForeignKey('User.id'))
)

association_stats = Table('association_stats', Base.metadata,
    Column('channelstats_id', Integer, ForeignKey('ChannelStats.id')),
    Column('userstats_id', Integer, ForeignKey('UserStats.id'))
)

class Image(Base):
    __tablename__ = 'Image'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    name = Column(String)
    date = Column(DateTime)
    sender = Column(String)
    url = Column(String)
    used = Column(Integer)

    def __repr__(self):
        return ("<Image (name='%s', date='%s', sender='%s')>" 
            % (self.name, str(self.date), self.sender))


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    isInTite = Column(Boolean)
    hasEnougthRank = Column(Boolean, default=False)
    images = relationship("Image", secondary=association_image_user)

    @hybrid_method
    def fav_images(self):
        return [image.id for image in self.images]

    def __repr__(self):
        return ("<User (id='%s', username='%s', isInTite='%s', hasEnougthRank'%s')>" 
            % (self.id, self.username, self.isInTite, self.hasEnougthRank))


class Message(Base):
    __tablename__ = 'Message'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    server = Column(String)
    channel = Column(String)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship('User')
    date = Column(DateTime)


### ADD TABLES ###
# import model
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# engine = create_engine('sqlite:///account.db')
# session = Session(engine)
# model.Base.metadata.create_all(engine)