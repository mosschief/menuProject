__author__ = 'mossc'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import text

from puppy_database_setup import Base, Shelter, Puppy, Adopter, PuppyAdopterLink


def puppy_session():

    engine = create_engine('sqlite:///puppyshelter.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    return session

def create_shelter(name, max_occupancy, current_occupancy):

    session = puppy_session()
    newshelter = Shelter(name=name, maximum_occupancy=max_occupancy, current_occupancy=current_occupancy)
    session.add(newshelter)
    session.commit()

def create_adopter(name):

    session = puppy_session()
    adopter_add = Adopter(name=name)
    session.add(adopter_add)
    session.commit()


def adopt(adopter_id, new_puppy_id):

    session = puppy_session()

    for id in adopter_id:
        count = session.query(PuppyAdopterLink).filter_by(puppy_id=new_puppy_id).filter_by(adopter_id=id).count()
        if count == 0:

            owner_add = PuppyAdopterLink(puppy_id=new_puppy_id, adopter_id=id)
            session.add(owner_add)
            session.commit()
        else:
            print 'Duplicate. Skipped addition for adopter %s' %id


    shelterid = session.query(Puppy.shelter_id).filter_by(id=new_puppy_id).one()

    puppy_update = session.query(Puppy).filter_by(id=new_puppy_id).one()
    puppy_update.shelter_id = None
    session.add(puppy_update)
    session.commit()


    shelters = session.query(Shelter).all()

    for shelter in shelters:

        puppy_count = session.query(Puppy, Shelter).filter(Shelter.id == shelter.id).filter(Puppy.shelter_id == Shelter.id).count()

        shelter.current_occupancy = puppy_count
        session.add(shelter)
        session.commit()



def puppy_checkin(name,shelter_id):

    session = puppy_session()
    # Gets maximum and current occupancy
    caps = session.query(Shelter.maximum_occupancy, Shelter.current_occupancy).filter(Shelter.id==shelter_id).one()


    if caps[0] > caps[1]:

        # adds puppy to shelter and puppy tables and increments current occupancy at shelter
        puppy_add = Puppy(name = name, shelter_id=shelter_id)
        shelteradd = session.query(Shelter).filter_by(id=shelter_id).one()
        shelteradd.current_occupancy = shelteradd.current_occupancy + 1
        session.add(shelteradd)
        session.add(puppy_add)
        session.commit()

    else:
        print('Sorry, shelter is full!')

        answer = raw_input('Do you want to look for another shelter (y/n): ')

        while answer != 'y' and answer != 'Y' and answer!= 'n' and answer!= 'N':
            print('please enter y or n')
            answer = raw_input('Do you want to look for another shelter (y/n): ')

        if answer == 'y' or answer == 'Y' or answer == 'yes' or answer ==  'Yes':
            #look for shelter
            open_shelter = session.query((Shelter.maximum_occupancy - Shelter.current_occupancy).label('open_space'),Shelter.id).order_by(text('open_space DESC')).first()
            if open_shelter.open_space > 0:
                puppy_add = Puppy(name = name, shelter_id=open_shelter.id)
                shelteradd = session.query(Shelter).filter_by(id=open_shelter.id).one()
                shelteradd.current_occupancy = shelteradd.current_occupancy + 1
                session.add(shelteradd)
                session.add(puppy_add)
                session.commit()
                print('Puppy added to shelter %s' % open_shelter.id)
            else:
                print('sorry, all shelters full')



        elif answer == 'n' or answer == 'N':
            return






