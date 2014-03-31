import gdata.calendar.data
import gdata.calendar.client

class CalendarClient:
  def __init__(self, email, password):
    self.cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python_Sample-1.0')
    self.cal_client.ClientLogin(email, password, self.cal_client.source);

  def print_all_events(self):
    feed = self.cal_client.GetAllCalendarsFeed()
    print 'Printing allcalendars: %s' % feed.title.text
    for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, a_calendar.title.text,)
      print a_calendar.content.src
      
      query = gdata.calendar.client.CalendarEventQuery(start_min='2004-01-01', start_max='2034-01-01'
      feed = self.cal_client.GetCalendarEventFeed(a_calendar.content.src,q=query)
      print 'Events on Calendar: %s' % (feed.title.text,)
      for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
        print '\t%s. %s' % (i, an_event.title.text,)

  

if __name__ == '__main__':
  cal=CalendarClient("ctctrekkers@gmail.com", "nagala123");
  cal.print_all_events()    
