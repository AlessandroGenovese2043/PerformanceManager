from locust import HttpUser, task, between
import random



def read_file(file_name):
    with open(file_name, "r") as f:
        return [tuple(map(int, line.strip().split())) for line in f]


input_and_conf = read_file("input_conf.txt")


class User(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def post_to_simulator(self):
        input_level, conf_hw = random.choice(input_and_conf)
        payload = {
            "application_name": "APP3",
            "api_name": "API0",
            "inputLevel": input_level,
            "confHW": conf_hw
        }
        self.client.post("/get_value_from_API", json=payload)
