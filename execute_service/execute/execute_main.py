import json
import re
import sys
import requests
import confluent_kafka
from utils.logger import logger
from confluent_kafka.admin import AdminClient, NewTopic


def set_new_confhw(component, confHW):
    url = "http://simulator-service:8080/set_confHW"
    data = {
        "component_name": component,
        "confHW": confHW
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logger.info(f"HW configuration changed: {confHW}")
            return True
        else:
            logger.info(f"Error in the request: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"Connection error: {e}")
    return False


def commit_completed(er, partitions):
    if er:
        logger.error(str(er))
    else:
        logger.info("Commit done!\n")
        logger.info("Committed partition offsets: " + str(partitions) + "\n")


def transform_data(data):
    pass


def delivery_callback(err, msg):
    if err:
        logger.error('%% Message failed delivery: %s\n' % err)
        raise SystemExit("Exiting after error in delivery message to Kafka broker\n")
    else:
        logger.info('%% Message delivered to %s, partition[%d] @ %d\n' %
                    (msg.topic(), msg.partition(), msg.offset()))


def produce_kafka_message(topic_name, kafka_producer, message):
    # Publish on the specific topic
    try:
        kafka_producer.produce(topic_name, value=message, callback=delivery_callback)
    except BufferError:
        logger.error(
            '%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(kafka_producer))
        return False
    # Wait until the message have been delivered
    logger.error("Waiting for message to be delivered\n")
    kafka_producer.flush()
    return True


def report_violation(data):
    logger.info("VIOLATION SLA!")


if __name__ == "__main__":

    SLO = 20
    # start Kafka subscription
    consumer_kafka = confluent_kafka.Consumer(
        {'bootstrap.servers': 'kafka-service:9092', 'group.id': 'group4', 'enable.auto.commit': 'false',
         'auto.offset.reset': 'latest', 'on_commit': commit_completed})
    try:
        consumer_kafka.subscribe(['execute'])
        # the analysis_service is also a Consumer related to the monitor_service Producer
    except confluent_kafka.KafkaException as ke:
        logger.error("Kafka exception raised! -> " + str(ke) + "\n")
        consumer_kafka.close()
        sys.exit("Terminate after Exception raised in Kafka topic subscribe\n")

    try:
        while True:
            # polling messages in Kafka topic
            msg = consumer_kafka.poll(timeout=5.0)
            if msg is None:
                # No message available within timeout.
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                logger.info("Waiting for message or event/error in poll()\n")
                continue
            elif msg.error():
                logger.info('error: {}\n'.format(msg.error()))
                if msg.error().code() == confluent_kafka.KafkaError.UNKNOWN_TOPIC_OR_PART:
                    raise SystemExit
            else:

                # Check for Kafka message
                record_key = msg.key()
                logger.info("RECORD_KEY: " + str(record_key))
                record_value = msg.value()
                logger.info("RECORD_VALUE: " + str(record_value))
                data = json.loads(record_value)
                logger.info("DATA: " + str(data))
                # execute
                newHWConfiguration = data["action_confHW"]
                component_name = data["principal_component"]

                # action of control
                set_new_confhw(component_name, newHWConfiguration)

                # make commit
                try:
                    consumer_kafka.commit(asynchronous=True)
                except Exception as e:
                    logger.error("Error in commit! -> " + str(e) + "\n")
                    raise SystemExit
    except (KeyboardInterrupt, SystemExit):  # to terminate correctly with either CTRL+C or docker stop
        pass
    finally:
        # Leave group and commit final offsets
        consumer_kafka.close()
