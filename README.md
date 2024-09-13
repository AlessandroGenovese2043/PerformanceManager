# PerformanceManager
### Docker
In order to run the simulator you must at least run the Docker containers “simulator_service”, “pushgateway” and “prometheus”.

### Endpoints
You have to insert the request body in the <i> Body</i> section, select <i>raw</i> and use JSON format.

Base endpoint:  http://localhost:8080

Before querying the simulator you need to create at least one application.

- /create_app POST

      //In this way we fill the request body 
      {
        "app_name": "APP3",
        "api_number": 2,
        "API0": {
          "version": "1.0",
          "component_number": 1,
          "endpoint": "/api0",
          "weights" : [1.5],
          "component": [
            {
              "name": "component1",
              "inputMax": 100,
              "inputLevel": 4,
              "confHW": 5,
              "performance_decrease": 20,
              "performance_increase": 25,
              "base_value": 1,
              "current_confHW" : 2
            }
          ]
        },
        "API1": {
          "version": "1.0",
          "component_number": 2,
          "endpoint": "/api1",
          "weights" : [1.2,2],
          "component": [
            {
              "name": "component1"
            },
            {
              "name": "component2",
              "inputMax": 100,
              "inputLevel": 2,
              "confHW": 2,
              "performance_decrease": 20,
              "performance_increase": 25,
              "base_value": 9
            }
          ]
        }
      }
- /get_value_from_API POST

      {
         "application_name" : "APP3",
         "api_name": "API1",
         "inputLevel" : 1,
         "confHW": 2 // it is possible to omit it in this case the current configuration of the component will be used
          //If you use the key “confHW” all application components will be tried with that confHW
          //If you want to change differently the configuration of the individual component use the "set_ConfHW" endpoint
      }

- /set_confHW

      {
      "component_name":"component1",
      "confHW":1
      }

- /view_apps GET

- /view_component GET

- /add_row POST

      //In this way we fill the request body
      {
      "component_name" : "component1"
      }
- /add_column POST

        //In this way we fill the request body
        {
        "component_name" : "component1"
        }
- /get_value_from_matrix POST

        //In this way we fill the request body
        {
        "component_name" : "component1",
        "inputLevel" : 2,
        "confHW": 1 // it is possible to omit it in this case the current configuration of the component will be used
        }
- /add_component

      {    
      "name": "component4",
      "inputMax": 100,
      "inputLevel": 4,
      "confHW": 5,
      "performance_decrease": 20,
      "performance_increase": 25,
      "base_value": 1,
      "current_confHW" : 2
      }

- /add_api
  
        {
        "application_name": "APP3",
        "api_name": "API3",
        "version": "1.0",
        "component_number": 1,
        "endpoint": "/api3",
        "weights" : [1.5,2],
        "component": [
        {
        "name": "component1",
        "inputMax": 100,
        "inputLevel": 4,
        "confHW": 5,
        "performance_decrease": 20,
        "performance_increase": 25,
        "base_value": 1,
        "current_confHW" : 2
        }
        ]
        }
