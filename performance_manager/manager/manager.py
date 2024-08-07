from flask import Flask, request, jsonify

from classes.API import API
from classes.application import Application
from classes.component import Component
from utils.logger import logger

my_apps = []
app_list_name = []
component_dict = dict()
def create_app():
    app = Flask(__name__)
    @app.route('/create_app', methods=['POST'])
    def create():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    api_number = data_dict.get("api_number")
                    name = data_dict.get("app_name")
                    if name in app_list_name:
                        raise Exception("App_name already present")
                    my_app = Application(name, api_number)
                    for i in range(api_number):
                        logger.info(f"API{i}")
                        logger.info(data_dict.get(f"API{i}")["version"])
                        api_version = data_dict.get(f"API{i}")["version"]
                        component_number = data_dict.get(f"API{i}")["component_number"]
                        endpoint = data_dict.get(f"API{i}")["endpoint"]
                        api = API(f"API{i}", api_version, component_number, endpoint)
                        my_app.init_add_api(api)
                        for component in data_dict.get(f"API{i}")["component"]:
                            logger.info(component_dict)
                            component_name = component["name"]
                            if component_name in component_dict:
                                api.init_add_component(component_dict[component_name])
                                continue
                            inputMax = component["inputMax"]
                            inputLevel = component["inputLevel"]
                            confHW = component["confHW"]
                            performance_decrease = component["performance_decrease"]
                            performance_increase = component["performance_increase"]
                            base_value = component["base_value"]
                            logger.info("COMPONENT "+str(component))
                            if "current_confHW" in component:
                                current_confHW = component["current_confHW"]
                            else:
                                current_confHW = 0
                            component = Component(component_name, inputMax, inputLevel, confHW, performance_decrease, performance_increase, base_value, current_confHW)
                            component_dict[component_name] = component
                            api.init_add_component(component)
                    app_list_name.append(name)
                    my_apps.append(my_app)
                    return f"App Created with {api_number} API ", 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/view_apps', methods=['GET'])
    def view():
        info_list = []
        for app in my_apps:
            info_list.append(app.get_info())
        return info_list, 200

    @app.route('/add_row', methods=['POST'])
    def add_row():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    component_name = data_dict.get("component_name")
                    if component_name not in component_dict:
                        raise Exception("This component does not exist")
                    component = component_dict[component_name]
                    new_row = component.add_row()
                    return f"New row added {new_row}, in component {component_name}", 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/add_column', methods=['POST'])
    def add_column():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    component_name = data_dict.get("component_name")
                    if component_name not in component_dict:
                        raise Exception("This component does not exist")
                    component = component_dict[component_name]
                    new_column = component.add_column()
                    return f"New column added {new_column}, in component {component_name}", 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/get_value_from_matrix', methods=['POST'])
    def get_value_from_matrix():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    component_name = data_dict.get("component_name")
                    if component_name not in component_dict:
                        raise Exception("This component does not exist")
                    component = component_dict[component_name]
                    inputLevel = data_dict.get("inputLevel")
                    if data_dict.get("confHW") is not None:
                        confHW = data_dict.get("confHW")
                        value = component.get_value_from_matrix(inputLevel, confHW)
                        if value is None:
                            # raise Exception("InputLevel and/or confHW are not valid")
                            num = component.getBaseValue() * ((1 + component.performance_decrease) ** inputLevel)
                            den = (1 + component.getPerformanceIncrease()) ** confHW
                            simulate_value = num / den
                            return (f"These inputLevel and confHW does not exist in the matrix of the component."
                                    f"\nHowever, it is possible to simulate the value\n"
                                    f"Value: {round(simulate_value,9)}")
                    else:
                        value = component.get_value_from_matrix(inputLevel)
                        if value is None:
                            # raise Exception("InputLevel is not valid")
                            num = component.getBaseValue() * ((1 + component.performance_decrease) ** inputLevel)
                            den = (1 + component.getPerformanceIncrease()) ** component.getCurrentConfHW()
                            simulate_value = num / den
                            return (f"These inputLevel and confHW does not exist in the matrix of the component."
                                    f"\nHowever, it is possible to simulate the value\n"
                                    f"Value: {round(simulate_value,9)}")
                    return f"Value {value}, in component {component_name}", 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    return app
# create Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

