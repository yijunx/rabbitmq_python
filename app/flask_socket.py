# gunicorn -b 0.0.0.0:5000 --workers 4 --threads 100 app.flask_socket:app

from flask_sock import Sock
from flask import Flask, render_template, request
import pika
from datetime import datetime

app = Flask(__name__)
sock = Sock(app)


channels = {}
connections = {}


@app.route("/")
def index():
    return render_template("index.html")


def the_callback_for_queue(ws):
    def callback(ch, method, properties, body):
        try:
            ws.send(body.decode("utf-8"))
            print(f"from Q")
        except Exception as e:
            print("collected backend stuff from rabbit, but..")
            print("well we cannot send throught the websocket anymore")
            print("well we lose it..")
            print(e)
            ch.close()

    return callback


def the_callback_for_exchange(ws, queue_name, exchange, routing_key):
    # well the exchange way is exactly what we want..
    def callback(ch, method, properties, body):
        try:
            # maybe we can add some memory stuff...
            ws.send(body.decode("utf-8"))
            print(f"from X")
        except Exception as e:
            print("collected backend stuff from rabbit, but..")
            print("well we cannot send throught the websocket anymore")
            print(e)
            print("thus we close the channel")
            ch.queue_unbind(
                queue=queue_name, exchange=exchange, routing_key=routing_key
            )
            ch.close()

    return callback


@sock.route("/direct_exchange/<user_x>")
def ws_for_users_with_exchange_type_direct(ws, user_x):
    # message will be lost if there is no queue bind to it
    # this bind is at server side
    print(f"using X at {datetime.now()}")
    routing_key = user_x
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    exchange = "direct_logs"
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="direct")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange="direct_logs", queue=queue_name, routing_key=routing_key
    )
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=the_callback_for_exchange(
            ws, queue_name, exchange, routing_key
        ),
        auto_ack=True,
    )
    channel.start_consuming()


@sock.route("/queue/<user_x>")
def ws_for_users_with_simple_message_queue(ws, user_x):
    # in the case, the emitter already creates a queue
    # and then put message, so the message will not be lost

    # if there is multiple client, it sends to different chanels
    # this is the biggest issue..

    print(f"using Q at {datetime.now()}")
    # this is how backend get cookie
    print(request.cookies.get("X-Authorization", "no cookies"))

    # if user_x not in connections:
    #     print("creating new conn / channel")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # channel = channels[user_x]
    channel.queue_declare(queue=user_x)
    channel.basic_consume(
        queue=user_x, on_message_callback=the_callback_for_queue(ws), auto_ack=True
    )
    channel.start_consuming()
