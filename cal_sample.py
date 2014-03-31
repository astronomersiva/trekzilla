import gdata.calendar.data
import gdata.calendar.client

class CalendarClient:
  def __init__(self, email, password):
    self.cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python_Sample-1.0')
    self.cal_client.ClientLogin(email, password, self.cal_client.source);

  def print_all_events(self):
    feed = self.cal_client.GetCalendarEventFeed()
    print 'Events on Primary Calendar: %s' % (feed.title.text,)
    for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, an_event.title.text,)
      for p, a_participant in zip(xrange(len(an_event.who)), an_event.who):
        print '\t\t%s. %s' % (p, a_participant.email,)
        print '\t\t\t%s' % (a_participant.value,)
        if a_participant.attendee_status:
          print '\t\t\t%s' % (a_participant.attendee_status.value,)
  

if __name__ == '__main__':
  cal=CalendarClient("ctctrekkers@gmail.com", "nagala123");
  cal.print_all_events()    
