

import pika
import sys
import uuid
import time

localhost = 'localhost'
uamserver = 'redes2.ii.uam.es'
hostname = uamserver

class SaimazoonClient(object):

    def __init__(self):
        #declare connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = hostname))
        self.channel = self.connection.channel()

        #rpc queue
        result = self.channel.queue_declare(queue='', exclusive= True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue,
                            on_message_callback=self.on_response,
                            auto_ack=True)

        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()
        else:
            return

        if "ORDERS:" in self.response or "NOTIFICATIONS:" in self.response:
            print(self.response)
            return

        #Do appropiate thing 
        rpta = self.response
        rptta = rpta.split()
        msgcode = rptta[0]

        if msgcode == "LOGEDIN":
            self.logedin = True
            print("Loged-in!")
        elif msgcode == "ERRORLOGIN":
            self.username = None
            print("Credentials are not valid!")
        elif msgcode == "REGISTERED":
            print("Correctly registered!")
        elif msgcode == "ORDERCREATED":
            print("Order performed correctly")
        else:
            print(self.response)
    
    def HandleOrders(self):

        usuario = "Simulacioncliente"
        passw = "Simulacioncliente"

        #builds message to register
        msg_register = "REGISTER "+ usuario + " " + passw

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_register,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)
    
        #builds message to log in
        msg_register = "LOGIN "+ usuario + " " + passw

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_register,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)

        #builds message to do order 
        print("Preforming 3 orders each with different number of products...")

        #order 1
        numero_producos_orden = 3
        msg_DoOrder = "DOORDER "+ usuario + " " + str(numero_producos_orden)

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_DoOrder,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id= self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)

        #order 2
        numero_producos_orden = 2
        msg_DoOrder = "DOORDER "+ usuario + " " + str(numero_producos_orden)

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_DoOrder,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id= self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)

        #order 3
        numero_producos_orden = 1
        msg_DoOrder = "DOORDER "+ usuario + " " + str(numero_producos_orden)

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_DoOrder,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id= self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)

    
        #builds message to view orders
        msg_ViewOrder = "VIEWORDERS "+ usuario

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_ViewOrder,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)
        
        #builds message
        msg_showNotifications = "SEENOTIFICATIONS "+ usuario

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_showNotifications,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)

        print("Preforming a 10 seconds sleep...")

        time.sleep(10)

        #builds message to view orders
        msg_ViewOrder = "VIEWORDERS "+ usuario

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_ViewOrder,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)
        
        #builds message
        msg_showNotifications = "SEENOTIFICATIONS "+ usuario

        #sends message to corresponding controller queue
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_publish(
            exchange='',
            routing_key='2302_11_rpc_queue',
            body = msg_showNotifications,
            properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
        )
        self.connection.process_data_events(time_limit=None)


        for i in range(0,10):
            print("Preforming a 15 seconds sleep...")
            time.sleep(15)

            #builds message to view orders
            msg_ViewOrder = "VIEWORDERS "+ usuario

            #sends message to corresponding controller queue
            self.corr_id = str(uuid.uuid4())
            self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
            self.channel.basic_publish(
                exchange='',
                routing_key='2302_11_rpc_queue',
                body = msg_ViewOrder,
                properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
            )
            self.connection.process_data_events(time_limit=None)
            

            #builds message
            msg_showNotifications = "SEENOTIFICATIONS "+ usuario

            #sends message to corresponding controller queue
            self.corr_id = str(uuid.uuid4())
            self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
            self.channel.basic_publish(
                exchange='',
                routing_key='2302_11_rpc_queue',
                body = msg_showNotifications,
                properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
            )
            self.connection.process_data_events(time_limit=None)


def main():
    #Create client class
    client = SaimazoonClient()

    #handle orders
    client.HandleOrders()

    client.connection.close()

if __name__ == '__main__':
    main()