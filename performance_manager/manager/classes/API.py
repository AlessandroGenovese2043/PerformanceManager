class API:
    def __init__(self, name, version, component_number):
        self.name = name
        self.version = version
        self.component_number = component_number
        self.component_list = []


    def add_component(self, component):
        self.component_number += 1
        self.component_list.append(component)

    def info(self):
        component_list_info = []
        for component in self.component_list:
            component_list_info.append(component.info())
        return f"API: {self.name}, Version: {self.version}, Number of components: {self.component_number}, Components: {component_list_info}"
