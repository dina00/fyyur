#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
import json
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker, relationship
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
basedir = os.path.abspath(os.path.dirname(__file__))

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


# TODO: connect to a local postgresql database

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_talent_description = db.Column(db.String(200))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    venue_name = db.relationship('Venue', backref=db.backref('shows'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows')) # many to one


db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  stops= db.session.query(Venue.city,Venue.state).distinct(Venue.city, Venue.state)
  for stop in stops:
    venues_in_city=db.session.query(Venue.id, Venue.name).filter(Venue.city==stop[0]).filter(Venue.state==stop[1])
    # populate data[] to send to template
    data.append({
      'city': stop[0],
      'state':stop[1],
      'venues':venues_in_city,
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues_result = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []
  num_upcoming_shows=0
  for venue in venues_result:
    shows=db.session.query(Show).filter(Show.venue_id==venue.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows+=1

    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
    })
  response={
    'count':len(venues_result),
    'data':data,
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue=db.session.query(Venue).filter(Venue.id==venue_id).one()
  shows=db.session.query(Show).filter(Show.venue_id==venue.id).all()
  past=[]
  future=[]

  for show in shows:
    artist = db.session.query(Artist).filter(Artist.id == show.artist_id).one()
    if show.start_time > datetime.now():
      future = [{
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)
      }]
    

    else:
      past.append({
        'artist_id':artist.id,
        'artist_name': artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time),
      })
  print(past)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_talent_description,
    "image_link": venue.image_link,
    "past_shows": past,
    "upcoming_shows": future,
    "past_shows_count":len(past),
    "upcoming_shows_count": len(future),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_talent_description = form.seeking_talent_description.data,
    image_link = form.image_link.data,
  )
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully added')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

      flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
  
  db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  instance= db.session.query(Venue).filter(Venue.id==venue_id).one()
  db.session.delete(instance)
  try:
    db.session.commit()
  except:
    flash('An error occurred in deleting venue.')
  db.session.close()
  return redirect(url_for('venues'))


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists= db.session.query(Artist.id,Artist.name)
  for artist in artists:
    # populate data[] to send to template
    data.append({
      'id': artist[0],
      'name':artist[1],
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists_result = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  data=[]
  num_upcoming_shows=0
  for artist in artists_result:
    shows=db.session.query(Show).filter(Show.artist_id==artist.id).all()
    for show in shows:
      if show.start_time> datetime.now():
        num_upcoming_shows+=1
    data=[{
      'id':artist.id,
      'name': artist.name,
      'num_upcoming_shows': num_upcoming_shows
    }]

  response={
    "count": len(artists_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  genres,past_shows,future_shows=[],[],[]
  artist=db.session.query(Artist).filter(Artist.id==artist_id).one()
  shows=db.session.query(Show).filter(Show.artist_id==artist.id).all()
  for genre in artist.genres:
      genres.append(genre)

  for show in shows:
    if show.start_time < datetime.now():
      venue=db.session.query(Venue).filter(Venue.id==show.venue_id).one()
      past_shows=[{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time),
      }]
    else:
      venue=db.session.query(Venue).filter(Venue.id==show.venue_id).one()
      future_shows=[{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time),
      }]

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": future_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).filter(Artist.id == aritst_id).one()

  updated_aritst = {
        name: form.name.data,
        genres: form.genres.data,
        address: form.address.data,
        city: form.city.data,
        state: form.state.data,
        phone: form.phone.data,
        website: form.website.data,
        facebook_link: form.facebook_link.data,
        seeking_venue: form.seeking_venue.data,
        seeking_description: form.seeking_description.data,
        image_link: form.image_link.data,
    }
  try:
        db.session.query(Artist).filter(Artist.id == artist_id).update(updated_artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfiully edited')
  except:
        flash('An error occurred with editing' + form.name.data)
  db.session.close()

  return render_template('forms/edit_artist.html', form=form, artist=artist)



# @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# def edit_artist_submission(artist_id):
#     form = ArtistForm(request.form)
#     artist = db.session.query(Artist).filter(Artist.id == aritst_id).one()

#     edited_artist = {
#         name: form.name.data,
#         genres: form.genres.data,
#         address: form.address.data,
#         city: form.city.data,
#         state: form.state.data,
#         phone: form.phone.data,
#         website: form.website.data,
#         facebook_link: form.facebook_link.data,
#         seeking_venue: form.seeking_venue.data,
#         seeking_description: form.seeking_description.data,
#         image_link: form.image_link.data,
#     }
#     try:
#         db.session.query(Artist).filter(Artist.id == artist_id).update(edited_artist)
#         db.session.commit()
#         flash('Artist ' + form.name.data + ' was successfiully edited')
#     except:
#         flash('An error occurred with editing' + form.name.data)
    
#     db.session.close()

#     return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  updated_venue = {
        name: form.name.data,
        genres: form.genres.data,
        address: form.address.data,
        city: form.city.data,
        state: form.state.data,
        phone: form.phone.data,
        website: form.website.data,
        facebook_link: form.facebook_link.data,
        seeking_talent: form.seeking_talent.data,
        seeking_description: form.seeking_description.data,
        image_link: form.image_link.data
    }
  try:
        db.session.query(Venue).filter(Venue.id == venue_id).update(updated_venue)
        db.session.commit()
        flash('Venue' + form.name.data + ' was updated successfully')
  except:
        flash('An error occurred while updating' + form.name.data + 'try again.')
 
  db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  artist = Artist(
        name = form.name.data,
        genres = form.genres.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        website = form.website.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data,
    )
  try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
        flash('An error occurred while adding ' + form.name.data + 'try again.')

  db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=db.session.query(Show.artist_id, Show.artist, Show.venue_id, Show.venue_name, Show.start_time).all()
  data=[]
  for show in shows:
    artist=db.session.query(Artist).filter(Artist.id==show.artist_id).one()
    venue=db.session.query(Venue).filter(Venue.id==show.venue_id).one()
    data=[{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
    )

  try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed')
  except:
        flash('An error occurred. Show could not be added')

  db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
