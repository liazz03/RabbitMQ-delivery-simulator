import pika
import sys
import uuid

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
        self.response = None
        self.logedin = False
        self.username = None

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


    def log_reg(self):

        #Register or Login
        while(self.logedin == False):
            opcion = input("Select an option: \n1.Register \n2.Log-in\nPress Ctrl+C to exit\n" )

            if opcion == '1':
                usuario=input("Introduzca nuevo nombre de usuario")
                passw = input("Introduzca nueva contraseña")

                #builds message
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


            elif opcion == '2':
                usuario=input("Introduzca nombre de usuario")
                passw = input("Introduzca contraseña")
                self.username = usuario
                #builds message
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
    
    def HandleOrders(self):

        print("----------------------------USER SPACE----------------------------------")
        
        while(True):
            opcion = input("Select an option: \n1.Make order \n2.See Order\n3.Cancell Order\n4.See notifications\nPress Ctrl+C to exit\n" )

            if opcion == '1':
                numprod= input("Indicate how many products your Order has: ")
            
                #builds message
                msg_DoOrder = "DOORDER "+ self.username + " " + numprod

                #sends message to corresponding controller queue
                self.corr_id = str(uuid.uuid4())
                self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
                self.channel.basic_publish(
                    exchange='',
                    routing_key='2302_11_rpc_queue',
                    body = msg_DoOrder,
                    properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
                )
                self.connection.process_data_events(time_limit=None)

            elif opcion == '2':
               #builds message
                msg_ViewOrder = "VIEWORDERS "+ self.username

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

            elif opcion == '3':

                orderid = input("Insert Orderid to cancell: ")

                
                #builds message
                msg_CancellOrder = "CANCELORDER "+ orderid

                #sends message to corresponding controller queue
                self.corr_id = str(uuid.uuid4())
                self.channel.queue_declare(queue='2302_11_rpc_queue', durable=False, auto_delete=True)
                self.channel.basic_publish(
                    exchange='',
                    routing_key='2302_11_rpc_queue',
                    body = msg_CancellOrder,
                    properties=pika.BasicProperties(reply_to=self.callback_queue,correlation_id=self.corr_id)
                )
                self.connection.process_data_events(time_limit=None)          

            elif opcion == '4':
                
                #builds message
                msg_showNotifications = "SEENOTIFICATIONS "+ self.username

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
    
    #ask for login/registration
    client.log_reg()

    #handle orders
    client.HandleOrders()

    client.connection.close()

if __name__ == '__main__':
    main()
