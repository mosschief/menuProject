__author__ = 'mossc'
from puppyproject import app
from flask import Flask, render_template, url_for, request, redirect, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from puppy_database_setup import Puppy, PuppyAdopterLink, Adopter, Shelter, Base


engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# List shelters and provide menu of options for shelters

@app.route('/')
@app.route('/shelters/')
def listshelters():
    shelters = session.query(Shelter).all()
    return render_template('shelters.html',shelters=shelters)

# Create new shelter

@app.route('/shelters/new/', methods=['GET','POST'])
def newshelter():

    if request.method == 'POST':
        newshelter = Shelter(name=request.form['name'], maximum_occupancy=request.form['maximum_occupancy'], current_occupancy=0)
        session.add(newshelter)
        session.commit()
        flash("Shelter added")
        return redirect(url_for('listshelters'))

    else:
        return render_template('newshelter.html')

@app.route('/shelters/<int:shelter_id>/delete/', methods=['GET','POST'])
def deleteshelter(shelter_id):

    shelter = session.query(Shelter).filter_by(id=shelter_id).one()
    session.delete(shelter)
    session.commit()
    flash("Shelter %s deleted" % str(shelter_id))
    return redirect(url_for('listshelters'))

# Check-in puppy to shelter

@app.route('/shelters/<int:shelter_id>/checkin/', methods=['GET','POST'])
def checkin(shelter_id):

    if request.method == 'POST':


        #  adds puppy to shelter and puppy tables and increments current occupancy at shelter
        puppy_add = Puppy(name = request.form['name'], shelter_id=shelter_id)
        shelteradd = session.query(Shelter).filter_by(id=shelter_id).one()
        shelteradd.current_occupancy = shelteradd.current_occupancy + 1
        session.add(shelteradd)
        session.add(puppy_add)
        session.commit()

        flash("Puppy added to shelter %s" % str(shelter_id))
        return redirect(url_for('listshelters'))


    else:

        caps = session.query(Shelter.maximum_occupancy, Shelter.current_occupancy).filter(Shelter.id==shelter_id).one()

        if caps[0] > caps[1]:

            return render_template('checkin.html', shelter_id=shelter_id)

        else:

            open_shelter = session.query((Shelter.maximum_occupancy - Shelter.current_occupancy).label('open_space'),Shelter.id).order_by(text('open_space DESC')).first()
            open_id = int(open_shelter.id)

            if open_shelter.open_space > 0:

                return render_template('shelter_full.html', shelter_id=shelter_id, open_id=open_id)

            else:
                flash('Sorry, all shelters are full!')
                return redirect(url_for('listshelters'))

# Lists all adopters

@app.route('/adopters/')
def listadopters():

    adopters = session.query(Adopter).all()
    return render_template('adopters.html',adopters=adopters)

@app.route('/adopters/new/', methods=['GET','POST'])
def newadopter():

    if request.method == 'POST':
        newadopter = Adopter(name=request.form['name'])
        session.add(newadopter)
        session.commit()
        flash("Adopter added")
        return redirect(url_for('listadopters'))

    else:
        return render_template('newadopter.html')

@app.route('/adopters/<int:adopter_id>/delete/', methods=['GET','POST'])
def deleteadopter(adopter_id):

    adopter = session.query(Adopter).filter_by(id=adopter_id).one()
    session.delete(adopter)
    session.commit()
    flash("Adopter %s deleted" % str(adopter_id))
    return redirect(url_for('listadopters'))


@app.route('/adopt/<int:adopter_id>/')
def adoptbyAdopter(adopter_id):
    available_puppies = session.query(Puppy).filter(Puppy.shelter_id!=None).all()
    return render_template('adoptbyAdopter.html', puppies=available_puppies, adopter_id=adopter_id)

@app.route('/adopt/<int:adopter_id>/<int:puppy_id>/')
def adoptPuppy(adopter_id,puppy_id):

    owner_add = PuppyAdopterLink(puppy_id=puppy_id, adopter_id=adopter_id)
    session.add(owner_add)

    puppy_update = session.query(Puppy).filter_by(id=puppy_id).one()
    puppy_update.shelter_id = None
    session.add(puppy_update)

    session.commit()

    shelters = session.query(Shelter).all()

    for shelter in shelters:

        puppy_count = session.query(Puppy, Shelter).filter(Shelter.id == shelter.id).filter(Puppy.shelter_id == Shelter.id).count()

        shelter.current_occupancy = puppy_count
        session.add(shelter)
        session.commit()
    flash('%s adopted!' % puppy_update.name)
    return redirect(url_for('listadopters'))

@app.route('/adopters/<int:adopter_id>/')
def adoptersPuppies(adopter_id):

    adopter = session.query(Adopter).filter_by(id=adopter_id).one()

    links = session.query(PuppyAdopterLink).filter_by(adopter_id=adopter_id)
    puppy_names = []
    for link in links:
        puppy = session.query(Puppy).filter_by(id=link.puppy_id).one()
        puppy_names.append(puppy.name)

    return render_template('adoptersPuppies.html', puppies=puppy_names, adopter=adopter)
