from flask_sock import Sock
from flask import Flask, render_template
import pika
from typing import Dict, List
from dataclasses import dataclass

app = Flask(__name__)
sock = Sock(app)
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()
channel.exchange_declare(exchange="direct_logs", exchange_type="direct")


@app.route('/')
def index():
    return render_template("index.html")

def the_callback(ws):
    def callback(ch, method, properties, body):
        ws.send(body.decode("utf-8"))
    return callback

# @sock.route('/user1')
# def ws_for_user1(ws):
#     routing_key = "user1"
#     channel.queue_bind(exchange="direct_logs", queue=queue_name, routing_key=routing_key)
#     channel.basic_consume(queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True)
#     channel.start_consuming()


# @sock.route('/user2')
# def ws_for_user2(ws):
#     routing_key = "user2"
#     channel.queue_bind(exchange="direct_logs", queue=queue_name, routing_key=routing_key)
#     channel.basic_consume(queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True)
#     channel.start_consuming()

@sock.route('/<user_x>')
def ws_for_users_with_exchange_type_direct(ws, user_x):
    print(user_x)
    routing_key = user_x

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="direct_logs", queue=queue_name, routing_key=routing_key)
    channel.basic_consume(queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True)
    channel.start_consuming()
# gunicorn -b 0.0.0.0:5000 --workers 4 --threads 100 app.flask_socket:app


# @sock.route('/queue/<user_x>') 
# # here we use a queue
# def ws_for_users_with_simple_message_queue(ws, user_x):
#     print(user_x)
#     routing_key = user_x
#     result = channel.queue_declare(queue="", exclusive=True)
#     queue_name = result.method.queue
#     channel.queue_bind(exchange="direct_logs", queue=queue_name, routing_key=routing_key)
#     channel.basic_consume(queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True)
#     channel.start_consuming()