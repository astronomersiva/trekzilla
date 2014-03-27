from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

event_organizers_table = Table('event_organizers', Base.metadata,
      Column('organizer_id',Integer, ForeignKey("members.id")),
      Column('event_id',Integer, ForeignKey("events.id"))
)

class Member(Base):
  __tablename__ = 'members'

  id = Column(Integer,primary_key=True)
  name = Column(String(length=256, convert_unicode=True))
  is_organizer = Column(Boolean)
  gender = Column(String(length=16, convert_unicode=True))
  age = Column(Integer)
  dob = Column(String(length=256, convert_unicode=True))
  id_proof = Column(String(length=256, convert_unicode=True))
  id_proof_number = Column(String(length=256, convert_unicode=True))
  email = Column(String(length=256))
  fb_profile = Column(String(length=512, convert_unicode=True))
  contact = Column(String(length=60, convert_unicode=True))
  emergency_contact = Column(String(length=60, convert_unicode=True))
  emergency_contact_person = Column(String(length=256, convert_unicode=True))
  bloodgroup = Column(String(length=60))
  swimming_ability = Column(Unicode(256))
  bike_type = Column(String(length=60, convert_unicode=True))
  bike_model = Column(String(length=256, convert_unicode=True))
  bike_registration_number = Column(String(length=256))
  camera_model = Column(String(length=256, convert_unicode=True))
  cycle_type = Column(String(length=60, convert_unicode=True))
  cycle_model = Column(String(length=256, convert_unicode=True))
  tshirt_size = Column(String(length=16, convert_unicode=True))

class Event(Base):

  __tablename__ = 'events'

  id = Column(Integer,primary_key=True)
  name = Column(String(length=256, convert_unicode=True),nullable=False)
  category = Column(String(length=256, convert_unicode=True))
  start_date = Column(Date)
  end_date = Column(Date)
  location = Column(String(length=256, convert_unicode=True))
  trek_difficulty = Column(String(length=60, convert_unicode=True))
  swimming_level = Column(String(length=60, convert_unicode=True))

  organizers = relationship("Member", secondary = event_organizers_table, backref="organized_events")
  #trek = relationship("Trek", uselist=False, backref="event")

  

class CoastalCleanupZone(Base):
  __tablename__ = "coastal_cleanup_zones"
  id = Column(Integer,primary_key=True)
  event_id = Column(Integer,ForeignKey("events.id"))
  zone_name = Column(String(length=256, convert_unicode=True))
  zone_lead1 = Column(Integer,ForeignKey("members.id"))
  zone_lead2 = Column(Integer,ForeignKey("members.id"))
  zone_lead3 = Column(Integer,ForeignKey("members.id"))
  zone_lead4 = Column(Integer,ForeignKey("members.id"))
  zone_greenlead1 = Column(Integer,ForeignKey("members.id"))
  zone_greenlead2 = Column(Integer,ForeignKey("members.id"))
  zone_greenlead3 = Column(Integer,ForeignKey("members.id"))
  zone_greenlead4 = Column(Integer,ForeignKey("members.id"))
  zone_headcount = Column(Integer,ForeignKey("members.id"))


class Worksheet(Base):

  __tablename__ = 'worksheets'

  id = Column(Integer,primary_key=True)
  gdata_resourceId = Column(String(length=256, convert_unicode=True),nullable=False)
  name = Column(String(length=256, convert_unicode=True))
  filename = Column(String(length=256, convert_unicode=True))
  event_id = Column(Integer,ForeignKey("events.id"))

  event = relationship("Event", backref="worksheets" )

class Registration(Base):

  __tablename__ = 'registrations'

  id = Column(Integer,primary_key=True)
  datetime = Column(String(length=256, convert_unicode=True))
  member_id = Column(Integer,ForeignKey("members.id"),nullable=False)
  event_id = Column(Integer,ForeignKey("events.id"),nullable=False)
  joining_at = Column(Unicode(256))
  volunteer_for = Column(String(length=256, convert_unicode=True))
  selected = Column(String(length=60, convert_unicode=True))
  payment_status = Column(String(length=60, convert_unicode=True))
  bring_along = Column(String(length=60, convert_unicode=True))
  biketrip_joining_as = Column(String(length=60, convert_unicode=True))
  photographer = Column(Boolean)
  dropout = Column(Boolean)
  triathlon_event = Column(String(length=60, convert_unicode=True))
  swimming_batch = Column(String(length=256, convert_unicode=True))
  prev_experience = Column(UnicodeText)
  final_organizer_comments = Column(UnicodeText)

  member = relationship("Member", backref="registrations")
  event = relationship("Event", backref="registrations" )


if __name__ == '__main__':
  db_user="admin"
  db_password="admin"
  db_host="localhost"
  db_name="ctc"

  engine=create_engine('mysql://'+db_user+':'+db_password+'@'+db_host+'/'+db_name)
  Base.metadata.create_all(engine)

  
