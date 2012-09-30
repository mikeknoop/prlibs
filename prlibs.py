from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')

from flask_flatpages import FlatPages
pages = FlatPages(app)

@app.route('/')
def index():
   return pages.get_or_404('index').body

@app.route('/success')
def generate():
   return pages.get_or_404('success').body

@app.route('/test')
def test():
   import requests
   import nltk
   import lxml
   from lxml.html.clean import clean_html
   r = requests.get('https://zapier.com/blog')
   t = lxml.html.fromstring(r.content)
   t = clean_html(t)
   text = t.text_content()
   text = text.encode('utf-8')
   tokens = nltk.word_tokenize(text)
   t = nltk.Text(tokens)
   tags = nltk.pos_tag(t)
   return '[%s]' % ', '.join(map(str, tags))

if __name__ == "__main__":
   app.run(host='192.168.56.10')