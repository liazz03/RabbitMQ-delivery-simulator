import pika 
import time
import uuid
import random

localhost = 'localhost'
uamserver = 'redes2.ii.uam.es'
hostname = uamserver

#probability of successful delivery
p_entrega = 0.5

class Delivery(object):


    def deliver_order(self,ch,method,props,body):

        ch.basic_ack(delivery_tag = method.delivery_tag)

        #decode message
        mesg = body.decode()
        tokens = mesg.split()

        orderid = tokens[0]

        print("Delivering order: " + orderid)

        #sends message to corresponding controller queue informing order is in delivery
        message_to_controller = "DELIVERING " + orderid        
        
        self.channel.queue_declare(queue='2302_11_controller_queue_delivery', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_controller_queue_delivery',
            body = message_to_controller
        )

        #random delivery time between 5 and 10 seconds
        time_toProcess = random.randint(10,20)
        time.sleep(time_toProcess)

        #simulates a probability of delivery sucess
        if random.random() > p_entrega:
            message_to_controller = "NOTDELIVERED " + orderid
        else:
            message_to_controller = "DELIVERED " + orderid

        #sends message to corresponding controller queue
        self.channel.queue_declare(queue='2302_11_controller_queue_delivery', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_controller_queue_delivery',
            body = message_to_controller
        )



    def __init__(self):


        #declare connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = hostname))
        self.channel = self.connection.channel()

        #RobotQueue
        self.channel.queue_declare(queue='2302_11_delivery_queue', durable=False, auto_delete=True)
        self.channel.basic_qos(prefetch_count= 1)

        #Wait for controller messages
        self.channel.basic_consume(queue = '2302_11_delivery_queue', on_message_callback=self.deliver_order)

        #print
        print('Waiting for messages, to exit press Crl+C')

        #consume (loop)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Closing connection...")
    


def main():

    #crea delivery
    robot = Delivery()

    robot.connection.close()


if __name__ == '__main__':
    main()
