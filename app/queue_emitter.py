import pika
import json
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="rabbitmq", credentials=pika.PlainCredentials("guest", "guest")
    )
)
channel = connection.channel()


user_id = sys.argv[1]
message = " ".join(sys.argv[2:]) or "Hello World!"
channel.queue_declare(queue=user_id)

channel.basic_publish(
    exchange="",
    routing_key=user_id,  # routing key has to be queue name
    body=message,
)

# The exchange parameter is the name of the exchange.
# The empty string denotes the default or nameless exchange:
# messages are routed to the queue with the name specified by routing_key,
# if it exists.
print(" [x] Sent %r:%r" % (user_id, message))
connection.close()
