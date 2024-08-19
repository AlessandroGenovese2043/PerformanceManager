class Application:
    def __init__(self, name, api_number):
        self.name = name
        self.api_number = api_number
        self.api_list = []

    def getName(self):
        return self.name

    def getApiNumber(self):
        return self.api_number

    def getApiList(self):
        return self.api_list

    def init_add_api(self, api):
        self.api_list.append(api)

    def add_api(self, api):
        self.api_number += 1
        self.api_list.append(api)

    def get_info(self):
        api_list_info = []
        for api in self.api_list:
            api_list_info.append(api.info())
        return {
            "name": self.name,
            "number of API": self.api_number,
            "api_list": api_list_info
        }
