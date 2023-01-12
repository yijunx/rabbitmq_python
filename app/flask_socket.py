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
result = channel.queue_declare(queue="", exclusive=True)
queue_name = result.method.queue

@app.route('/')
def index():
    return render_template("index.html")

def the_callback(ws):
    def callback(ch, method, properties, body):
        ws.send(body.decode("utf-8"))
    return callback

@sock.route('/echo')
def echo(ws):
    routing_key = "user1"
    channel.queue_bind(exchange="direct_logs", queue=queue_name, routing_key=routing_key)
    channel.basic_consume(queue=queue_name, on_message_callback=the_callback(ws), auto_ack=True)
    channel.start_consuming()
# gunicorn -b 0.0.0.0:5000 --workers 4 --threads 100 app.flask_socket:app