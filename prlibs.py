from flask import Flask
from flask_flatpages  import FlatPages

FLATPAGES_EXTENSION = '.html'

app = Flask(__name__)
pages = FlatPages(app)

@app.route("/")
def index():
   return pages.get_or_404('static/index').html

@app.route('/<path:path>/')
def page(path):
   return pages.get_or_404('static/'+path).html

if __name__ == "__main__":
   app.run()