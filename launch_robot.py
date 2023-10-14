import pika 
import time
import uuid
import random

localhost = 'localhost'
uamserver = 'redes2.ii.uam.es'
hostname = uamserver

#probability of finding product in storage 
p_almacen = 0.8

class Robot(object):


    def process_order(self,ch,method,props,body):

        ch.basic_ack(delivery_tag = method.delivery_tag)

        #decode message
        mesg = body.decode()
        tokens = mesg.split()

        orderid = tokens[0]
        products = tokens[1:]

        print("Processing order: " + orderid)

        #sends message to corresponding controller queue informing order is processing
        message_to_controller = "PROCESSING " + orderid

        self.channel.queue_declare(queue='2302_11_controller_queue_robot', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_controller_queue_robot',
            body = message_to_controller
        )

        message_to_controller = ""

        #for each product simulates a probability of finding it in storage
        for product in products:
            
            #random processing time between 5 and 10 seconds
            time_toProcess = random.randint(5,10)
            time.sleep(time_toProcess)

            if random.random() > p_almacen:
                message_to_controller = "NOTFOUND " + orderid + " " + product

                #sends message to corresponding controller queue
                self.channel.queue_declare(queue='2302_11_controller_queue_robot', durable=False, auto_delete=True)
                self.channel.basic_publish(
                    exchange='',
                    routing_key='2302_11_controller_queue_robot',
                    body = message_to_controller
                )

        #sends message to corresponding controller queue informing order is processed
        message_to_controller = "PROCESSED " + orderid

        self.channel.queue_declare(queue='2302_11_controller_queue_robot', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_controller_queue_robot',
            body = message_to_controller
        )


    def __init__(self):


        #declare connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = hostname))
        self.channel = self.connection.channel()

        #RobotQueue
        self.channel.queue_declare(queue='2302_11_robot_queue', durable=False, auto_delete=True)
        self.channel.basic_qos(prefetch_count= 1)

        #Wait for controller messages
        self.channel.basic_consume(queue = '2302_11_robot_queue', on_message_callback=self.process_order)

        #print
        print('Waiting for messages, to exit press Crl+C')

        #consume (loop)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Closing connection...")
    


def main():

    #crea robot
    robot = Robot()

    robot.connection.close()


if __name__ == '__main__':
    main()
