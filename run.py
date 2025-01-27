from init import  app, socketio
from routes.workflow import init_routes  
from flask_cors import CORS

# Cors
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Endpoints / Routes
init_routes(app)

# Socket
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    app.run()