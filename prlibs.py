from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')

from flask_flatpages import FlatPages
pages = FlatPages(app)

@app.route('/')
def index():
   return pages.get_or_404('index').body

if __name__ == "__main__":
   app.run()
