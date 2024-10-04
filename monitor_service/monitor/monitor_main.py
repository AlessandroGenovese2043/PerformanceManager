import confluent_kafka
from utils.logger import logger
from confluent_kafka.admin import AdminClient, NewTopic

if __name__ == "__main__":


    # Kafka admin and producer initialization in order to publish in topic "metrics_to_analyze"
    broker = 'kafka-service:9092'
    topic = 'metrics_to_analyze'
    producer_conf = {'bootstrap.servers': broker, 'acks': 1}
    admin_conf = {'bootstrap.servers': broker}
    kadmin = AdminClient(admin_conf)

    # Create topic "metrics_to_analyze" if not exists
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
    if found == False:
        new_topic = NewTopic(topic, 2, 1)  # Number-of-partitions = 2, Number-of-replicas = 1
        kadmin.create_topics([new_topic,])

    # Create Producer instance
    producer_kafka = confluent_kafka.Producer(**producer_conf)

    # start Kafka subscription
    consumer_kafka = confluent_kafka.Consumer(
        {'bootstrap.servers': 'kafka-service:9092', 'group.id': 'group2', 'enable.auto.commit': 'false',
         'auto.offset.reset': 'latest', 'on_commit': commit_completed})
    try:
        consumer_kafka.subscribe(['event_update'])  # the worker_service is also a Consumer related to the WMS Producer
    except confluent_kafka.KafkaException as ke:
        logger.error("Kafka exception raised! -> " + str(ke) + "\n")
        consumer_kafka.close()
        sys.exit("Terminate after Exception raised in Kafka topic subscribe\n")