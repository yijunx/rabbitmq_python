import pika, sys, os, time

# round robin
# By default, RabbitMQ will send each message to the next consumer,
# in sequence. On average every consumer will get the same number of messages.
# This way of distributing messages is called round-robin.


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq", credentials=pika.PlainCredentials("guest", "guest")
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        time.sleep(body.count(b"."))
        print(" [x] Done")
        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    # this tells the rmq do not send stuff to busy places
    channel.basic_consume(queue="task_queue", on_message_callback=callback, auto_ack=False)
    # here there is auto_ack is True
    # it means that, when the worker gets the job
    # the message disappears from queue
    # if we want to remain the message till the job done,
    # turn it false, and add
    # ch.basic_ack(delivery_tag = method.delivery_tag) in the callback

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
