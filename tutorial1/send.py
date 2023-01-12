import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials("guest", "guest")))
channel = connection.channel()


channel.queue_declare(queue="hello")
payload = {"hello": "world"}
channel.basic_publish(exchange='',
                      routing_key='hello',  # routing key has to be queue name
                      body=json.dumps(payload))
print(" [x] Sent 'Hello World!'")


connection.close()