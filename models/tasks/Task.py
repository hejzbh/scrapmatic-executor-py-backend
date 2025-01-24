from init import socketio
import json
import copy
from utils.generateDownloadUrl import generateDownloadURL
from services.updateDatabaseModel import updateDatabaseModel

class Task:
    def __init__(self, taskType, inputs, stepId):
        # Initialize a task with type, inputs, step ID, and default outputs and status.
        self.taskType = taskType
        self.inputs = inputs
        self.stepId = stepId
        self.outputs = {}
        self.setStatus("PENDING")

    async def setStatus(self, status):
        # Update the status of the task and notify through socket events.
        self.status = status
        socketio.emit("STEP_UPDATE", {"id": self.stepId, "status": status})
        await updateDatabaseModel("ExecutionStep", self.stepId, {"status": status})

    async def setOutputs(self, outputs):
        # Update the outputs of the task and process any specific modifications.
        for key in outputs:
            self.outputs[key] = outputs[key]

        # Create a deep copy of outputs to avoid mutating the original dictionary.
        outputResults = copy.deepcopy(self.outputs)
        
        # Replace certain keys with modified or user-friendly values.
        if "webPage" in outputResults:
            outputResults["webPage"] = "Web Page"
        
        if "html" in outputResults:
            # Generate a downloadable URL for HTML outputs.
            outputResults["html"] = generateDownloadURL(outputResults["html"])
        
        # Convert the outputs to JSON format for consistent communication.
        outputResults = json.dumps(outputResults)

        # Emit the updated outputs through socket events and update the database.
        socketio.emit("STEP_UPDATE", {"id": self.stepId, "outputResults": outputResults})
        await updateDatabaseModel("ExecutionStep", self.stepId, {"outputResults": outputResults})
