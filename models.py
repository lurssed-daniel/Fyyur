from app import db


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(100))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")

    def __repr__(self):
        return f'Venue id: {self.id} name: {self.name} city: {self.city} state: {self.state}'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")

    def __repr__(self):
        return f'Artist id: {self.id} name: {self.name} city: {self.city} state: {self.state}'

    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

    class Shows(db.Model):
      __tablename__ = 'shows'
      id = db.Column(db.Integer, primary_key=True)
      venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
      artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
      start_time = db.Column(db.DateTime, nullable=False)

      def __repr__(self):
          return f'Show artists_id: {self.artist_id} venues_id: {self.venue_id}'