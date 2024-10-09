import json

from flask import Flask, request, Response

from classes.API import API
from classes.application import Application
from classes.component import Component
from utils.logger import logger
from prometheus_client import Counter, generate_latest, REGISTRY, Gauge, CollectorRegistry, push_to_gateway

registry = CollectorRegistry()
API_RESPONSE_TIME = Gauge('API_Response_time', 'API Response time obtained from simulator', ['API'], registry=registry)
COMPONENT_RESPONSE_TIME = Gauge('Component_Response_time', 'Component Response time obtained from simulator',
                                ['name', 'confHW'], registry=registry)

my_apps = []
app_list_name = []
application_dict = dict()
component_dict = dict()


def create_app():
    app = Flask(__name__)

    @app.route('/metrics')
    def metrics():
        # Export all the metrics as text for Prometheus
        return Response(generate_latest(REGISTRY), mimetype='text/plain')

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
                        component_weights = data_dict.get(f"API{i}")["weights"]
                        api = API(f"API{i}", api_version, component_number, endpoint, component_weights)
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
                            logger.info("COMPONENT " + str(component))
                            if "current_confHW" in component:
                                current_confHW = component["current_confHW"]
                            else:
                                current_confHW = 0
                            component = Component(component_name, inputMax, inputLevel, confHW, performance_decrease,
                                                  performance_increase, base_value, current_confHW)
                            component_dict[component_name] = component
                            api.init_add_component(component)
                    app_list_name.append(name)
                    my_apps.append(my_app)
                    application_dict[name] = my_app
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
                                    f"Value: {round(simulate_value, 9)} ms")
                    else:
                        value = component.get_value_from_matrix(inputLevel)
                        if value is None:
                            # raise Exception("InputLevel is not valid")
                            num = component.getBaseValue() * ((1 + component.performance_decrease) ** inputLevel)
                            den = (1 + component.getPerformanceIncrease()) ** component.getCurrentConfHW()
                            simulate_value = num / den
                            return (f"These inputLevel and confHW does not exist in the matrix of the component."
                                    f"\nHowever, it is possible to simulate the value\n"
                                    f"Value: {round(simulate_value, 9)} ms")
                    return f"Value {round(value, 9)} ms, in component {component_name}", 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/get_value_from_API', methods=['POST'])
    def get_value_from_api():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    application_name = data_dict.get("application_name")
                    api_name = data_dict.get("api_name")
                    if application_name not in application_dict:
                        raise Exception("This application does not exist")
                    application = application_dict[application_name]
                    list = application.getApiList()
                    for api in list:
                        if api.getName() == api_name:
                            break
                    else:
                        raise Exception("This api does not exist in that application")
                    component_list = api.getComponentList()
                    inputLevel = data_dict.get("inputLevel")
                    i = 0
                    sum = 0
                    if data_dict.get("confHW") is not None:
                        confHW = data_dict.get("confHW")
                        i = 0
                        for component in component_list:
                            value = component.get_value_from_matrix(inputLevel, confHW[i])
                            if value is None:
                                # raise Exception("InputLevel and/or confHW are not valid")
                                num = component.getBaseValue() * ((1 + component.performance_decrease) ** inputLevel)
                                den = (1 + component.getPerformanceIncrease()) ** confHW[i]
                                value = num / den
                                '''
                                return (f"These inputLevel and confHW does not exist in the matrix of the component."
                                        f"\nHowever, it is possible to simulate the value\n"
                                        f"Value: {round(simulate_value,9)}")
                                '''
                            logger.info(f"Component:{component.getName()}, value:{value}")
                            COMPONENT_RESPONSE_TIME.labels(name=component.getName(), confHW=confHW[i]).set(value)
                            push_to_gateway('pushgateway:9091', job='simulator', registry=registry)
                            weighted_value = value * api.getComponentWeights()[i]
                            sum += weighted_value
                            logger.info(f"Component:{component.getName()}, weighted_value:{weighted_value}, i: {i}")
                            i += 1
                    else:
                        for component in component_list:
                            confHW = component.getCurrentConfHW()
                            value = component.get_value_from_matrix(inputLevel)
                            if value is None:
                                num = component.getBaseValue() * ((1 + component.performance_decrease) ** inputLevel)
                                den = (1 + component.getPerformanceIncrease()) ** component.getCurrentConfHW()
                                value = num / den
                            logger.info(f"Component:{component.getName()}, value:{value}")
                            COMPONENT_RESPONSE_TIME.labels(name=component.getName(),confHW=confHW).set(value)
                            push_to_gateway('pushgateway:9091', job='simulator', registry=registry)
                            weighted_value = value * api.getComponentWeights()[i]
                            sum += weighted_value
                            logger.info(f"Component:{component.getName()}, weighted_value:{weighted_value}, i: {i}")
                            i += 1
                    logger.info(f"Value:{sum}")
                    API_RESPONSE_TIME.labels(API=api_name).set(sum)
                    push_to_gateway('pushgateway:9091', job='simulator', registry=registry)
                    # return (f"Value {round(sum, 9)} ms, in API: {api_name} application: {application_name}, "
                    #        f"component_weights: {api.getComponentWeights()}"), 200
                    list_weights = api.getComponentWeights()
                    principal_component = api.getPrincipalComponent()
                    var = component_dict[principal_component]
                    confHW = var.getCurrentConfHW()
                    response_data = {
                        "RT": round(sum, 9),
                        "api_name": api_name,
                        "application_name": application_name,
                        "component_weights": list_weights,
                        "principal_component": principal_component,
                        "confHW": confHW
                    }
                    return json.dumps(response_data), 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/set_confHW', methods=['POST'])
    def set_confHW():
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
                    if data_dict.get("confHW") is not None:
                        confHW = data_dict.get("confHW")
                        component.setConfHW(confHW)
                        return (f"Setted the new HW configuration: {confHW}")
                    else:
                        # show the current confHW
                        return f"Current HW configuration: {component.getCurrentConfHW()}"
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/add_component', methods=['POST'])
    def add_component():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    component_name = data_dict.get("name")
                    if component_name in component_dict:
                        raise Exception("This component already exist")
                    inputMax = data_dict.get("inputMax")
                    inputLevel = data_dict.get("inputLevel")
                    confHW = data_dict.get("confHW")
                    performance_decrease = data_dict.get("performance_decrease")
                    performance_increase = data_dict.get("performance_increase")
                    base_value = data_dict.get("base_value")
                    if data_dict.get("current_confHW"):
                        current_confHW = data_dict.get("current_confHW")
                    else:
                        current_confHW = 0
                    component = Component(component_name, inputMax, inputLevel, confHW, performance_decrease,
                                          performance_increase, base_value, current_confHW)
                    component_dict[component_name] = component
                    return (f"New component added: {component_name}"), 200
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/view_components', methods=['GET'])
    def view_components():
        info_list = []
        for component in component_dict.values():
            info_list.append(component.info())
        return info_list, 200

    @app.route('/view_component', methods=['POST'])
    def view_component():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    component_name = data_dict.get("component_name")
                    if component_name in component_dict.keys():
                        component = component_dict[component_name]
                        return component.json_info(), 200
                    else:
                        return f"Error: there is no component with name: {component_name}", 400
            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    @app.route('/add_api', methods=['POST'])
    def add_api():
        if request.is_json:
            try:
                # Extract json data
                data_dict = request.get_json()
                logger.info("Data received:" + str(data_dict))
                if data_dict:
                    application_name = data_dict.get("application_name")
                    if application_name not in application_dict:
                        raise Exception("This application_name does not exist")
                    api_name = data_dict.get("api_name")
                    application = application_dict[application_name]
                    list = application.getApiList()
                    for api in list:
                        if api.getName() == api_name:
                            raise Exception("This api already exist in that application")
                    api_version = data_dict.get("version")
                    component_number = data_dict.get("component_number")
                    endpoint = data_dict.get("endpoint")
                    component_weights = data_dict.get("weights")
                    api = API(api_name, api_version, component_number, endpoint, component_weights)
                    application.init_add_api(api)
                    for component in data_dict.get("component"):
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
                        logger.info("COMPONENT " + str(component))
                        if "current_confHW" in component:
                            current_confHW = component["current_confHW"]
                        else:
                            current_confHW = 0
                        component = Component(component_name, inputMax, inputLevel, confHW, performance_decrease,
                                              performance_increase, base_value, current_confHW)
                        component_dict[component_name] = component
                        api.init_add_component(component)
                    return f"Added new API:{api_name}"

            except Exception as e:
                return f"Error in reading data: {str(e)}", 400
        else:
            return "Error: the request must be in JSON format", 400

    return app


# create Flask application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
