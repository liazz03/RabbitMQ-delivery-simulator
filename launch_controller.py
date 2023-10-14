import pika 
import time
import uuid
import random
from enum import Enum
import pickle
import os


localhost = 'localhost'
uamserver = 'redes2.ii.uam.es'
hostname = uamserver

class STATUS(Enum):
    PENDING = "PENDING"     
    PROCESSING = "PROCESSING"   
    DELIVERING = "DELIVERING"  
    DELIVERED = "DELIVERED"    
    CANCELLED = "CANCELLED"    
    FAILEDTODELIVER = "FAILED TO DELIVER" 


class Order(object):
    def __init__(self,clientid,numProducts) -> None:
        self.orderid = uuid.uuid4() 
        self.clientid = clientid
        self.status = STATUS.PENDING
        #Revisar si esto es necesario porque dice que no hace falta modelar productos
        self.productsid = []

        #create an id for each product
        for i in range(0,numProducts):
            self.productsid.append(uuid.uuid4())

        self.deliveryAttempts = 0

    def __str__(self) -> str:
        return "Order id: " + str(self.orderid) + " Status: " + self.status.value



class Client(object):
    def __init__(self,user,password) -> None:
        self.user = user
        self.password = password
        self.id = uuid.uuid4()
        self.orders = [] 
        self.notifications = []

    def addOrder(self,order):
        self.orders.append(order)
    
    def RemoveOrder(self, order):
        self.orders.remove(order) 

    def __str__(self) -> str:
        return "id: " + str(self.id) + " User: " + self.user

class Controller(object):
     
    def __init__(self):
        

        orders_serialized = "orders_seriallized.pickle"
        clients_serialized = "clients_seriallized.pickle"
    
        pathorders = os.path.join(os.getcwd(),orders_serialized)
        pathclients = os.path.join(os.getcwd(),clients_serialized)

        #load clients
        if os.path.exists(pathclients):
            with open(clients_serialized, "rb") as file:
                serialized_clients = file.read()
                self.clients = pickle.loads(serialized_clients)
        else:
            self.clients = []

        #load orders
        if os.path.exists(pathorders):
            with open(orders_serialized, "rb") as file:
                serialized_orders = file.read()
                self.orders = pickle.loads(serialized_orders)
        else:
            self.orders = []

        #declare connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = hostname))
        self.channel = self.connection.channel()
        
        #RPC queue 
        self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
        self.channel.basic_qos(prefetch_count= 1)

        #controller queue
        self.channel.queue_declare(queue='2302_11_controller_queue_robot', durable=False, auto_delete=True)
        self.channel.queue_declare(queue='2302_11_controller_queue_delivery', durable=False, auto_delete=True)

    def start_consuming(self):

        #print
        print('Waiting for messages, to exit press Crl+C')

        self.channel.basic_qos(prefetch_count= 1)
        #RPC -- CLIENT COMMUNICATION
        self.channel.basic_consume(queue = '2302_11_rpc_queue', on_message_callback=self.on_request_rpc)

        #communication with robots and delivery people
        self.channel.basic_consume(queue = '2302_11_controller_queue_robot', on_message_callback=self.process_answers_robot)
        self.channel.basic_consume(queue = '2302_11_controller_queue_delivery', on_message_callback=self.process_answers_delivery)

        #consume (loop)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            #serialize clients and orders
            self.serialize_clients_orders()
            
            #close connection
            self.connection.close()
            print("Closing connection...")
    
    def serialize_clients_orders(self):
        #save clients and orders
        serialized_clients = pickle.dumps(self.clients)
        with open("clients_seriallized.pickle","wb") as file:
            file.write(serialized_clients)

        serialized_orders = pickle.dumps(self.orders)
        with open("orders_seriallized.pickle","wb") as file:
            file.write(serialized_orders)

    def process_answers_robot(self,ch,method,props,body):
        ch.basic_ack(delivery_tag = method.delivery_tag)

        #decode message
        mesg = body.decode()
        tokens = mesg.split()

        #find client
        orderid = tokens[1]
        for order in self.orders:
                if str(order.orderid) == orderid:
                    orderr = order
                    break
        clientid = orderr.clientid
        clientt = None
        for client in self.clients:
            if client.id == clientid:
                clientt = client
                break
        
        if tokens[0] == "PROCESSING":
            orderr.status = STATUS.PROCESSING
            notification = "order: " + orderid + " is being processed by a robot."
            print(notification)
            clientt.notifications.append(notification)
        
        elif tokens[0] == "PROCESSED":
            if orderr.status is not STATUS.CANCELLED:
                #sends order to delivery 
                self.channel.queue_declare(queue='2302_11_delivery_queue', durable=False, auto_delete=True)
                message_toDelivery = orderid
                self.channel.basic_publish(
                        exchange='',
                        routing_key='2302_11_delivery_queue',
                        body = message_toDelivery
                )

        elif tokens[0] == "NOTFOUND":
            notification = "product: " + tokens[2] + " of order: " + orderid + " was not found in storage."
            print(notification)
            clientt.notifications.append(notification)

    def process_answers_delivery(self,ch,method,props,body):
        ch.basic_ack(delivery_tag = method.delivery_tag)

        #decode message
        mesg = body.decode()
        tokens = mesg.split()

        #find client
        orderid = tokens[1]
        for order in self.orders:
                if str(order.orderid) == orderid:
                    orderr = order
                    break
        clientid = orderr.clientid
        clientt = None
        for client in self.clients:
            if client.id == clientid:
                clientt = client
                break

        if tokens[0] == "DELIVERING":
            orderr.status = STATUS.DELIVERING
            notification = "order: " + orderid + " is on delivery process."
            clientt.notifications.append(notification)
            print(notification)

        elif tokens[0] == "DELIVERED" :
            orderr.status = STATUS.DELIVERED
            notification = "order: " + orderid + " was delivered"
            clientt.notifications.append(notification)
            print(notification)

        elif tokens[0] == "NOTDELIVERED":
       
            #Review attepts and change status
            if orderr.deliveryAttempts == 2:
                orderr.status = STATUS.FAILEDTODELIVER
                notification = "Failed to deliver order: " + orderid 
                clientt.notifications.append(notification)
                print(notification)
                return
            
            else:
                orderr.deliveryAttempts = orderr.deliveryAttempts + 1

                notification = "Failed to deliver order: " + orderid + " on attempt " + str(orderr.deliveryAttempts)
                clientt.notifications.append(notification)
                print(notification)

                #reattempt derlivery
                #sends order to delivery 
                self.channel.queue_declare(queue='2302_11_delivery_queue', durable=False, auto_delete=True)
                message_toDelivery = orderid
                self.channel.basic_publish(
                        exchange='',
                        routing_key='2302_11_delivery_queue',
                        body = message_toDelivery
                    )

    def on_request_rpc(self,ch,method,props,body):

        #decode message
        mesg = body.decode()
        tokens = mesg.split()

        print("RPC Request for: "+ tokens[0])

        #verify client
        if tokens[0] == "LOGIN":
            exists = False
            for client in self.clients:
                if client.user == tokens[1] and client.password == tokens[2]:
                    exists  = True
            
            if exists:
                response = "LOGEDIN"
            else:
                response = "ERRORLOGIN"

            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))

            ch.basic_ack(delivery_tag = method.delivery_tag)

        #add new client
        elif tokens[0] == "REGISTER" :
            new_client = Client(tokens[1], tokens[2])
            self.clients.append(new_client)

            response = "REGISTERED"

            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)

        #New Order
        elif tokens[0] == "DOORDER" :
            client_username = tokens[1]

            #get client 
            clientt = None
            for client in self.clients:
                if client.user == client_username:
                    clientt = client
            
            #create order
            new_order = Order(clientt.id, int(tokens[2]))
            clientt.addOrder(new_order)
            self.orders.append(new_order)

            #create reponse to client
            response = "ORDERCREATED"
            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))


            ch.basic_ack(delivery_tag = method.delivery_tag)

            #send order to robot queue
            self.channel.queue_declare(queue='2302_11_robot_queue', durable=False, auto_delete=True)
            message_toRobot = " " + str(new_order.orderid) + " "

            for prodid in new_order.productsid:
                message_toRobot = message_toRobot + str(prodid) + " "

            self.channel.basic_publish(
                    exchange='',
                    routing_key='2302_11_robot_queue',
                    body = message_toRobot
                )

        #ViewOrder
        elif tokens[0] == "VIEWORDERS" :
            client_username = tokens[1]

            #get client 
            clientt = None
            for client in self.clients:
                if client.user == client_username:
                    clientt = client
            
            response = "ORDERS: \n" 
            for order in clientt.orders:
                response = response + str(order) + "\n"

            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)

        #cancell order
        elif tokens[0] == "CANCELORDER" :
            orderid = tokens[1]

            response = None
            #getorder
            for order in self.orders:
                if str(order.orderid) == orderid:
                    if order.status.value != "DELIVERING" and order.status.value != "DELIVERED" and order.status.value != "CANCELLED":
                        order.status = STATUS.CANCELLED
                        response = "Order with id:  " + orderid + " was cancelled"
                    else:
                        response = "Order with id:  " + orderid + " cannot be cancelled"

                    break
            
            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
        
        #view notifications
        elif tokens[0] == "SEENOTIFICATIONS":
            client_username = tokens[1]

            #get client 
            clientt = None
            for client in self.clients:
                if client.user == client_username:
                    clientt = client
            
            response = "NOTIFICATIONS: \n" 

            for notification in clientt.notifications:
                response = response + notification + "\n"
            
            ch.basic_publish(exchange = '', routing_key = props.reply_to, properties = pika.BasicProperties(correlation_id= props.correlation_id),
                            body = str(response))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)

def main():

    controller = Controller()
    controller.start_consuming()

if __name__ == '__main__':
    main()

