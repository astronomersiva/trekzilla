from flask import Flask
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView
from db_create import *

app = Flask(__name__)

admin = Admin(app, name="Trekzilla")
admin.add_view(ModelView(Member, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Registration, db.session))

@app.route('/')
def index():
  return 'CTC Trek Data'

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')



if __name__ == '__main__':
  app.run()
