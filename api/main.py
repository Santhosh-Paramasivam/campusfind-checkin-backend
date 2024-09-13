import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from flask_restful import Api, Resource
from google.cloud.exceptions import NotFound

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
    # Step 2: Debug the headers to ensure the API key is sent
    api_key = req.headers.get('x-api-key')
        
    return api_key == API_KEY

def updateDocument(collection_id, query, updated_values):

    collection_ref = db.collection(collection_id)

    try:
        # Query the Firestore collection with the provided query
        query_ref = collection_ref.where(query[0], query[1], query[2])
        docs = query_ref.stream()
    except (NotFound) as e:
        # Log or handle specific Firestore exceptions
        print(f"Error during query: {e}")
        return {"success": False, "message": "Invalid query or document not found."}, 400

    docs = query_ref.stream()

    doc_updated = False

    for doc in docs:
        doc_ref = db.collection(collection_id).document(doc.id)

        doc_ref.update(updated_values)
        doc_updated = True

    return doc_updated

def getDocument(collection_id, query, values_to_get):

    collection_ref = db.collection(collection_id)

    query_ref = collection_ref.where(query[0],query[1],query[2])
    docs = query_ref.stream()

    docs_list = list(docs)
    if docs_list:
        doc = docs_list[0]
        query_result = {"id":doc.id}
        for value in values_to_get:
            print(value, doc.to_dict().get(value))
            query_result.update({value: doc.to_dict().get(value)})
        return query_result
    else:
        return None

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

class updateUserLocation(Resource):
    def post(self):
        if not apiKeyCheck(request):
            return {"Error":"Unauthorised access"},401
        
        data = json.loads(request.json)

        if not data:
            return {"Error":"No input data sent"},400
        if 'uid' not in data:
            return {"Error":"uid field not sent"},400
        if 'mac_address' not in data:
            return {"Error":"mac_address field not sent"},400    
        
        mac_address = data['mac_address']
        uid = data['uid']

        location = getDocument("rfid_reader_location",("reader_mac_address","==",mac_address),("location",))['location']
        if not location:
            return {"Error":"Invalid MAC address"},400
        
        user_id = getDocument('rfid_users',('rfid_uid','==',data['uid']),('user_id',))['user_id']
        if not user_id:
            return {"Error":"Invalid UID"},400

        updateDocument('rfid_users',('user_id','==',user_id),{"location":location})
        if not data:
           return {"Error":"User document not updated"}, 400
        else:
            return {"Success":"User document updated","uid":uid,"mac_address":mac_address,"location":location,"user_id":user_id}, 200
        
            
class sendScannedUID(Resource):
    def get(self):
        if not apiKeyCheck(request):
            return {"error": "Unauthorized access"}, 401
        
        data = request.json
        if not data:
            return {"error": "Bad Request, No data in request"}, 400
        if 'uid' not in data:
            return {"error": "Bad Request, Tag uid not in request"}, 400
        if 'mac_address' not in data:
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
api.add_resource(updateUserLocation,"/update_user_location")

app = app