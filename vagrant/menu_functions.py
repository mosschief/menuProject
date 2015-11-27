__author__ = 'mossc'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import text

from database_setup import Base, MenuItem, Restaurant


def session():

    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    return session

def getrestaurants():

    s = session()
    restaurants = s.query(Restaurant).all()
    return restaurants

def add_restaurant(restaurant_name):

    s = session()
    restaurant = Restaurant(name=restaurant_name)
    s.add(restaurant)
    s.commit()

def get_restaurant(restaurant_id):
    s = session()
    restaurant = s.query(Restaurant).filter_by(id=restaurant_id).one()
    return restaurant

def update_restaurant(restaurant_id,new_restaurant_name):

    s = session()
    restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
    restaurant.name = new_restaurant_name
    s.add(restaurant)
    s.commit()

def delete_restaurant(restaurant_id):

    s = session()
    restaurant = s.query(Restaurant).filter_by(id = restaurant_id).one()
    s.delete(restaurant)
    s.commit()