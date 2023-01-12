# gunicorn -b 0.0.0.0:5000 --workers 4 --threads 100 app.flask_socket:app

from flask_sock import Sock
from flask import Flask, render_template, request
import pika
from typing import Dict, List
from dataclasses import dataclass

app = Flask(__name__)
sock = Sock(app)


@app.route("/")
def index():
    return render_template("index.html")


def the_callback(ws):
    def callback(ch, method, properties, body):
        ws.send(body.decode("utf-8"))

    return callback


@sock.route("/direct_exchange/<user_x>")
def ws_for_users_with_exchange_type_direct(ws, user_x):
    # message will be lost if there is no queue bind to it
    print("using X")
    routing_key = user_x
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))

    channel = connection.channel()
    channel.exchange_declare(exchange="direct_logs", exchange_type="direct")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange="direct_logs", queue=queue_name, routing_key=routing_key
    )
    channel.basic_consume(
        queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True
    )
    channel.start_consuming()


@sock.route("/queue/<user_x>")
def ws_for_users_with_simple_message_queue(ws, user_x):
    # in the case, the emitter already creates a queue
    # and then put message, so the message will not be lost
    print("using Q")
    # this is how backend get cookie
    print(request.cookies.get("X-Authorization", "no cookies"))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue=user_x)
    channel.basic_consume(
        queue=user_x, on_message_callback=the_callback(ws), auto_ack=True
    )
    channel.start_consuming()
