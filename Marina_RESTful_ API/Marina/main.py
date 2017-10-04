# main.py
#
# Corey Savage
# CS 496
#
# Marina Traffic API  
# Demonstrates an API for managing Marina boats and slips, utilizing Google Cloud Platform. 
# View readme for user documentation 
#

import webapp2
from google.appengine.ext import ndb
import json
import datetime

def getDateTime():
    now = datetime.datetime.today().strftime("%Y/%m/%d")
    return now

# Parent - Marina_Boats
class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    classification = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty(default=True)

# Parent - Marina_Slips
class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
    departure_history = ndb.JsonProperty(repeated=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Marina Traffic API\nServer: Google Cloud Platform\nDatabase: Google NDB Client\n\nCorey Savage')

class BoatHandler(webapp2.RequestHandler):
    # POST /boats - Add new boat to database
    def post(self):
        parent_key = ndb.Key(Boat, "Marina_Boats")
        boat_data = json.loads(self.request.body)
        if boat_data.get('classification'):
            new_boat = Boat(name=boat_data['name'], classification=boat_data['classification'], parent=parent_key)    
        else:
            new_boat = Boat(name=boat_data['name'], parent=parent_key)
        new_boat.put()
        if boat_data.get('length'):
            new_boat.length = boat_data['length']
            new_boat.put()
        new_boat.id = new_boat.key.urlsafe()
        new_boat.put()
        boat_dict = new_boat.to_dict()
        # URL for individual boats
        boat_dict['self'] = '/boat/' + new_boat.id
        self.response.write(json.dumps(boat_dict))

    def get(self, id=None):
        # GET /boat/{boat_id} - Individual boat information
        if id:
            specific_boat = ndb.Key(urlsafe=id).get()
            specific_boat_dict = specific_boat.to_dict()
            self.response.write(json.dumps(specific_boat_dict))
        # GET /boats - All boats list
        else:
            allBoats = Boat.query().fetch()
            self.response.write(allBoats)

    # PATCH /boat/{boat_id} - Modify existing boat
    def patch(self, id=None):
        if id:
            patch_boat_data = json.loads(self.request.body)
            specific_boat = ndb.Key(urlsafe=id).get()
            if patch_boat_data.get('at_sea'):
                self.response.write("at_sea: Error 405 - Method not allowed. Check readme for acceptable requests\nResuming Patch Request..\n\n")
            if patch_boat_data.get('name'):
                specific_boat.name = patch_boat_data['name']
                specific_boat.put()
                self.response.write("Updated boat name\n")
            if patch_boat_data.get('classification'):
                specific_boat.classification = patch_boat_data['classification']
                specific_boat.put()
                self.response.write("Updated boat type\n")
            if patch_boat_data.get('length'):
                specific_boat.length = patch_boat_data['length']
                specific_boat.put()
                self.response.write("Updated boat length\n")
            specific_boat_dict = specific_boat.to_dict()
            self.response.write(json.dumps(specific_boat_dict))
        else:
            self.abort(400)

    # PUT /boat/{boat_id} - Replaces boat
    def put(self, id=None):
        if id:
            put_boat_data = json.loads(self.request.body)
            specific_boat = ndb.Key(urlsafe=id).get()
            if put_boat_data.get('at_sea'):
                self.response.write("at_sea: Error 405 - Method not allowed. Check readme for acceptable requests\nResuming Put Request..\n\n")
            if put_boat_data.get('name'):
                specific_boat.name = put_boat_data['name']
                specific_boat.put()
            else:
                self.abort(400)
            if put_boat_data.get('classification'):
                specific_boat.classification = put_boat_data['classification']
                specific_boat.put()
            else:
                specific_boat.classification = None
                specific_boat.put()
            if put_boat_data.get('length'):
                specific_boat.length = put_boat_data['length']
                specific_boat.put()
            else:
                specific_boat.length = None
                specific_boat.put()
            specific_boat_dict = specific_boat.to_dict()
            self.response.write(json.dumps(specific_boat_dict))
        else:
            self.abort(400)

    # DELETE /boat/{boat_id} - Remove boat
    def delete(self, id=None):
        if id:
            specific_boat = ndb.Key(urlsafe=id).get()
            slip_search = Slip.query(Slip.current_boat == id)
            slip_remove_boat = slip_search.get()
            if slip_remove_boat:
                slip_remove_boat.current_boat = None
                slip_remove_boat.put()
                slip_remove_boat.arrival_date = None
                slip_remove_boat.put()
            specific_boat.key.delete()
            self.response.write("Boat Removed From Database")





class SlipHandler(webapp2.RequestHandler):
    # POST /slips - Add new slip to database
    def post(self):
        parent_key = ndb.Key(Slip, "Marina_Slips")
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data['number'], parent=parent_key)
        new_slip.put()
        new_slip.id = new_slip.key.urlsafe()
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.id
        self.response.write(json.dumps(slip_dict))

    def get(self, id=None):
        # GET /slip/{slip_id} - Individual slip information
        if id:
            specific_slip = ndb.Key(urlsafe=id).get()
            specific_slip_dict = specific_slip.to_dict()
            specific_slip_dict['departure'] = "/slip/" + id + "/departure"
            specific_slip_dict['arrival'] = "/slip/" + id + "/arrival"
            self.response.write(json.dumps(specific_slip_dict))
        # GET /slips - All slips list
        else:
            allSlips = Slip.query().fetch()
            self.response.write(allSlips)

    # PATCH /slip/{slip_id} - Modify existing slip
    def patch(self, id=None):
        if id:
            patch_slip_data = json.loads(self.request.body)
            specific_slip = ndb.Key(urlsafe=id).get()
            if patch_slip_data.get('number'):
                specific_slip.number = patch_slip_data['number']
                specific_slip.put()
                self.response.write("Updated slip number\n")
            specific_slip_dict = specific_slip.to_dict()
            self.response.write(json.dumps(specific_slip_dict))

    # PUT /slip/{slip_id} - Replace existing slip
    def put(self, id=None):
        if id:
            put_slip_data = json.loads(self.request.body)
            specific_slip = ndb.Key(urlsafe=id).get()
            if put_slip_data.get('number'):
                specific_slip.number = put_slip_data['number']
                specific_slip.put()
            else:
                self.abort(400)
            specific_slip.departure_history = []
            specific_slip.put()
            specific_slip_dict = specific_slip.to_dict()
            self.response.write(json.dumps(specific_slip_dict))

    # DELETE /slip/{slip_id} - Remove slip
    def delete(self, id=None):
        if id:
            specific_slip = ndb.Key(urlsafe=id).get()
            if Boat.query(specific_slip.current_boat == Boat.id):
                boat_search = Boat.query(specific_slip.current_boat == Boat.id)
                boat_to_sea = boat_search.get()
            if boat_to_sea:
                boat_to_sea.at_sea = True
                boat_to_sea.put()
            specific_slip.key.delete()
            self.response.write("Slip Removed From Database")

    


class ArrivalHandler(webapp2.RequestHandler):
    # PUT /slip/{slip_id}/arrival - Manages boats arriving to slips
    def put(self, id=None):
        if id:
            arrival_data = json.loads(self.request.body)
            specific_slip = ndb.Key(urlsafe=id).get()
            specific_slip.number
            specific_slip.put()
            # Check if slip is empty
            if not(specific_slip.current_boat):
                specific_slip.current_boat = arrival_data['boat_id']
                specific_slip.put()
                specific_slip.arrival_date = getDateTime()
                specific_slip.put()
                specific_slip_dict = specific_slip.to_dict()
                self.response.write(json.dumps(specific_slip_dict))
                boat_search = Boat.query(Boat.id == arrival_data['boat_id'])
                boat_docking = boat_search.get()
                boat_docking.at_sea = False
                boat_docking.put()
                boat_docking_dict = boat_docking.to_dict()
                self.response.write("\n" + json.dumps(boat_docking_dict))

            # If slip is already occupied by boat - Error 403
            else:
                self.abort(403)

class DepartureHandler(webapp2.RequestHandler):
    # PUT /slip/{slip_id}/departure - Manages boats departing from slips
    def put(self, id=None):
        if id:
            #departure_data = json.loads(self.request.body)
            specific_slip = ndb.Key(urlsafe=id).get()
            specific_slip.number
            specific_slip.put()
            if specific_slip.current_boat:
                boat_search = Boat.query(Boat.id == specific_slip.current_boat)
                boat_departing = boat_search.get()
                specific_slip.departure_history = specific_slip.departure_history + [{"departure_date": getDateTime(), "departed_boat": boat_departing.id}]
                
                boat_departing.at_sea = True
                boat_departing.put()
                boat_departing_dict = boat_departing.to_dict()

                specific_slip.current_boat = None
                specific_slip.put()
                specific_slip.arrival_date = None
                specific_slip.put()
                specific_slip_dict = specific_slip.to_dict()

                self.response.write(json.dumps(specific_slip_dict))
                self.response.write("\n" + json.dumps(boat_departing_dict))

            # If slip has no boat to depart - Error 404
            else:
                self.abort(404)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/slips', SlipHandler),
    ('/slip/(.*)/arrival', ArrivalHandler),
    ('/slip/(.*)/departure', DepartureHandler),
    ('/slip/(.*)', SlipHandler)
], debug=True)

