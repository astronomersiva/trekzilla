from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+config.DBUSER+':'+config.DBPASSWD+'@'+config.DBHOST+'/'+config.DBNAME
db = SQLAlchemy(app)

event_organizers_table = db.Table('event_organizers', 
      db.Column('organizer_id',db.Integer, db.ForeignKey("members.id")),
      db.Column('event_id',db.Integer, db.ForeignKey("events.id"))
)

class Member(db.Model):
  __tablename__ = 'members'

  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(length=256, convert_unicode=True))
  is_organizer = db.Column(db.Boolean)
  gender = db.Column(db.String(length=16, convert_unicode=True))
  age = db.Column(db.Integer)
  dob = db.Column(db.String(length=256, convert_unicode=True))
  id_proof = db.Column(db.String(length=256, convert_unicode=True))
  id_proof_number = db.Column(db.String(length=256, convert_unicode=True))
  email = db.Column(db.String(length=256),unique=True,nullable=False)
  fb_profile = db.Column(db.String(length=512, convert_unicode=True))
  contact = db.Column(db.String(length=60, convert_unicode=True))
  emergency_contact = db.Column(db.String(length=60, convert_unicode=True))
  emergency_contact_person = db.Column(db.String(length=256, convert_unicode=True))
  bloodgroup = db.Column(db.String(length=60))
  swimming_ability = db.Column(db.Unicode(256))
  bike_type = db.Column(db.String(length=60, convert_unicode=True))
  bike_model = db.Column(db.String(length=256, convert_unicode=True))
  bike_registration_number = db.Column(db.String(length=256))
  camera_model = db.Column(db.String(length=256, convert_unicode=True))
  cycle_type = db.Column(db.String(length=60, convert_unicode=True))
  cycle_model = db.Column(db.String(length=256, convert_unicode=True))
  tshirt_size = db.Column(db.String(length=16, convert_unicode=True))


  def __repr__(self):
    return self.name + '<' + self.email + '>'

class Event(db.Model):

  __tablename__ = 'events'

  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(length=256, convert_unicode=True),nullable=False)
  category = db.Column(db.String(length=256, convert_unicode=True))
  start_date = db.Column(db.Date)
  end_date = db.Column(db.Date)
  location = db.Column(db.String(length=256, convert_unicode=True))
  trek_difficulty = db.Column(db.String(length=60, convert_unicode=True))
  swimming_batch_level = db.Column(db.String(length=60, convert_unicode=True))
  primary_organizer_id = db.Column(db.Integer,db.ForeignKey("members.id")) 

  organizers = db.relationship("Member", secondary = event_organizers_table, backref="organized_events")
  #trek = relationship("Trek", uselist=False, backref="event")

  primary_organizer = db.relationship("Member", backref="events_as_primary_organizer" )

  def __repr__(self):
    return self.name

  

class CoastalCleanupZone(db.Model):
  __tablename__ = "coastal_cleanup_zones"
  id = db.Column(db.Integer,primary_key=True)
  event_id = db.Column(db.Integer,db.ForeignKey("events.id"))
  zone_name = db.Column(db.String(length=256, convert_unicode=True))
  zone_lead1 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_lead2 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_lead3 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_lead4 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_greenlead1 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_greenlead2 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_greenlead3 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_greenlead4 = db.Column(db.Integer,db.ForeignKey("members.id"))
  zone_headcount = db.Column(db.Integer,db.ForeignKey("members.id"))


class Worksheet(db.Model):

  __tablename__ = 'worksheets'

  id = db.Column(db.Integer,primary_key=True)
  gdata_resourceId = db.Column(db.String(length=256, convert_unicode=True),nullable=False)
  name = db.Column(db.String(length=256, convert_unicode=True))
  filename = db.Column(db.String(length=256, convert_unicode=True))
  event_id = db.Column(db.Integer,db.ForeignKey("events.id"))

  event = db.relationship("Event", backref="worksheets" )

class Registration(db.Model):

  __tablename__ = 'registrations'

  id = db.Column(db.Integer,primary_key=True)
  datetime = db.Column(db.String(length=256, convert_unicode=True))
  member_id = db.Column(db.Integer,db.ForeignKey("members.id"),nullable=False)
  event_id = db.Column(db.Integer,db.ForeignKey("events.id"),nullable=False)
  joining_at = db.Column(db.Unicode(256))
  volunteer_for = db.Column(db.String(length=256, convert_unicode=True))
  selected = db.Column(db.String(length=60, convert_unicode=True))
  payment_status = db.Column(db.String(length=60, convert_unicode=True))
  bring_along = db.Column(db.String(length=60, convert_unicode=True))
  biketrip_joining_as = db.Column(db.String(length=60, convert_unicode=True))
  photographer = db.Column(db.Boolean)
  dropout = db.Column(db.Boolean)
  triathlon_event = db.Column(db.String(length=60, convert_unicode=True))
  swimming_batch = db.Column(db.String(length=256, convert_unicode=True))
  prev_experience = db.Column(db.UnicodeText)
  final_organizer_comments = db.Column(db.UnicodeText)

  member = db.relationship("Member", backref="registrations")
  event = db.relationship("Event", backref="registrations" )

if __name__ == '__main__':
  db.create_all()
