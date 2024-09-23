import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from flask_restful import Api, Resource
from datetime import datetime

service_account_base64 = os.getenv('FIREBASE_AUTH_CREDENTIALS')
service_account_json = base64.b64decode(service_account_base64).decode('utf-8')
service_account_info = json.loads(service_account_json)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
api = Api(app)

API_KEY = "klXJfkUSyMFuIevkzCDJ7cn5uUzrFCyT"

def apiKeyCheck(req):

    api_key = req.headers.get('x-api-key')
        
    return api_key == API_KEY

def updateDocument(collection_id, query, updated_values):

    collection_ref = db.collection(collection_id)

    query_ref = collection_ref.where(query[0], query[1], query[2])
    if not query_ref:
        return False
    
    docs = query_ref.stream()
    doc_updated = False

    for doc in docs:
        doc_ref = db.collection(collection_id).document(doc.id)

        doc_ref.update(updated_values)
        doc_updated = True

    return doc_updated

def getDocument(collection_id, query, values_to_get):

    collection_ref = db.collection(collection_id)

    query_ref = collection_ref.where(query[0], query[1], query[2])
    if not query_ref:
        return None

    docs = query_ref.stream()
    for doc in docs:
        query_result = {"id":doc.id}
        for value in values_to_get:
            query_result.update({value: doc.to_dict().get(value)})
        return query_result
    else:
        return None

class UpdateUserLocation(Resource):
    def post(self):
        if not apiKeyCheck(request):
            return {"Error":"Unauthorised access"},401
        
        data = request.json

        if not data:
            return {"Error":"No input data sent"},400
        if 'uid' not in data:
            return {"Error":"uid field not sent"},400
        if 'mac_address' not in data:
            return {"Error":"mac_address field not sent"},400
        if 'entry_time' not in data:
            return {"Error":"entry_time field not sent"},400    
        
        mac_address = data['mac_address']
        uid = data['uid']
        date_time = datetime.fromisoformat(data['entry_time'].replace("Z", "+00:00"))

        rfid_users = getDocument('rfid_users',('rfid_uid','==',data['uid']),('location','user_id','in_room'))
        if not rfid_users:
            return {"Error":"Invalid UID"},400
        previous_location = rfid_users['location']
        user_id = rfid_users['user_id']
        in_room = rfid_users['in_room']

        reader_mac_address = getDocument("rfid_reader_location",("reader_mac_address","==",mac_address),("location",))
        if not reader_mac_address:
            return {"Error":"Invalid MAC address"},400
        current_location = reader_mac_address['location']

        if(current_location != previous_location):
            in_room = True
        else:
            in_room = not in_room

        docUpdated = updateDocument('rfid_users',('user_id','==',user_id),{"location":current_location, "in_room":in_room, "last_location_entry":date_time})
        if not docUpdated:
            return {"Error":"Unexpected error occured"},400

        return {"Success":"User document updated"}, 200

class UpdateRFIDReaderOnlineTimestamp(Resource):
     
     def post(self):
        if not apiKeyCheck(request):
            return {"Error":"Unauthorised access"},401
        
        data = json.loads(request.json)

        if not data:
            return {"Error":"No input data sent"},400
        if 'last_online' not in data:
            return {"Error":"status_time field not sent"},400
        if 'mac_address' not in data:
            return {"Error":"mac_address field not sent"},400
        
        mac_address = data['mac_address']
        last_online = datetime.fromisoformat(data['last_online'].replace("Z", "+00:00"))

        docUpdated = updateDocument("rfid_reader_location",("reader_mac_address","==",mac_address),{"last_online":last_online})
        if not docUpdated:
            return {"Error":"Unexpected error occured"},400
        
        return {"Success":"last_online variable updated"}, 200
    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(UpdateUserLocation,"/update_user_location")
api.add_resource(UpdateRFIDReaderOnlineTimestamp,"/last_online")

app = app