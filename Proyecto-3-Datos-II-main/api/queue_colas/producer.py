import pika
import json
import os

# Configuración: host de RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def send_message(queue_name, message):
    # Conectar a RabbitMQ cada vez que se envía un mensaje
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    # Declarar la cola (por seguridad)
    channel.queue_declare(queue=queue_name, durable=True)

    # Publicar el mensaje
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistencia del mensaje
        )
    )

    # Cerrar la conexión después de enviar
    connection.close()

    print(f"Mensaje enviado a {queue_name}")
