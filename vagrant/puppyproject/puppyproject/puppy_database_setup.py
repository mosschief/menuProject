__author__ = 'mossc'

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()




class Shelter(Base):
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    address = Column(String(250))
    city = Column(String(250))
    state = Column(String(250))
    email = Column(String(250))
    zipcode = Column(String(10))
    website = Column(String)
    maximum_occupancy = Column(Integer)
    current_occupancy = Column(Integer)


class Adopter(Base):
    __tablename__ = 'adopter'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    puppies = relationship('Puppy', secondary='puppy_adopter_link')


class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    dateOfBirth = Column(Date)
    breed = Column(String(250))
    gender = Column(String(8))
    weight = Column(Numeric(10))
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    # adopter = relationship(Adopter, secondary=association_table, backref = 'puppies')
    adopters = relationship(Adopter, secondary='puppy_adopter_link')


class PuppyAdopterLink(Base):

    __tablename__ = 'puppy_adopter_link'
    id = Column(Integer, primary_key=True)
    puppy_id = Column(Integer, ForeignKey('puppy.id'))
    adopter_id = Column(Integer, ForeignKey('adopter.id'))


engine = create_engine('sqlite:///puppyshelter.db')


Base.metadata.create_all(engine)