import gdata.docs.service
import gdata.spreadsheet.service
from xlrd import open_workbook
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from db_create import *
import os, traceback, datetime
import logging
from config import config
import re


class DBhelper:
     def session(self):
        session = self.sessionmaker()
        session._model_changes= {}
        return session

     def __init__(self,db_type,db_host,db_user,db_password,db_name):
        self.engine=create_engine(db_type+"://"+db_user+":"+db_password+"@"+db_host+"/"+db_name)
        self.metadata=MetaData()
        self.sessionmaker = sessionmaker(bind=self.engine)     
        
class XLhelper:

    def __init__(self):
      self.email_regex=re.compile("\S+@\S+.\S")
      self.bloodgroup_contact_regex=re.compile("([a-zA-z+]*)\s*([0-9]*)")

    def openbook(self,file_name,dbhelper):
      try:
        wb = open_workbook(file_name)
      except:
        logging.error("cannot open "+str(file_name))
        return
      try:
        session=dbhelper.session()
        try:
          associated_event_id=session.query(Worksheet).filter_by(filename = file_name ).first().event_id
          logging.info("Found Associated event id is "+str( associated_event_id))
        except:
          logging.error("Exception while fetching associated event id for "+str(file_name))
          associated_event_id=None
          traceback.print_exc() 
        email_col=-1
        new_member=True
        s = wb.sheets()[0]
        for col in range(s.ncols):          
          if str(s.cell(0,col).value).strip().lower().find("email")!=-1 or str(s.cell(0,col).value).strip().lower().find("e-mail")!= -1 or str(s.cell(0,col).value).strip().lower() == "mail id":
            email_col=col
        if email_col==-1:
           logging.info( "No email column so returning without doing anything for file "+str(file_name) )
           return
        for row in range(1,s.nrows):
          session=dbhelper.session()
          registration = Registration( event_id = associated_event_id )
          logging.info(" Initializing registration with event id "+ str(registration.event_id))
          if self.email_regex.search(s.cell(row,email_col).value) is None:
            continue
          try:
            member_count = session.query(Member).filter_by(email = s.cell(row,email_col).value ).count()
          except:
            logging.exception("cannot get member count")
            member_count = 0
            traceback.print_exc() 
          if member_count > 0:
            try:
              member=session.query(Member).filter_by(email = s.cell(row,email_col).value ).first()
              logging.info("found an existing member "+str(member.id))
              new_member=False
            except:
              logging.exception("cannot find member with mail id "+ s.cell(row,email_col).value)
              member = Member(email = s.cell(row,email_col).value)
              new_member=True 
              traceback.print_exc()  
          else:
            member = Member(email = s.cell(row,email_col).value)
            logging.info("going to add a new member")
            new_member=True
          try:
            for col in range(s.ncols):
              header=str(s.cell(0,col).value).strip().lower()
              if header.startswith("name") or header=="full name" or header == "how we suppose to call u?" or header == "my name" or header == "participants" or header.find("your name")!=-1 or header.find("your official name")!=-1:
                if member.name==None:
                   member.name=s.cell(row,col).value 
              elif header.find("gender")!=-1:
								value=str(s.cell(row,col).value)
								if value.find("female")!=-1:
									member.gender='female'
								elif value.find("male")!=-1:
									member.gender='male'
								else:
									member.gender=None
              elif header == "date of birth" or header == "when we can get treat from u ?":
                member.dob = str(s.cell(row,col).value)
              elif header == "id proof":
                member.id_proof = str(s.cell(row,col).value)
              elif header == "id proof number":
                member.id_proof_number = str(s.cell(row,col).value)
              elif( header=="profile link" or header=="profile" or header.find("fb")!=-1 or header.find("social network")!=-1 or header.find("facebook")!=-1 or header.find("social network")!=-1):
                if member.fb_profile==None:
                  member.fb_profile=s.cell(row,col).value
              elif header.find("contact")!=-1 or header.find("mobile")!=-1 or header.find("phone")!=-1:
                if member.contact==None:
                  member.contact=s.cell(row,col).value
              elif header == "emergency contact person":
                member.emergency_contact_person = str(s.cell(row,col).value)
              elif (header.find("contact")!=-1 or header.find("mobile")!=-1) and header.find("emergency")!=-1:
                if(header.find("blood group")==-1):
                  member.emergency_contact = s.cell(row,col).value
                else:
                  m=self.bloodgroup_contact_regex.match(s.cell(row,col).value)
                  member.bloodgroup=m.group(1)
                  member.emergency_contact = m.group(2)
              elif header.startswith("swimming"):
                member.swimming_ability = s.cell(row,col).value
              elif header.find("camera") != -1 and header.find("you own")!=-1 :
                member.camera_model = s.cell(row,col).value
              elif header.find("bike")!=-1 and header.find("model")!=-1 :
                member.bike_model = s.cell(row,col).value
              elif header.find("cycle")!=-1 and header.find("model")!=-1 :
                member.cycle_model = s.cell(row,col).value
              elif header.find("cycle")!=-1 and header.find("type")!=-1 :
                member.cycle_type = s.cell(row,col).value
              elif header.startswith("bike registration number"):
                member.bike_registration_number = s.cell(row,col).value
              elif header.find("blood group")!=-1 and header.find("blood group of your all participants")==-1:
                member.bloodgroup= s.cell(row,col).value
              elif(header.startswith("joining at") or header =="i will join @" or header == "joining location" or header=="assembling point" or header == "pickup point" or header == "where would u like to join with us ?" or header.startswith("boarding")):
                registration.joining_at = s.cell(row,col).value
              elif header == "timestamp":
                registration.datetime = str(s.cell(row,col).value)
              elif header == "payment":
                registration.payment_status = s.cell(row,col).value
              elif header == "organizer's comment":
                registration.final_organizer_comments = str(s.cell(row,col).value)
              elif header.startswith("coming as"):
                registration.biker = str(s.cell(row,col).value)
              elif header in ["volunteering","volunteer for", "i wish to volunteer", "i can volunteer", "contribution"]:
                registration.volunteer_for = s.cell(row,col).value
              elif header in ["ctc experience", "ctc moderate/difficult trek experience", "experience"] or header.find("mention the treks done in past six months")!= -1 or (header.find("treks completed")!= -1 and header.find("past")!= -1 ) or header.find("trekking experience")!= -1:
                registration.prev_experience = s.cell(row,col).value
              elif header.find("batch")!= -1:
                registration.swimming_batch = str(s.cell(row,col).value)
              elif header=="selection" or header.startswith("shortlist?") or header == "status" or header == "call status" :
                registration.selected=s.cell(row,col).value
              elif header.startswith("i can bring") or header=="transport" or header.startswith("coming by") :
                registration.bring_along=s.cell(row,col).value
              else:
                  pass
            #session=dbhelper.session()
            if new_member:
              try:
                session.add(member)
                session.commit()
              except:
                logging.exception("Error while adding member ",member.id)
                traceback.print_exc() 
                session.rollback()
                continue
          except:
                logging.exception("Error while header loop for " + str(header) + " for "+ str(member.id) +":"+ str(member.name) +" in "+ str(file_name))
          #session=dbhelper.session()
          try:
            added_member = session.query(Member).filter_by(email = s.cell(row,email_col).value ).first()
            registration.member_id = added_member.id
          except:
            logging.exception("error while retrieving member for email ",s.cell(row,email_col).value)
            traceback.print_exc() 
            continue          
          try:
            session.add(registration)
            session.commit()
          except:
            logging.exception("Error while adding registration " + str(registration.id )+ " for file "+file_name)
            session.rollback()
      except:
        logging.exception( "Error in "+file_name  )  


class GDataClient(object):
  
  def __init__(self,email,password,dbhelper):
    self.gd_client = gdata.docs.service.DocsService()
    self.gs_client = gdata.spreadsheet.service.SpreadsheetsService()
    for tries in range(10):
      try:
        self.gd_client.ClientLogin(email, password)   
        break
      except:
        logging.critical("Trying to do client login again")
    for tries in range(10):
      try:
        self.gs_client.ClientLogin(email, password)
        break
      except:
        logging.critical("Trying to do client login again")        

    self.dbhelper = dbhelper

  def str_replace_with_none(self,string,arr):
    for char in arr:
      string=string.replace(char,"")
    return string

  def strip_non_alnum(self, string):
    new_str=""
    for ch in string:
      if ch.isalnum():
        new_str=new_str+ch
    return new_str

  def downloadSpreadSheets(self,file_path):
    documents_feed = self.gd_client.GetDocumentListFeed()
    session=self.dbhelper.session()
    resource_ids = [a[0] for a in session.query(Worksheet.gdata_resourceId).all()]
    for document_entry in documents_feed.entry:
      if document_entry.GetDocumentType()=="spreadsheet" and document_entry.resourceId.text not in resource_ids:
        logging.info("Downloading "+document_entry.title.text)
        docs_token = self.gd_client.GetClientLoginToken()
        self.gd_client.SetClientLoginToken(self.gs_client.GetClientLoginToken())
        tries=0
        for tries in range(10):
          try:
            self.gd_client.Export(document_entry, file_path+self.strip_non_alnum(document_entry.title.text)+".xlsx")
            break
          except:
            logging.critical("Could not download worksheet Trying again "+document_entry.title.text)
            if tries == 9:
              logging.error("cannot connect now. stopping download")
              return          
        self.gd_client.SetClientLoginToken(docs_token)
        worksheet = Worksheet( name = document_entry.title.text, gdata_resourceId = document_entry.resourceId.text , filename = file_path+self.strip_non_alnum(document_entry.title.text)+".xlsx" )
        filename=file_path+self.strip_non_alnum(document_entry.title.text).lower()
        session=self.dbhelper.session()
        try:
          session.add(worksheet)
          session.commit()
        except:
          logging.exception( "Exception while adding worksheet to db ", workseeth.name)
          session.rollback()
          continue
        added_ws = session.query(Worksheet).filter_by(gdata_resourceId = document_entry.resourceId.text ).first()
        doc_name = document_entry.title.text.lower()
        event_name = document_entry.title.text
        if doc_name.find("workshop") != -1 or doc_name.find("trek polamaa") != -1 or doc_name.find("training")!=-1:
          event = Event( name = document_entry.title.text, category="workshop")
        elif doc_name.find("treasure hunt") != -1:
          event = Event( name = document_entry.title.text, category="treasure_hunt")
        elif doc_name.find("trek") != -1 or doc_name.find("emperors to javadhu hills") != -1 or doc_name.find("mission")!=-1 or doc_name.find("monsoon survival") != -1 or doc_name.find("nagala") != -1 or doc_name.find("venkatagiri") != -1 or doc_name.find("kumbakarai to kodaikanal") != -1 or doc_name.find("hike") != -1 or doc_name.find("nagari") != -1 or doc_name.find("venkateswara")!=-1 or doc_name.find("ombatu gudda")!=-1 or doc_name.find("wild west")!=-1:
          if doc_name.find("social")!=-1:
            event = Event( name = event_name, category="social_trek")
          else:
            event = Event( name = event_name, category="trek")
            if doc_name.find("easy")!=-1:
              event.trek_difficulty = "easy"
            elif doc_name.find("moderate")!=-1:
              event.trek_difficulty = "moderate"          
            else:
              event.trek_difficulty = "difficult"
        elif doc_name.find("weekend getaway")!=-1 or doc_name.find("tour")!=-1:
            event = Event( name = event_name, category="tour")            
        elif doc_name.find("social")!=-1 or doc_name.find("saranalayam")!=-1:
            event = Event( name = event_name, category="social")
        elif doc_name.find("walk") != -1:
          if doc_name.find("bird") !=-1:
            event = Event( name = event_name, category="bird_watching")
          elif doc_name.find("snake") != -1:
            event = Event( name = event_name, category="snake_watching")
          else:
            event = Event( name = event_name, category="walk")           
        elif doc_name.find("walk of a lifetime")!= -1:  
            event = Event( name = event_name, category="walk")
        elif doc_name.find("photography") != -1:
          event = Event( name = event_name, category="photography_trip")      
        elif (doc_name.find("tree")!=-1 and doc_name.find("plantation") != -1) or (doc_name.find("seed")!=-1 and doc_name.find("sowing")!=-1 ):
          event = Event( name = event_name, category="tree_plantation")
        elif doc_name.find("swimming") != -1 and doc_name.find("camp") != -1:
          event = Event( name = event_name, category="swimming_camp")
          if doc_name.find("beginners")!=-1:
            event.swimming_level = "beginners"
          else:
            event.swimming_level = "advanced"  
        elif doc_name.find("beach busters")!=-1:
          event = Event( name = event_name, category="beach_busters")  
        elif doc_name.find("sea dive")!=-1:
          event = Event( name = event_name, category="sea_dive")                
        elif filename.find("coastalcleanup") != -1:
          event = Event( name = event_name, category="coastal_cleanup")
        elif filename.find("marathon") != -1 or filename.find("completed_attendees")!=-1:
          event = Event( name = event_name, category="marathon")
        elif filename.find("triathlon") != -1:
          event = Event( name = event_name, category="triathlon")
        elif doc_name.find("suv") != -1:
          event = Event( name = event_name, category="suv_trip")
        elif filename.find("bike") != -1 or filename.find("bikers")!= -1 or filename.find("biking") != -1 or filename.find("ride") != -1 or filename.find("biketrip") != -1 or doc_name.find("kick start") != -1 or doc_name.find("wheels")!=-1:
          event = Event( name = event_name, category="bike_ride")
        elif filename.find("dailyrunning") != -1:
          event = Event( name = event_name, category="daily_running")
        elif filename.find("cycling") != -1 or filename.find("cycletrip") != -1:
          event = Event( name = event_name, category="cycling")
        elif filename.find("farmvisit") != -1:
          event = Event( name = event_name, category="farm_visit")
        else:   
          event = Event( name = event_name )
        try:
          session.add(event)
        except:
          logging.exception("could not add event ", event.name)

        acl_query = gdata.docs.service.DocumentAclQuery(document_entry.resourceId.text)
        acl_feed = self.gd_client.GetDocumentListAclFeed(acl_query.ToUri())
        owners = [a.scope.value for a in acl_feed.entry if a.role.value == 'owner' ]
        if len(owners)>0:
          owner_email=owners[0]
          if session.query(Member).filter_by(email = owner_email ).count() == 0:
            session.add(Member(email = owner_email ))
          owner_member = session.query(Member).filter_by(email = owner_email ).first()
          owner_member.is_organizer=True
          event.primary_organizer_id = owner_member.id
        """
        organizers =  owners + [a.scope.value for a in acl_feed.entry if a.role.value == 'writer' ]
        for organizer_email in organizers:
          if session.query(Member).filter_by(email = organizer_email ).count() == 0:
            session.add(Member(email = organizer_email ))
          organizer_member = session.query(Member).filter_by(email = organizer_email ).first()
          event.organizers.append(organizer_member)
        """

        try:
          added_event = session.query(Event).filter_by(name = document_entry.title.text ).first()
          added_ws.event = added_event
          session.commit()  
        except:
          logging.exception("error while adding event to worksheet ", added_ws.name)
          session.rollback()


def main():
  logging.basicConfig(filename = "ctc.log", level=logging.DEBUG)
  xlpath=config.XL_PATH
  dbhelper=DBhelper(db_type=config.DBTYPE,db_host=config.DBHOST,db_user=config.DBUSER,db_password=config.DBPASSWD,db_name=config.DBNAME)
  gdclient=GDataClient(config.CTC_EMAIL,config.CTC_EMAIL_PASSWORD,dbhelper)
  gdclient.downloadSpreadSheets(xlpath)

  spreadsheet_files = os.listdir(xlpath)
  for file in spreadsheet_files:
      xlhelper=XLhelper()
      if (file.endswith(".xlsx") or file.endswith(".xls")):
        xlhelper.openbook(xlpath+file,dbhelper)
      os.remove(xlpath+file)
    
  
  
if __name__ == '__main__':
  main()
