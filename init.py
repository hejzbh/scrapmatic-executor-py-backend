from flask import Flask
from pymongo import MongoClient
from flask_socketio import SocketIO
import os
PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

def createApp():
   return Flask(__name__)

def connectToDatabase():
   client = MongoClient("mongodb+srv://hejzbh:h0E0NeoKDoZjn9id@scrapmatic.s02zw.mongodb.net/Scrapmatic")
   db = client["Scrapmatic"]
   return db


db = connectToDatabase()
app = createApp()
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")