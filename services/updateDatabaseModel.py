from init import db
from bson import ObjectId

async def updateDatabaseModel(collectionName:str, modelId:str, data):
    db.get_collection(collectionName).update_one({"_id": ObjectId(modelId)}, {"$set":data})