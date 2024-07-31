from flask import Flask, request, jsonify
from utils.logger import logger


def create_app():
    app = Flask(__name__)

    @app.route('/create_app', methods=['POST'])
    def create_app():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    api_number = data_dict.get("api_number")
                    #TODO...
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400
