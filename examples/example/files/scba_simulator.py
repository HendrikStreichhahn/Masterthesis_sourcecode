import random
import time
import threading
from tcp_receiver import tcp_receiver
from tcp_sender import tcp_sender

position_host = '127.0.0.1'
position_port = 8094

pressure_host = '127.0.0.1'
pressure_port = 8095

alarm_host = "127.0.0.1"
alarm_port = 8096


send_interval = 5

positionX = 0.0
positionY = 0.0
positionZ = 0.0
pressure = 300.0

def alarm_function(message):
    global send_interval 
    send_interval = 1

def messageSender():
    while True:
        sender_position.send(f"messure_position PositionX={positionX},PositionY={positionY},PositionZ={positionZ}")
        sender_pressure.send(f"measure_pressure pressure={pressure}")
        time.sleep(send_interval)

alarm_receiver = tcp_receiver(alarm_host, alarm_port, alarm_function)
alarm_receiver.start()


time.sleep(10)
sender_position = tcp_sender(position_host, position_port)
sender_pressure = tcp_sender(pressure_host, pressure_port)

sender_thread = threading.Thread(target=messageSender, args=())
sender_thread.start()

while True:
    time.sleep(1)
    positionX += random.uniform(-.1, .1)
    positionY += random.uniform(-.1, .1)
    positionZ += random.uniform(-.1, .1)
    pressure -= 0.05
    
    