# oauth_demo.py
#
# Corey Savage
# CS 496
#
# OAuth 2.0 Web Client Demo  
# Demonstrates a basic website with OAuth 2.0 authentication
#

import jinja2
import urllib2
import urllib
import os
import logging
import webapp2
import json
from google.appengine.ext import ndb
from webapp2_extras import sessions
from google.appengine.api import urlfetch

import string
import random
chars = string.letters + string.digits
chars = string.letters + string.digits + string.punctuation
pwdSize = 32
key = ''.join((random.choice(chars)) for x in range(pwdSize))

secret_key = key

jinja_environment = jinja2.Environment(
   loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
   autoescape = True)

class OauthHandler(webapp2.RequestHandler):
    def get(self):
        code = self.request.get('code')
        data_to_post = {
            'code': code,
            'client_id':'838080691485-jf0lut0oq1tdirerhoa9tc7lf3roard3.apps.googleusercontent.com',
            'redirect_uri':'https://oauth2demo-167110.appspot.com/oauth',
            'client_secret':'kXaXyMr8ssNNZkzpRWdzUw3-',
            'grant_type': 'authorization_code' }
        # Send encoded data to application-2
        try:
            form_data = urllib.urlencode(data_to_post)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            result = urlfetch.fetch(
                url='https://www.googleapis.com/oauth2/v4/token',
                payload=form_data,
                method=urlfetch.POST,
                headers=headers)

            try:
                results_json = json.loads(result.content)
                token = results_json['access_token']
                authorizeString = 'Bearer ' + token
                plus_header = {'Authorization': authorizeString}
                user_info = urlfetch.fetch(
                    url='https://www.googleapis.com/plus/v1/people/me',
                    payload=None,
                    method=urlfetch.GET,
                    headers=plus_header)


                results_json = json.loads(user_info.content)
                userName = results_json['displayName']
                userURL = results_json['url']
                url='https://oauth2demo-167110.appspot.com'
                user_data_to_post = urllib.urlencode({
                    'displayName': userName,
                    'url': userURL
                })
                try:
                    address = url + '?' + user_data_to_post
                    self.redirect(address)
                except urllib2.URLError:
                    logging.exception('Caught exception fetching url')

            except urlfetch.Error:
                logging.exception('Caught exception fetching url')

        except urlfetch.Error:
            logging.exception('Caught exception fetching url')


class MainPage(webapp2.RequestHandler):
    def get(self):
        if self.request.get('displayName'):
            userName = self.request.get('displayName')
            userURL = self.request.get('url')
            template_values = {
                'greeting':'Well Done, ',
                'userName':userName,
                'userURL':userURL,
                'secret_key':secret_key
            }
            template = jinja_environment.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            template_values = {
                'greeting':'Welcome, Stranger',
                'guest':'True'
            }
            template = jinja_environment.get_template('index.html')
            self.response.write(template.render(template_values))

    def post(self, displayName=None):
        url = 'https://accounts.google.com/o/oauth2/v2/auth'
        data = urllib.urlencode({'response_type':'code',
                                'client_id':'838080691485-jf0lut0oq1tdirerhoa9tc7lf3roard3.apps.googleusercontent.com',
                                'redirect_uri':'https://oauth2demo-167110.appspot.com/oauth',
                                'scope':'email',
                                'state': secret_key})
        try:
            address = url + '?' + data
            self.redirect(address)
        except urllib2.URLError:
            logging.exception('Caught exception fetching url')




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)