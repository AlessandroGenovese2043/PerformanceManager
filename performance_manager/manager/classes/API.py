class API:
    def __init__(self, name, version, component_number, endpoint, component_weights):
        self.name = name
        self.version = version
        self.component_number = component_number
        self.endpoint = endpoint
        self.component_list = []
        if len(component_weights) < component_number:
            for i in range(component_weights, component_number):
                component_weights.append(1)  # if the component weight is not specified it will be set at 1
        elif len(component_weights) == component_number:
            self.component_weights = component_weights
        else:
            self.component_weights = component_weights[:component_number]


    def getName(self):
        return self.name
    def getVersion(self):
        return self.version
    def getComponentNumber(self):
        return self.component_number
    def getPrincipalComponent(self):
        combined = zip(self.component_list, self.component_weights)

        max_pair = max(combined, key=lambda x: x[1])
        return max_pair[0]  # return the component with the highest weights

    def getComponentWeights(self):
        return self.component_weights
    def getComponentList(self):
        return self.component_list
    def getEndpoint(self):
        return self.endpoint

    def init_add_component(self, component):
        self.component_list.append(component)

    def add_component(self, component):
        self.component_number += 1
        self.component_list.append(component)

    def info(self):
        component_list_info = []
        for component in self.component_list:
            component_list_info.append(component.info())
        return (f"API: {self.name}, Version: {self.version}, Number of components: {self.component_number}, \n "
                f"Components: {component_list_info}, Component_weights: {self.component_weights}")
