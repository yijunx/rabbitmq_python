import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq', credentials=pika.PlainCredentials("guest", "guest")))
channel = connection.channel()
# As you see, after establishing the connection we declared the exchange. 
# This step is necessary as publishing to a non-existing exchange is forbidden.
channel.exchange_declare(exchange='logs', exchange_type='fanout')
# There are a few exchange types available: direct, topic, headers and fanout. We'll focus on the last one -- the fanout. Let's create an exchange of that type, and call it logs:

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)

# The messages will be lost if no queue is bound to the exchange yet,
# but that's okay for us; if no consumer is listening yet we can safely discard the message.
print(" [x] Sent %r" % message)
connection.close()