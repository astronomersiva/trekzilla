import gdata.docs.service
import gdata.spreadsheet.service
from xlrd import open_workbook
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from ctcdb_orm import *
import os, traceback, datetime
import logging


class DBhelper:
     def session(self):
        return self.sessionmaker()

     def __init__(self,db_type,db_host,db_member,db_password,db_name):
        self.engine=create_engine(db_type+"://"+db_member+":"+db_password+"@"+db_host+"/"+db_name)
        self.metadata=MetaData()
        self.sessionmaker = sessionmaker(bind=self.engine)     
        
class XLhelper:
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
          #session=dbhelper.session()
          registration = Registration( event_id = associated_event_id )
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
              if (header.startswith("name") or header=="full name" or header == "how we suppose to call u?" or header == "my name" or header == "participants") and new_member:
                member.name=s.cell(row,col).value 
              elif header.startswith("gender") and new_member:
                member.gender = str(s.cell(row,col).value).partition('/')[0].strip()
              elif header == "Age\gender" and new_member:
                member.gender = str(s.cell(row,col).value).partition('\\')[2].strip()
              elif header == "date of birth" or header == "when we can get treat from u ?":
                member.dob = str(s.cell(row,col).value)
              elif header == "id proof":
                member.id_proof = str(s.cell(row,col).value)
              elif header == "id proof number":
                member.id_proof_number = str(s.cell(row,col).value)
              elif( header=="profile link" or header=="profile" or header.find("fb")!=-1 or header.find("social network")!=-1 or header.find("facebook")!=-1 or header.find("social network")!=-1):
                member.fb_profile=str(s.cell(row,col).value)
              elif(header.find("contact")!=-1 or header.find("mobile")!=-1):
                member.contact=s.cell(row,col).value
              elif (header.find("contact")!=-1 or header.find("mobile")!=-1) and header.find("emergency")!=-1:
                member.emergency_contact = str(s.cell(row,col).value)
              elif header == "emergency contact person":
                member.emergency_contact_person = str(s.cell(row,col).value)
              elif header.startswith("swimming"):
                member.swimming_ability = s.cell(row,col).value
              elif header.find("camera") != -1 and header.find("you own")!=-1 :
                member.camera_model = str(s.cell(row,col).value)
              elif header.find("bike")!=-1 and header.find("model")!=-1 :
                member.bike_model = str(s.cell(row,col).value)
              elif header.find("cycle")!=-1 and header.find("model")!=-1 :
                member.cycle_model = str(s.cell(row,col).value)
              elif header.find("cycle")!=-1 and header.find("type")!=-1 :
                member.cycle_type = str(s.cell(row,col).value)
              elif header.startswith("bike registration number"):
                member.bike_registration_number = str(s.cell(row,col).value)
              elif header.find("blood group")!=-1 and header.find("blood group of your all participants")==-1:
                member.bloodgroup= str(s.cell(row,col).value)
              elif(header.startswith("joining at") or header =="i will join @" or header == "joining location" or header=="assembling point" or header == "pickup point" or header == "where would u like to join with us ?" or header.startswith("boarding")):
                registration.joining_at = s.cell(row,col).value
              elif header == "timestamp":
                registration.datetime = str(s.cell(row,col).value)
              elif header == "payment":
                registration.payment_status = str(s.cell(row,col).value)
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
              logging.exception("Error while adding registration " + str(registration.id ))
      except:
        logging.exception( "Error in "+file_name  )  


class GDataClient(object):
  
  def __init__(self,email,password,dbhelper):
    self.gd_client = gdata.docs.service.DocsService()
    self.gd_client.ClientLogin(email, password)

    self.gs_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gs_client.ClientLogin(email, password)

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
        except:
          logging.exception( "Exception while adding worksheet to db ", workseeth.name)
        added_ws = session.query(Worksheet).filter_by(gdata_resourceId = document_entry.resourceId.text ).first()
        doc_name = document_entry.title.text.lower()
        if doc_name.find("workshop") != -1 or doc_name.find("trek polamaa") != -1:
          event = Event( name = document_entry.title.text, category="workshop")
        elif doc_name.find("trek") != -1 or doc_name.find("emperors to javadhu hills") != -1 or doc_name.find("monsoon survival") != -1 or doc_name.find("nagala eastern adventure") != -1 or doc_name.find("venkatagiri") != -1 or doc_name.find("kumbakarai to kodaikanal") != -1 or doc_name.find("hike") != -1:
          event = Event( name = document_entry.title.text, category="trek")
          if doc_name.find("easy"):
            event.trek_difficulty = "easy"
          elif doc_name.find("moderate"):
            event.trek_difficulty = "moderate"          
          else:
            event.trek_difficulty = "difficult"  
        elif doc_name.find("walk of a lifetime")!= -1:  
            event = Event( name = document_entry.title.text, category="walk")
        elif doc_name.find("photography") != -1:
          event = Event( name = document_entry.title.text, category="photography_trip")      
        elif (doc_name.find("tree")!=-1 and doc_name.find("plantation") != -1) or (doc_name.find("seed")!=-1 and doc_name.find("sowing")!=-1 ):
          event = Event( name = document_entry.title.text, category="tree_plantation")
        elif doc_name.find("swimming") != -1 and doc_name.find("camp") != -1:
          event = Event( name = document_entry.title.text, category="swimming_camp")
          if doc_name.find("beginners"):
            event.swimming_level = "beginners"
          else:
            event.swimming_level = "advanced"         
        elif filename.find("coastalcleanup") != -1:
          event = Event( name = document_entry.title.text, category="coastal_cleanup")
        elif filename.find("marathon") != -1 or filename.find("completed_attendees"):
          event = Event( name = document_entry.title.text, category="marathon")
        elif filename.find("triathlon") != -1:
          event = Event( name = document_entry.title.text, category="triathlon")
        elif filename.find("workshop") != -1:
          event = Event( name = document_entry.title.text, category="workshop")
        elif filename.find("bike") != -1 or filename.find("bikers")!= -1 or filename.find("biking") != -1 or filename.find("ride") != -1 or filename.find("biketrip") != -1:
          event = Event( name = document_entry.title.text, category="bike_ride")
        elif filename.find("dailyrunning") != -1:
          event = Event( name = document_entry.title.text, category="daily_running")
        elif filename.find("cycling") != -1 or filename.find("cycletrip") != -1:
          event = Event( name = document_entry.title.text, category="cycling")
        elif filename.find("farmvisit") != -1:
          event = Event( name = document_entry.title.text, category="farm_visit")
        else:   
          event = Event( name = document_entry.title.text )
        try:
          session.add(event)
        except:
          logging.exception("could not add event ", event.name)
        try:
          added_event = session.query(Event).filter_by(name = document_entry.title.text ).first()
          added_ws.event = added_event
          session.commit()  
        except:
          logging.exception("error while adding event to worksheet ", added_ws.name)


def main():
  logging.basicConfig(filename = "ctc.log", level=logging.DEBUG)
  xlpath='/home/surya/workspace/python/ctc/'
  dbhelper=DBhelper(db_type="mysql",db_host="localhost",db_member="admin",db_password="admin",db_name="ctc")
  gdclient=GDataClient("ctctrekkers@gmail.com","nagala123",dbhelper)
  gdclient.downloadSpreadSheets(xlpath)

  spreadsheet_files = os.listdir(xlpath)
  for file in spreadsheet_files:
      xlhelper=XLhelper()
      if (file.endswith(".xlsx") or file.endswith(".xls")):
        xlhelper.openbook(xlpath+file,dbhelper)
      os.remove(xlpath+file)
    
  
  
if __name__ == '__main__':
  main()
