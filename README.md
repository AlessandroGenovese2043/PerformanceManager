# PerformanceManager

### Endpoints
You have to insert the request body in the <i> Body</i> section, select <i>raw</i> and use JSON format.

- /create_app POST

      //In this way we fill the request body 
        {
            "app_name": "APP2",
            "api_number": 2,
            "API0": {
                "version": "1.0",
                "component_number": 1,
                "endpoint": "/api0",
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

- view_apps GET

- add_row POST

      //In this way we fill the request body
      {
      "component_name" : "component1"
      }
- add_column POST

        //In this way we fill the request body
        {
        "component_name" : "component1"
        }
- get_value_from_matrix POST

        //In this way we fill the request body
        {
        "component_name" : "component1",
        "inputLevel" : 2,
        "confHW": 1 // it is possible to omit it in this case the current configuration of the component will be used
        }