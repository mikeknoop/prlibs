from flask import Flask
app = Flask(__name__)
from flask_flatpages  import FlatPages

#DEBUG = True
#FLATPAGES_AUTO_RELOAD = DEBUG
#FLATPAGES_EXTENSION = '.html'

#pages = FlatPages(app)

@app.route("/")
def index():
     return "Hello World"
#    return pages.get_or_404('static/index').html

#@app.route('/<path:path>/')
#def page(path):
#    return pages.get_or_404('static/'+path).html

if __name__ == "__main__":
    app.run()
