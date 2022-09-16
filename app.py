#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

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
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    all_venues = Venue.query.all()
    if not all_venues:
      flash('couldn\'t find your Venue !! Create one!!!')
      return render_template('pages/venues.html', areas=data)
    data = []

    for area in all_venues:
      num_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==area.id).filter(Show.start_time>datetime.now()).count()
      venue_dict = {'id':area.id, 'name':area.name, 'num_upcoming_shows': num_upcoming_shows}
      currentData = [(d) for d in data if (d['city'] == area.city and d['state'] == area.state)]
      if not(currentData):
        cityStateVenue_dict  = {'city': area.city, 'state': area.state, 'venues': [venue_dict] }
        data.append(cityStateVenue_dict)
      else:
        venues_list = currentData[0]['venues']
        venues_list.append(venue_dict)
        data[data.index(currentData[0])]['venues'] = venues_list
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_Term = request.form['search_term']
  data = []
  off_venues = Venue.query.filter(Venue.name.ilike('%'+search_Term+'%'))
  for area in off_venues:
    data.append({
      "id" : area.id,
      "name" : area.name,
      "num_upcoming_shows" : db.session.query(Venue).join(Show).filter(Show.venue_id == area.id).filter(Show.start_time > datetime.now()).count()
    })
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  shows = []
  shows = db.session.query(
  Artist.id.label('artist_id'),
  Artist.name.label('artist_name'),
  Artist.image_link.label('artist_image_link'),
  Show.start_time).join(Show).filter(
  Show.venue_id == venue_id).filter(
  Show.start_time < datetime.now())
  past_shows = []
  for show in shows:
    past_shows.append(
      {
       'artist_id' :show['artist_id'],
       'artist_name' : show['artist_name'],
       'artist_image_link' : show['artist_image_link'],
       'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  shows = db.session.query(
  Artist.id.label('artist_id'),
  Artist.name.label('artist_name'),
  Artist.image_link.label('artist_image_link'),
  Show.start_time).join(Show).filter(
  Show.venue_id == venue_id).filter(
  Show.start_time > datetime.now())
  upcoming_shows = []

  for show in shows:
    upcoming_shows.append(
      {
       'artist_id' :show['artist_id'],
       'artist_name' : show['artist_name'],
       'artist_image_link' : show['artist_image_link'],
       'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows" :past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
  try:
        form = VenueForm()

        if form.validate_on_submit():
            print("Form Valid")
        else:
            return render_template('forms/new_venue.html', form=form)

        existing_venue = Venue.query.filter(
            Venue.name.ilike(f'%{form.name.data}%')).all()
        if len(existing_venue) > 0:
            form.name.errors.append(
                'Venue name ' +
                request.form['name'] +
                ' already exists!')
            return render_template('forms/new_venue.html', form=form)

        genres = ",".join(form.genres.data)

        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, genres=genres,
                      image_link=form.image_link.data, facebook_link=form.facebook_link.data, website_link=form.website_link.data, is_talent_seeking=form.seeking_talent.data,
                      talent_seeking_description=form.seeking_description.data)

        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully created!')
  except BaseException:
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ for flash
        # messages
        db.session.rollback()
        flash('An error occured Venue ' + request.form['name'] + ' was not successfully created!')
        print(sys.exc_info())
  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue: {venue_id} was successfully deleted!')
    except BaseException:
        flash(f'Venue: {venue_id} was not successfully deleted!')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'Success': True})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_Term = request.form['search_term']
  data = []
  venue_area = Artist.query.filter(Artist.name.ilike('%'+search_Term+'%'))
  for artist in venue_area:
    data.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : db.session.query(Artist).join(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).count()
    })
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()
    shows = []
    shows = db.session.query(
    Venue.id.label('venue_id'),
    Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'),
    Show.start_time).join(Show).filter(
    Show.artist_id == artist_id).filter(
    Show.start_time < datetime.now())
    past_shows = []
    for show in shows:
      past_shows.append(
      {
        'venue_id' :show['venue_id'],
        'venue_name' : show['venue_name'],
        'venue_image_link' : show['venue_image_link'],
        'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
      )
    shows = db.session.query(
    Venue.id.label('venue_id'),
    Venue.name.label('venue_name'),
    Venue.image_link.label('venue_image_link'),
    Show.start_time).join(Show).filter(
    Show.artist_id == artist_id).filter(
    Show.start_time > datetime.now())
    upcoming_shows = []
    for show in shows:
      upcoming_shows.append(
        {
        'venue_id' :show['venue_id'],
        'venue_name' : show['venue_name'],
        'venue_image_link' : show['venue_image_link'],
        'start_time' : show['start_time'].strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
      )
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows" :past_shows,
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
  # TODO: populate form with fields from artist with ID <artist_id>

  try:
        artist = Artist.query.get(artist_id)
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres.split(',')
        form.image_link.data = artist.image_link
        form.facebook_link.data = artist.facebook_link
        form.website_link.data = artist.website_link
        form.seeking_venue.data = artist.is_venue_seeking
        form.seeking_description.data = artist.venue_seeking_description

  except BaseException:
        flash(f'Artist: {artist_id} was not successfully loaded!')
        print(sys.exc_info())
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  try:
     artist = Artist.query.get(artist_id)
     artist.name=request.form['name']
     artist.city=request.form['city']
     artist.state=request.form['state']
     artist.phone =request.form['phone'],
     artist.image_link=request.form['image_link']
     artist.facebook_link=request.form['facebook_link']
     artist.website =request.form['website_link'],
     artist.seeking_venue =bool(request.form.get('seeking_venue'))
     artist.seeking_description =request.form['seeking_description'],
     artist.genres=','.join([str(item) for item in request.form.getlist('genres')])
     db.session.add(artist)
     db.session.commit()
     flash('Artist ' + request.form['name'] + ' was successfully Updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist  ' + request.form['name'] + ' could not be Update.')
  finally:
        db.session.close()
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter(Venue.id == venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
     venue = Venue.query.get(venue_id)
     venue.name=request.form['name']
     venue.city=request.form['city']
     venue.state=request.form['state']
     venue.address=request.form['address']
     venue.phone =request.form['phone'],
     venue.image_link=request.form['image_link']
     venue.facebook_link=request.form['facebook_link']
     venue.website =request.form['website_link'],
     venue.seeking_talent =bool(request.form.get('seeking_talent'))
     venue.seeking_description =request.form['seeking_description'],
     venue.genres=','.join([str(item) for item in request.form.getlist('genres')])
     db.session.add(venue)
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully Updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Venue  ' + request.form['name'] + ' could not be Update.')
  finally:
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

    try:
        form = ArtistForm()

        if form.validate_on_submit():
            print("Form Valid")
        else:
            return render_template('forms/new_artist.html', form=form)

        existing_artist = Artist.query.filter(
            Artist.name.ilike(f'%{form.name.data}%')).all()
        if len(existing_artist) > 0:
            form.name.errors.append(
                'Artist name ' +
                request.form['name'] +
                ' already exists!')
            return render_template('forms/new_artist.html', form=form)

        genres = ",".join(form.genres.data)

        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, genres=genres,
                        image_link=form.image_link.data, facebook_link=form.facebook_link.data, website_link=form.website_link.data, is_venue_seeking=form.seeking_venue.data,
                        venue_seeking_description=form.seeking_description.data)

        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except BaseException:
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
        # listed.')
        db.session.rollback()
        flash(
            'An error occured Artist ' +
            request.form['name'] +
            ' was not successfully listed!')
        print(sys.exc_info())
    finally:
        db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append(
      {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  venues = Venue.query.all()
  artists = Artist.query.all()

  form.artist_id.choices = []
  form.venue_id.choices = []

  for venue in venues:
      form.venue_id.choices.append((venue.id, venue.name))

  for artist in artists:
      form.artist_id.choices.append((artist.id, artist.name))

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
        form = ShowForm()

        venue_id = form.venue_id.data
        artist_id = form.artist_id.data
        start_time = form.start_time.data

        show = Show(
            venue_id=venue_id,
            artist_id=artist_id,
            start_time=start_time)

        db.session.add(show)
        db.session.commit()
# on successful db insert, flash success
        flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
  except BaseException:
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('An error occured Show was not successfully listed!')
        print(sys.exc_info())
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
