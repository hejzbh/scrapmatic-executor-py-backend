from init import socketio
from models.tasks.LaunchBrowser import LaunchBrowserTask
from models.tasks.PageToHTML import PageToHtmlTask
from datetime import datetime, date
from models.tasks.ExtractTextFromElement import ExtractTextFromElementTask 
from services.updateDatabaseModel import updateDatabaseModel

class FlowExecutor:
    def __init__(self, execution, nodes, edges, steps):
        # Initialize the flow executor with provided execution, nodes, edges, and steps
        self.status = execution["status"]
        self.creditsCost = execution["creditsCost"]
        self.executionId = execution["_id"]
        self.nodes = nodes
        self.steps = steps
        self.edges = edges

    # Set the current status and update it in the database and emit it via socket
    async def setStatus(self, status):
        self.status = status
        socketio.emit('executionStatus', self.status)
        await updateDatabaseModel("WorkflowExecution", self.executionId, {"status": status})

    # Emit start time and update it in the database
    async def onStart(self):
        currentDate = datetime.now().isoformat()
        socketio.emit("STARTED_AT", currentDate)
        await updateDatabaseModel("WorkflowExecution", self.executionId, {"startedAt": currentDate})

    # Emit end time and update it in the database
    async def onEnd(self):
        currentDate = datetime.now().isoformat()
        socketio.emit("COMPLETED_AT", currentDate)
        await updateDatabaseModel("WorkflowExecution", self.executionId, {"completedAt": currentDate})

    # Get a node by its ID
    def getNode(self, nodeId):
        return next(node for node in self.nodes if node['id'] == nodeId)

    # Get all connected nodes to a specific node (source node)
    def getConnectedNodes(self, sourceNodeId):
        connectedNodes = []
        for edge in self.edges:
            if edge["source"] == sourceNodeId:
                connectedNodes.append(edge["target"])
        return connectedNodes

    # Provide outputs from one node to the inputs of the connected nodes
    def provideOutputsToNodeInputs(self, outputs, sourceNodeId):
        for key in outputs:
            # Find all connected nodes that need the output from the source node
            connectedNodes = self.getConnectedNodes(sourceNodeId)
            for connectedNodeId in connectedNodes:
                targetNode = self.getNode(connectedNodeId)
                targetNode["data"]["inputs"][key] = outputs[key]

    # Execute the entire flow
    async def execute(self):
        try:
            # 1) Set status to running
            await self.setStatus("RUNNING")
            await self.onStart()

            # Iterate over each step in the workflow
            for step in self.steps:
                # For each node in the step, get the node object
                node = self.getNode(step["nodeId"])
                if node is None:
                    continue

                inputs = node["data"]["inputs"]
                taskType = node["data"]["taskType"]
                task = None

                # Match the task type and create the corresponding task
                match taskType:
                    case "LAUNCH_BROWSER":
                        task = LaunchBrowserTask(taskType, inputs, str(step["_id"]))
                    case "PAGE_TO_HTML":
                        task = PageToHtmlTask(taskType, inputs, str(step["_id"]))
                    case "EXTRACT_TEXT_FROM_ELEMENT":
                        task = ExtractTextFromElementTask(taskType, inputs, str(step["_id"]))

                # Execute the task and get the outputs
                outputs = await task.execute()

                # Provide the outputs to the connected nodes
                self.provideOutputsToNodeInputs(outputs, step["nodeId"])

            # 2) Set status to completed
            await self.setStatus("COMPLETED")

        except Exception as e:
            # If any error occurs, set status to failed
            await self.setStatus("FAILED")
            raise ValueError(e)
        
        finally:
            # Emit completion time and update the database
            await self.onEnd()
