import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from utils.logger import logger
import confluent_kafka
from confluent_kafka.admin import AdminClient, NewTopic
import time


def reset_conf(component_name):
    reset_data = {
        "component_name": component_name,
        "confHW": 0
    }
    try:
        reset_response = requests.post("http://simulator-service:8080/set_confHW", json=reset_data)
        if reset_response.status_code == 200:
            return True
        else:
            logger.info(f"Error in the request: {reset_response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"Connection error: {e}")
    return False

def produce_kafka_message(topic_name, kafka_producer, message_to_sent):
    # Publish on the specific topic
    try:
        kafka_producer.produce(topic_name, value=message_to_sent)
    except BufferError:
        logger.error(
            '%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(kafka_producer))
        return False
    return True


def create_load_curve(n_samples, frequency, amplitude):
    # Create x-axis from 0 to n_samples
    x = np.arange(0, n_samples)
    # Straight line going from a 0 to 1000 with n_samples samples
    linear_component = np.linspace(0, 1000, n_samples)

    sinusoidal_component = amplitude * np.sin(2 * np.pi * frequency * x / n_samples)

    # Combination of the two components
    y = linear_component + sinusoidal_component
    return x, y


if __name__ == '__main__':
    # Kafka admin and producer initialization in order to publish in topic "metric_update"
    broker = 'kafka-service:9092'
    topic = 'metric_update'
    producer_conf = {'bootstrap.servers': broker, 'acks': 0}
    admin_conf = {'bootstrap.servers': broker}
    kadmin = AdminClient(admin_conf)

    # Create topic "metric_update" if not exists
    list_topics_metadata = kadmin.list_topics()
    topics = list_topics_metadata.topics  # Returns a dict()
    logger.info(f"LIST_TOPICS: {list_topics_metadata}")
    logger.info(f"TOPICS: {topics}")
    topic_names = set(topics.keys())
    logger.info(f"TOPIC_NAMES: {topic_names}")
    found = False
    for name in topic_names:
        if name == topic:
            found = True
    if found is False:
        new_topic = NewTopic(topic, 2, 1)  # Number-of-partitions = 1, Number-of-replicas = 1
        kadmin.create_topics([new_topic, ])

    # Create Producer instance
    producer_kafka = confluent_kafka.Producer(**producer_conf)

    x_values, y_values = create_load_curve(1500, 15, 30)
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)
    plt.title("Load curve with increasing trend and oscillations")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.savefig('./plotLoadCurve.png')

    step_function = np.floor(y_values / 100)

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label='Original curve')
    plt.step(x_values, step_function, label='Step function', color='red')

    plt.title("Original curve and step function")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.savefig('./plotOriginalAndStep.png')

    plt.plot(x_values, step_function, label="Step Function")
    plt.title("Step function")
    plt.xlabel("Sample")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.savefig('./plotStep.png')

    url = "http://simulator-service:8080/get_value_from_API"
    results_df = pd.DataFrame(columns=["inputLevel", "response"])
    application_name = "APP3"
    api_name = "API0"
    data_list = []
    SLO = 20
    time.sleep(5)

    for i in range(len(step_function)):
        # Prepares JSON data to be sent to the server
        data = {
            "application_name": application_name,
            "api_name": api_name,
            "inputLevel": int(step_function[i])
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                '''
                result = response.text
                match = re.search(r"Value ([\d.]+) ms", result)
                if match:
                    time_ms = match.group(1)
                    data_list.append({
                        "inputLevel": data["inputLevel"],
                        "response": float(time_ms)
                    })
                '''
                result = response.json()
                message = dict()
                message["application_name"] = data["application_name"]
                message["api_name"] = data["api_name"]
                message["inputLevel"] = data["inputLevel"]
                message["RT"] = float(result["RT"])
                component_name = result["principal_component"]
                message["principal_component"] = result["principal_component"]
                message["confHW"] = result["confHW"]
                json_message = json.dumps(message)
                logger.info(f"JSON_MESSAGE:{json_message}")
                produce_kafka_message(topic, producer_kafka, json_message)
                logger.info("Produced message to Kafka")
                data_list.append({
                    "inputLevel": data["inputLevel"],
                    "response": float(result["RT"]),
                    "confHW": result["confHW"]

                })
                #  else:
                #   print(f"Pattern not found: {result}")
                time.sleep(0.015)
            else:
                logger.info(f"Error in the request for inputLevel {data['inputLevel']}: {response.status_code} + {response}")

        except requests.exceptions.RequestException as e:
            logger.info(f"Connection error: {e}")


    results_df = pd.DataFrame(data_list)
    print(results_df)
    results_df.to_csv('output.csv')

    plt.figure(figsize=(10, 6))
    plt.plot(results_df['inputLevel'], results_df['response'])
    plt.xlabel('Input Level')
    plt.ylabel('Response')
    plt.title('Graph between Input Level and Response with control')
    plt.grid(True)
    plt.savefig('./plot1.png')

    start_time = pd.Timestamp('2023-09-17 00:00:00')
    timestamps = pd.date_range(start=start_time, periods=len(results_df), freq='min')
    results_df['SLO'] = SLO
    results_df['timestamp'] = timestamps
    # results_df = results_df.set_index('timestamp')
    print(results_df)
    results_df.to_csv('output_with_timestamp_and_SLO.csv', index=False)

    plt.plot(results_df['timestamp'], results_df['response'], label='confHW0')
    plt.axhline(y=SLO, color='red', linestyle='--', label='SLO')
    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.ylabel('Response time (ms)')
    plt.title('Graph between timestamps and response time with control')
    plt.grid(True)
    plt.legend()
    plt.savefig('./plot2.png')

    reset_conf(component_name)
