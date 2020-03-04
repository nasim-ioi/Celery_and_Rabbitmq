import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

message_list = sys.argv[1:]
if not message_list:
    sys.stderr.write(" please say seller or customer,name of stock,percent of stock,name,email %s \n" % sys.argv[0])
    sys.exit(1)
else:
    message = message_list[0]
    input_list = message.split(',') #seller or customer,name of stock,percent of stock,name,email
    if len(input_list) != 5:
        sys.stderr.write(" please say seller or customer,name of stock,percent of stock,name,email %s \n" % sys.argv[0])
        sys.exit(1)

# print("input_list: ", input_list)

queue_name = input_list[0] + '_' + input_list[1]
# print("queue_name: ",queue_name)

channel.queue_declare(queue = queue_name, durable = True)

exchange_name = input_list[1] + '_' + 'exchange'
# print("exchange_name: ",exchange_name)

channel.exchange_declare(exchange_name , exchange_type = 'direct')

channel.queue_bind(exchange = exchange_name, queue = queue_name, routing_key = input_list[0])

channel.basic_publish(exchange = exchange_name, routing_key = input_list[0], body = message, properties=pika.BasicProperties(delivery_mode = 2,))

print("Sent %r:%r" % (queue_name, message))

connection.close()