#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://gayatri:1234@localhost:5432/fyyur'
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)    
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=False)
    
    def __repr__(self):

      return f'<Venue: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, genres: {self.genres}, website: {self.website}, shows: {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String)    
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=False)

    def __repr__(self):
      return f'<Artist: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, shows: {self.shows}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
   _tablename__ = 'show'

   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)

   def __repr__(self):
    return f'<Show {self.id}, date: {self.date}, artist_id: {self.artist_id}, venue_id: {self.venue_id}>'
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
  data =[]
  venues = Venue.query.all()
  a = Venue.query.distinct(Venue.city,Venue.state).all()
  for i in a:
    list_of_venues = []
    for v in venues:
      if v.city == i.city and v.state == i.state:
         list_of_venues.append({
           'id': v.id, 
           'name':v.name})
         data.append({
          'city' : i.city,
          'state': i.state,
          'venues': [{'id': v.id, 'name':v.name}]      
    })
    return render_template('pages/venues.html', areas=data);

     

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  v = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  data =[]
  for i in v:
    data.append({'id': i.id, 'name': i.name,})
  response = {'data': data, 'count': len(v)}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 v = Venue.query.get(venue_id)
 a = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
 upcoming_shows =[]
 b= db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
 past_shows =[]

 for show in a:
  upcoming_shows.append({
      'artist_image_link': show.artist.image_link,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
 for show in b:
   past_shows.append({
    'artist_image_link': show.artist.image_link,
    'artist_id': show.artist.id,
    'artist_name': show.artist.name,
    'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })
 data= {
   'id': v.id,
   'name': v.name,
   'genres': v.genres,
   'address': v.address,
   'city': v.city,
   'state': v.state,
   'phone': v.phone,
   'website_link': v.website_link,
   'image_link': v.image_link,
   'facebook_link': v.facebook_link,
   'seeking_talent': v.seeking_talent,
   'seeking_description': v.seeking_description,
   'past_shows': past_shows,
   'upcoming_shows': upcoming_shows,
   'past_shows_count': len(past_shows),
   'upcoming_shows_count': len(upcoming_shows)
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
  form =VenueForm(request.form)
  try:
    venue = Venue(name=form.name.data,city=form.city.data,state=form.state.data,
    address=form.address.data,phone=form.phone.data,image_link=form.image_link.data,
    genres=form.genres.data,facebook_link=form.facebook_link.data,website_link=form.website_link.data,
    seeking_talent=form.seeking_talent.data,seeking_description=form.seeking_description.data)
   
    db.session.add(venue)
    db.session.commit()
    
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
   print(e)
   flash('An error occurred. Venue ' + Venue.name + ' could not be listed.')
   db.session.rollback()
  finally: 
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try: 
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
   db.sesion.rollback()
  finally:
    db.session.close()
  return jsonify({'success':True})

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.All()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  a = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  data = []
  for i in a:
   data.append({
    'id':i.id,
    'name':i.name
    })
  
  response ={
   'data': data,
   'count': len(a)
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  a = Artist.query.get(artist_id)
  #define upcoming and past shows
  query1 = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows= []
  
  query2 = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows= []

  for show in query1:
    upcoming_shows.append({
      'venue_image_link': show.venue.image_link,
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in query2:
     past_shows.append({
      'venue_image_link': show.venue.image_link,
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  #display appropriate data 
  data= {
   'id': a.id,
   'name': a.name,
   'genres': a.genres,
   'city': a.city,
   'state': a.state,
   'phone': a.phone,
   'website_link': a.website_link,
   'facebook_link': a.facebook_link,
   'image_link': a.image_link,
   'seeking_venue': a.seeking_venue,
   'seeking_description': a.seeking_description,
   'past_shows': past_shows,
   'upcoming_shows': upcoming_shows,
   'past_shows_count': len(past_shows),
   'upcoming_shows_count': len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])

def edit_artist(artist_id):
  form = ArtistForm(obj = a)
  a = Artist.query.get(artist_id)
  a={
    'id': a.id,
    'name': a.name,
    'genres': a.genres,
    'city': a.city,
    "state": a.state,
    'phone': a.phone,
    'website_link': a.website_link,
    'facebook_link': a.facebook_link,
    'seeking_venue': a.seeking_venue,
    'seeking_description': a.seeking_description,
    'image_link': a.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=a)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  a= Artist.query.get(artist_id)
  form=ArtistForm(request.form)
  try: 
   
    a.name=form.name.data,
    a.city=form.city.data,
    a.state=form.state.data, 
    a.phone=form.phone.data,
    a.image_link=form.image_link.data,
    a.genres=form.genres.data,
    a.facebook_link=form.facebook_link.data,
    a.website_link=form.website_link.data,
    a.seeking_venue=form.seeking_venue.data,
    a.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + Artist.name + ' could not be updated.')
  finally: 
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  v=Venue.query.get(venue_id)
  form = VenueForm(obj=v)
  v={
    'id': v.id, 
    'name': v.name,
    'genres': v.genres,
    'address': v.address,
    'city': v.city,
    'state': v.state,
    'phone': v.phone,
    'website_link': v.website_link, 
    'facebook_link': v.facebook_link,
    'seeking_talent': v.seeking_talent,
    'seeking_description': v.seeking_description,
    'image_link': v.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=v)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  v = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    v.name=form.name.data,
    v.city=form.city.data,
    v.state=form.state.data,
    v.address=form.address.data,
    v.phone=form.phone.data,
    v.image_link=form.image_link.data,
    v.genres=form.genres.data,
    v.facebook_link=form.facebook_link.data,
    v.website_link=form.website_link.data,
    v.seeking_talent=form.seeking_talent.data,
    v.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + Venue.name + ' could not be updated.')
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
  form = ArtistForm(request.form)
  try: 
    a= Artist(name=form.name.data,city=form.city.data,state=form.state.data, 
    phone=form.phone.data,image_link=form.image_link.data,genres=form.genres.data,
    facebook_link=form.facebook_link.data,website_link=form.website_link.data,
    seeking_venue=form.seeking_venue.data,seeking_description=form.seeking_description.data)
    
    db.session.add(a)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + Artist.name + ' could not be listed.')
  finally: 
    db.session.close()
  return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
   a = Show.query.all()
   data = []

   for i in a:
        show_details = {
            "venue_id": i.venue_id,
            "venue_name": i.venue.name,
            "artist_id": i.artist_id,
            "artist_name": i.artist.name,
            "artist_image_link": i.artist.image_link,
            "start_time": str(i.start_time),
        }

        data.append(show_details)
   return render_template('pages/shows.html', shows=data)

  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try: 
    show = Show(artist_id=form.artist_id.data,venue_id=form.venue_id.data,start_time=form.start_time.data)

    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except ValueError as e:
    print (e)
    db.session.rollback()
    flash('An error occurred. Show ' + Show.name + ' could not be listed.')
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

 
