from flask import Flask
from flask import request
app = Flask(__name__)
app.config.from_pyfile('config.py')

from flask_flatpages import FlatPages
pages = FlatPages(app)

import random
import simplejson
import stripe

title = [
   [
      {
         't': '{0}, a company like {1} for {2}, launches new endeavour',
         'v': ['company', 'similiar_company', 'NNS'],
         'p': False
      },
      {
         't': '{0}, backed by {1}, pivots from {2} to focus on {3} {4}',
         'v': ['company', 'full_name', 'NNS', 'VB', 'NNS'],
         'p': False
      },   
   ]
]

content = [
   [
      {
         't': '{0}, the startup that allows you to {1} {2} {3}, officially opened its doors today. The startup seeks to {4} {5} by {6} {7} {8}.',
         'v': ['company', 'VB', 'JJ,JJR', 'NNS', 'VB', 'NNS', 'VBG', 'JJ,JJR', 'NNS'],
      },
   ],
   [
      {
         't': '{0} makes it easy to {1} {2} without having to {3} {4} or {5} {6}.',
         'v': ['company', 'VB', 'NNS', 'VB', 'NNS', 'VB', 'NNS'],
      },
   ],
   [
      {
         't': 'Insider {0} said "{1} helps {2} by letting them {3} {4} {5}."',
         'v': ['full_name', 'company', 'NNS', 'RB', 'VB', 'NNS'],
      },
   ],
   [
      {
         't': 'Next up for {0} is to {1} the {2} and {3} the {4}.',
         'v': ['company', 'VB', 'NNS', 'VB', 'NNS'],
      },
   ],
   [
      {
         't': 'One early customer told us that {0} had already helped solve his companies {1} problem.',
         'v': ['company', 'NNS'],
      }
   ]
]

@app.route('/')
def index():
   html = pages.get_or_404('index').body
   html = html.replace("{{STATIC_URL}}", app.config['STATIC_URL'])
   html = html.replace("{{STRIPE_PUB_KEY}}", app.config['STRIPE_PUB_KEY'])
   html = html.replace("{{NOCC}}", "")
   return html

   STATIC_URL

@app.route('/nocc')
def nocc():
   html = pages.get_or_404('index').body
   html = html.replace("{{STATIC_URL}}", app.config['STATIC_URL'])
   html = html.replace("{{STRIPE_PUB_KEY}}", app.config['STRIPE_PUB_KEY'])
   html = html.replace("{{NOCC}}", "hide")
   return html

@app.route('/success')
def success():
   html = pages.get_or_404('success').body
   html = html.replace("{{STATIC_URL}}", app.config['STATIC_URL'])
   html = html.replace("{{STRIPE_PUB_KEY}}", app.config['STRIPE_PUB_KEY'])
   html = html.replace("{{NOCC}}", "")
   return html

@app.route('/generate')
def generate():

   try:

      # imports
      import requests
      import nltk
      import lxml
      from lxml.html.clean import clean_html
      data = {}
      text = ""

      # fetch url, strip data down to just text
      url = request.args.get('url', None)
      if url:
         r = requests.get(url)
         if r.status_code != requests.codes.ok:
            raise Exception('Could not get content from URL ('+r.status_code+')')
         t = lxml.html.fromstring(r.content)
         t = clean_html(t)
         text += t.text_content()

      # combine with hand passed text
      text += request.args.get('text', '')
      text = text.encode('utf-8')

      # naive replacing to help the tokenizer
      text = text.replace("n't ", " not ")

      # tokenize text into part of speech
      tokens = nltk.word_tokenize(text)
      t = nltk.Text(tokens)
      all_tags = nltk.pos_tag(t)
      #print ' '.join('%s %s' % x for x in all_tags)

      # combine tags with query params
      for k in request.args.keys():
         v = request.args.get(k, None)
         all_tags.append((v, k))

      data['title'] = gen(title, all_tags, request)
      data['content'] = gen(content, all_tags, request)

      nocc = request.args.get('nocc', None)
      if not nocc:
         # cool it all worked, so lets charge the CC now
         token = request.args.get('token', None)
         if not token:
            raise Exception('Missing CC details.')

         stripe.api_key = app.config['STRIPE_API_KEY']
         stripe.Charge.create(
           amount=500,
           currency="usd",
           card=token,
           description="prlibs.com Starup PR Generator"
         )

   except Exception as error:
      data['error'] = '(card not charged) {0}'.format(error)
      return (simplejson.dumps(data), 400)

   return (simplejson.dumps(data), 200)

def gen(sentences, all_tags, request):
   final = ""
   # loop over all sentenced, replace in part of speech, output final string
   for sentence_choices in sentences:
      # sentence_choices is an array of sentence. one should be picked
      # do replacements on all sentences and randomly choose one
      replaced_choices = []
      for sentence in sentence_choices:
         replacements = []
         for tags in sentence['v']:
            tags = tags.split(',')
            for tag in tags:
               matches = find_tags(all_tags, tag)
               if len(matches) > 0:
                  r = random.choice(matches)
                  replacements.append(r)
                  break
         if len(replacements) == len(sentence['v']):
            replaced = sentence['t'].format(*replacements)
            replaced += "\n\n"
            replaced_choices.append(replaced)

      if len(replaced_choices) == 0:
         raise Exception('Not enough content at URL (or extras) to generate from.')
      else:
         final += random.choice(replaced_choices)

   return final

def find_tags(all_tags, search):
   """ given a list of nltk tags, find a specific tag <string> and return an array of all matching """
   matching = []
   for tag in all_tags:
      if tag[1] == search:
         matching.append(tag[0])
   return matching

if __name__ == "__main__":
   app.run(host='192.168.56.10')