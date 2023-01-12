import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials("guest", "guest")))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')
# There are a few exchange types available: direct, topic, headers and fanout. We'll focus on the last one -- the fanout. Let's create an exchange of that type, and call it logs:

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)
connection.close()