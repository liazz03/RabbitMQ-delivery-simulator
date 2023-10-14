# REDES_P2
Ejecución de la práctica

La práctica cuenta con una variable global (hostname) en todos los actores donde se puede modificar el nombre de servidor host de las colas utilizadas a local host o redes.ii.uam.es.

La práctica se puede probar a través de las siguientes formas:

Lanzando todos los actores y commandline_client.py: se tiene que ejecutar launch_robot.py, launch_controller.py y launch_delivery.py y finalmente commandline_client.py. Se podrá ingresar órdenes, ver órdenes, cancelar órdenes y ver notificaciones por linea de comandos. Previamente el cliente deberá registrarse y luego loggearse.

Lanzando todos los actores y launch_client.py: se tiene que ejecutar launch_robot.py, launch_controller.py y launch_delivery.py y finalmente launch_client.py. Launch_client crea 1 cliente y lanza 3 órdenes con diferente número de productos, se hacen 10 sleeps de 15 segundos y luego de cada uno se envían mensajes de petición a la cola RPC para mostrar notificaciones y estado de los pedidos.

Lanzando el script de bash: Se ejecuta todo el sistema ejecutando ./launch_system.sh. Este script lanza un controlador, dos robots, dos deliverys y el launch_client.py en terminales separadas (procesos separados). Cada terminal lleva el nombre del actor correspondiente.

Importante: El comando de cancelar una orden podrá probarse únicamente ejecutando commandline_client.py, pues se necesita visualizar las órdenes (petición de View Orders a cola RPC de controlador) para poder saber el id (uuid4) del pedido a cancelar.
