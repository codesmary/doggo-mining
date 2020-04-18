from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Pet(Base):
    __tablename__ = 'pet'
    id = Column(Integer, primary_key=True)
    mixed_breed = Column(Boolean)
    primary_color = Column(String(500))
    secondary_color = Column(String(500))
    tertiary_color = Column(String(500))
    age = Column(String(500))
    size = Column(String(500))
    gender = Column(String(500))
    coat = Column(String(500))
    good_with_children = Column(Boolean)
    good_with_other_dogs = Column(Boolean)
    good_with_cats = Column(Boolean)
    unknown_breed = Column(Boolean)
    primary_breed = Column(String(500))
    secondary_breed = Column(String(500))

engine = create_engine('sqlite:///pets.db')
Base.metadata.create_all(engine)