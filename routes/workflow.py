from flask import jsonify, request
from bson import ObjectId
from init import db
import json
from models.FlowExecutor import FlowExecutor
from services.updateDatabaseModel import updateDatabaseModel

"""
ČEKIRATI DA LI KORISNIK PRIJE SVEGA MOZE UOPSTE POKRENUTI CITAV WORKFLOW, AKO NEMA DOVOLJNO KREDITA VRAITIT ODMAH ERRRO
"""

def init_routes(app):
    @app.route("/run-workflow", methods=["POST"])
    async def run_workflow():
        try:
            data = request.json
            
            # Ensure data is provided
            if not data:
                return jsonify({"error": "Data is missing"}), 400

            # Extract executionId and validate
            execution_id = data.get("executionId")
            user_id = data.get("userId")
            if not execution_id or not user_id:
                return jsonify({"error": "'executionId' is missing"}), 400


            # Fetch execution from the database
            execution = db.get_collection('WorkflowExecution').find_one({"_id": ObjectId(execution_id)})

            # Handle case where execution is not found
            if execution is None:
                return jsonify({"error": "Execution not found"}), 404

            # Convert ObjectId to string for JSON compatibility
            execution['_id'] = str(execution['_id'])     

            # Check can user run nworkflow due to credits
            if not await canUserRunWorkflow(user_id, execution):
                return jsonify({"error": "Insufficient credits to run this workflow"}), 400
        
            
            # Fetch workflow 
            workflow = db.get_collection("Workflow").find_one({"_id": execution["workflowId"]})

            if workflow is None:
                return jsonify({"error":"Workflow is not found"})

            # Fetch associated steps if execution is found
            steps = list(db.get_collection('ExecutionStep').find({"workflowExecutionId": ObjectId(execution_id)}))


            # Extract nodes from workflow
            workflow["editorObjectJSON"] = json.loads(workflow["editorObjectJSON"])
            nodes = list(workflow["editorObjectJSON"]["nodes"])
            edges = list(workflow["editorObjectJSON"]["edges"])
            

    

                        
            # Executor that handles the most important step in entire process, it executes tasks
            flowExecutor = FlowExecutor(execution, nodes,  edges, steps)
            await flowExecutor.execute()
            await chargeUserBalance(userId=user_id, amount=execution["creditsCost"])
    
        
       
       
            return jsonify({
                "message": "Successfully executed workflow", 
            }), 200
        except Exception as e:
            # Return error response if something goes wrong during serialization
            return jsonify({
                "error":  str(e), 
            }), 500


async def chargeUserBalance(userId, amount):
    balance = db.get_collection("UserBalance").find_one({"userId": userId})
    chargedCredits = balance["availableCredits"] - amount
   
    await updateDatabaseModel("UserBalance", balance["_id"], {"availableCredits": chargedCredits})


async def canUserRunWorkflow(user_id, execution):

    try:
        balance = db.get_collection("UserBalance").find_one({"userId": user_id})

        if balance is None:
           return False

        return balance["availableCredits"]>execution["creditsCost"]
    except:
        return False

