#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'venue', lazy = True)
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='artist', lazy=True)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable = False)
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
  cities = db.session.query(Venue.city).distinct()
  data = []
  for city in cities:
    venue_data = []
    venues = Venue.query.filter_by(city = city)
    for venue in venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0,
      })
    data.append({
      "city": city,
      "state": venues[0].state,
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  result = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  for venue in  result:
    data.append({
      "id" : venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0,
    })
  response={
    "count": len(result),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  shows = db.session.query(Artist).join(Show,  Artist.id == Show.artist_id)\
    .filter(Show.venue_id == venue_id).with_entities(Artist.id, Artist.name,Artist.image_link, Show.start_time).all()
  upcoming_shows = []
  past_shows = []
  for show in shows:
    show_data = {
        "artist_id": show[0],
        "artist_name": show[1],
        "artist_image_link": show[2],
        "start_time": show[3].strftime('%Y-%m-%d %H:%M:%S')
    }
    if show[3] < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)
  venue = Venue.query.get(venue_id)
  data={
    "id": venue.id,
    "name": venue,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  genres = ','.join(request.form.getlist('genres'))
  venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link,
                facebook_link = facebook_link, genres = genres)
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  result = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data = []
  for artist in result:
    data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": 0,
    })
  response = {
      "count": len(result),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  shows = db.session.query(Venue).join(Show,  Venue.id == Show.venue_id)\
    .filter(Show.artist_id == artist_id).with_entities(Venue.id, Venue.name, Venue.image_link, Show.start_time).all()
  upcoming_shows = []
  past_shows = []
  for show in shows:
    show_data = {
        "venue_id": show[0],
        "venue_name": show[1],
        "venue_image_link": show[2],
        "start_time": show[3].strftime('%Y-%m-%d %H:%M:%S')
    }
    if show[3] < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = Artist.query.get(artist_id)
  artist={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres.split(','),
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist_data.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  genres = ','.join(request.form.getlist('genres'))
  try:
    Artist.query.get(artist_id).update({
      "name": name,
      "genres": genres,
      "city": city,
      "state": state,
      "phone": phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": image_link
    })
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.get(venue_id)
  venue={
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": venue_data.genres.split(','),
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue_data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  genres = ','.join(request.form.getlist('genres'))
  try:
    Venue.query.get(venue_id).update({
      "name": name,
      "genres": genres,
      "address": address,
      "city": city,
      "state": state,
      "phone": phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": image_link
    })
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.close()
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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  genres = ','.join(request.form.getlist('genres'))
  artist = Artist(name = name, city = city, state = state, phone = phone, image_link = image_link,
                facebook_link = facebook_link, genres = genres)
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Venue).join(Show, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id)\
    .with_entities(Venue.id,Venue.name, Artist.id,Artist.name,Artist.image_link, Show.start_time).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show[0],
      "venue_name": show[1],
      "artist_id": show[2],
      "artist_name": show[3],
      "artist_image_link": show[4],
      "start_time": show[5].strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%d %H:%M:%S')
  try:
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
