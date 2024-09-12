import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
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

class HelloWorld(Resource):
    def get(self):
        collection_ref = db.collection('rfid_users')
        
        # Pull all documents from the collection
        # docs = collection_ref.stream()
        query_ref = collection_ref.where("rfid", "==", "AAAAAAAA")
        docs = query_ref.stream()

        docs_list = list(docs)
        if docs_list:
            doc = docs_list[0]  # Fetch the first document from the query result
            return {
                "id": doc.id,
                "user_name": doc.to_dict().get('user_name')
            }
        else:
            return {"error": "No matching document found"}, 404
        # Convert generator to list and fetch first document if exists
        
        #docs_list = list(docs)
        #if docs_list:
        #    first_doc = docs_list[0].to_dict()
        #    return {"data": first_doc}
        #else:
        #    return {"data": "No documents found"}, 404
    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(HelloWorld, "/helloworld")

app = app