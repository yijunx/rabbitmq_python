import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="rabbitmq", credentials=pika.PlainCredentials("guest", "guest")
    )
)
channel = connection.channel()


channel.queue_declare(queue="task_queue", durable=True)

message = " ".join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange="",
    routing_key="task_queue",  # routing key has to be queue name
    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
    body=message,
)
print(f" [x] Sent {message}")

connection.close()
