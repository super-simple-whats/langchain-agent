from flask import Flask, request, jsonify
from typing import Callable, Dict, Any
import os

class WebhookResponse:
    data: Any
    code: int
    
    def __init__(self, data: Any, code: int):
        self.data = data
        self.code = code

class WebhookServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.callback = None
        
        # Register the route in the instance method
        @self.app.route(os.environ.get("HOOKS_PATH"), methods=['POST'])
        def webhook_handler():
            # Get the JSON data from the webhook
            data = request.json
            
            if self.callback:
                response = self.callback(data)
            
            # Return a successful response
            return jsonify(response.data), response.code

    def run(self, callback: Callable[[Dict[str, Any]], WebhookResponse]):
        self.callback = callback
        # Run the Flask server
        self.app.run(host='0.0.0.0', port=int(os.environ.get("HOOKS_PORT")), debug=True)
        