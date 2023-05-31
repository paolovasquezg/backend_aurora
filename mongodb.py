from pymongo import MongoClient

uri = 'mongodb://localhost'

client = MongoClient(uri)
db = client['aurora']
sesion = db['sesions']
message = db['message']