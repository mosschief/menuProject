__author__ = 'mossc'
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import httplib2
import requests




app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email'])
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserId(email):

    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id

    except:
        return None

@app.route("/gdisconnect")
def gdisconnect():
    print("My name is: %s" % login_session['username'] )
    print 'In gdisconnect access token is %s', login_session['access_token']

    if login_session['access_token'] is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("URL is: %s " % url)
    print('Result is: ' + str(result))

    if result['status'] == '200':
        #Reset the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # Given token was invalid

        response = make_response(json.dumps('Failed to revoke token for a given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    if 'username' not in login_session:
        return redirect('/login')
    restaurants = session.query(Restaurant).all()
    return render_template("restaurants.html", restaurants=restaurants, name=login_session['username'], myID=login_session['user_id'])


@app.route('/restaurants/new/', methods=['GET','POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':

        newRestaurant = Restaurant(name = request.form['name'], user_id=login_session['user_id'])
        session.add(newRestaurant)
        session.commit()
        flash('New restaurant created!')
        return redirect(url_for('restaurants'))

    else:
        return render_template('newrestaurant.html')

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):

    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if login_session['user_id'] != restaurant.user_id:
        flash('Restricted access')
        return redirect(url_for('restaurants'))



    if request.method == 'POST':
        restaurant.name = request.form['name']

        session.add(restaurant)
        session.commit()
        flash('Restaurant name changed')
        return redirect(url_for('restaurants'))
    else:

        return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):

    if 'username' not in login_session:
        return redirect('/login')

    deletedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if login_session['user_id'] != deletedRestaurant.user_id:
        flash('Restricted access')
        return redirect(url_for('restaurants'))


    session.delete(deletedRestaurant)

    deletedItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    for item in deletedItems:
        session.delete(item)

    session.commit()

    flash('Restaurant Deleted!')
    return redirect(url_for('restaurants'))

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(item.serialize)


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],restaurant_id=restaurant_id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New menu item created!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:

        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    editItem = session.query(MenuItem).filter_by(id=menu_id).one()

    if login_session['user_id'] != editItem.user_id:
        flash('Restricted access')
        return redirect(url_for('restaurantMenu'),restaurant_id=restaurant_id)

    if request.method == 'POST':

        editItem.name = request.form['name']
        session.add(editItem)
        session.commit()
        flash('Menu Item Edited!')

        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

    else:
        itemname = session.query(MenuItem.name).filter(MenuItem.id==menu_id).one()
        return render_template('edititem.html', restaurant_id = restaurant_id, menu_id=menu_id, itemname=itemname[0])

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):

    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != deletedItem.user_id:
        flash('Restricted access')
        return redirect(url_for(restaurantMenu),restaurant_id=restaurant_id)

    if request.method == 'POST':

        session.delete(deletedItem)
        session.commit()
        flash('Menu Item Deleted!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

    else:

        itemname = session.query(MenuItem.name).filter(MenuItem.id==menu_id).one()
        return render_template('deleteitem.html', restaurant_id = restaurant_id, menu_id=menu_id, itemname=itemname[0])



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)