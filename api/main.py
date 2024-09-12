import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from flask_restful import Api, Resource

service_account_base64 = os.getenv('FIREBASE_AUTH_CREDENTIALS')
service_account_json = base64.b64decode(service_account_base64).decode('utf-8')
service_account_info = json.loads(service_account_json)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

app = Flask(__name__)
api = Api(app)

API_KEY = "klXJfkUSyMFuIevkzCDJ7cn5uUzrFCyT"

def apiKeyCheck(req):

    api_key = req.headers.get('x-api-key')
    return api_key == API_KEY

class getUserFromUID(Resource):
    def get(self):
        collection_ref = db.collection('rfid_users')

        query_ref = collection_ref.where("rfid", "==", "AAAAAAAA")
        docs = query_ref.stream()

        docs_list = list(docs)
        if docs_list:
            doc = docs_list[0]
            return {
                "id": doc.id,
                "user_id": doc.to_dict().get('user_id')
            }
        else:
            return {"error": "No matching document found"}, 404
        
class getRoomFromMACAddress(Resource):
    def get(self):
        collection_ref = db.collection('rfid_reader_location')

        query_ref = collection_ref.where("reader_mac_address", "==", "1234")
        docs = query_ref.stream()

        docs_list = list(docs)
        if docs_list:
            doc = docs_list[0]
            return {
                "id": doc.id,
                "location": doc.to_dict().get('location')
            }
        else:
            return {"error": "No matching document found"}, 404
        
class sendScannedUID(Resource):
    def get(self):
        if not apiKeyCheck(request):
            return {"error": "Unauthorized access"}, 401
        
        data = request.json
        if not data:
            return {"error": "Bad Request, No data in request"}, 400
        if 'uid' not in data:
            return {"error": "Bad Request, Tag uid not in request"}, 400
        if 'mac address' not in data:
            return {"error": "Bad Request, MAC Address not in request"}, 400
        
        return data, 200

    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(getUserFromUID, "/getUserFromUID")
api.add_resource(getRoomFromMACAddress, "/getRoomFromMACAddress")
api.add_resource(sendScannedUID,  "/track_update")

app = app