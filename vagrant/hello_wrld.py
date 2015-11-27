from flask import Flask

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import menu_functions

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')

def restaurantmenu(restaurant_id):

    restaurant = menu_functions.get_restaurant(restaurant_id)
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ""

    if items != []:

        for i in items:
            output += i.name
            output += '</br>'
            output += i.price
            output += '</br>'
            output += i.description
            output += '</br>'
            output += '-----------'
            output += '</br>'
        return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)