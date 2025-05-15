import pika
import json
import os
import boto3
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuración RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# Configuración InfluxDB
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "admintoken")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "adorg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "adbucket")

# Configuración MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = "ad-events"

# Conexión InfluxDB
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Conexión MinIO
minio_client = boto3.client(
    's3',
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

# Crear bucket si no existe
try:
    minio_client.head_bucket(Bucket=MINIO_BUCKET)
except:
    minio_client.create_bucket(Bucket=MINIO_BUCKET)

def process_message(ch, method, properties, body):
    try:
        event = json.loads(body)
        queue = method.routing_key

        # Guardar evento crudo en MinIO
        minio_client.put_object(
            Bucket=MINIO_BUCKET,
            Key=f"{queue}/{event['timestamp']}.json",
            Body=json.dumps(event).encode('utf-8')
        )

        if queue == "impressions_queue":
            event_type = "impression"
            tags = {
                "state": event.get("state"),
                "ad_ids": ",".join([ad["ad"]["ad_id"] for ad in event.get("ads", [])]),
                "keywords": event.get("search_keywords")
            }
        elif queue == "clicks_queue":
            event_type = "click"
            tags = {
                "state": event["user_info"]["state"],
                "ad_id": event["clicked_ad"]["ad_id"]
            }
        elif queue == "conversions_queue":
            event_type = "conversion"
            tags = {
                "state": event["user_info"]["state"],
                "conversion_type": event.get("conversion_type")
            }
        else:
            print("Unknown queue")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        point = Point("ad_events") \
            .tag("event_type", event_type)

        for k, v in tags.items():
            if v:
                point = point.tag(k, v)

        point = point.field("count", 1) \
                     .time(event["timestamp"], WritePrecision.NS)

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        print(f"Processed {event_type} event")

    except Exception as e:
        print(f"Error processing message: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Conexión RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Declarar colas
queues = ["impressions_queue", "clicks_queue", "conversions_queue"]
for queue in queues:
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_consume(queue=queue, on_message_callback=process_message)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
