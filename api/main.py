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
        collection_ref = db.collection('trial')

        # Pull all documents from the collection
        docs = collection_ref.stream()

        # Loop through and print each document's data
        #for doc in docs:
        #    print(f'Document ID: {doc.id}')
        #    print(f'Document Data: {doc.to_dict()}')
        return {"data":docs[0].to_dict()}
    
@app.route('/favicon.ico')
def favicon():
    return '', 204 

@app.route("/")
def index():
    return {"message": "Welcome to the API!"}

api.add_resource(HelloWorld, "/helloworld")

app = app