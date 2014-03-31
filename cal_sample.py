import gdata.calendar.data
import gdata.calendar.client

class CalendarClient:
  def __init__(self, email, password):
    self.cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python_Sample-1.0')
    self.cal_client.ClientLogin(email, password, self.cal_client.source);

  def print_all_events():
    feed = self.cal_client.GetAllCalendarsFeed()
    print 'Printing allcalendars: %s' % feed.title.text
    for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
      print '\t%s. %s' % (i, a_calendar.title.text,)

if __name__ == '__main__':
  cal=CalendarClient("ctctrekkers@gmail.com", "nagala123");
  cal.print_all_events()    
