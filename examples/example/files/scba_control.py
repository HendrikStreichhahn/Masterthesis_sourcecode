from tcp_receiver import tcp_receiver
from tcp_sender import tcp_sender

position_x = None
position_y = None
position_z = None
pressure = None

pos_treshold = 10
pres_treshold = 50

alarm_host = "127.0.0.1"
alarm_port = 8096

host_urls = "127.0.0.1"
host_ports = [8094, 8095]

def handle_message(data):
    global position_x, position_y, position_z, pressure
    inpFields = data.strip().split(' ')
    fields = inpFields[1].strip().split(',')
    for field in fields:
        if '=' in field:
            key, value = field.split('=')
            if key == 'PositionX':
                position_x = float(value)
            elif key == 'PositionY':
                position_y = float(value)
            elif key == 'PositionZ':
                position_z = float(value)
            elif key == 'pressure':
                pressure = float(value)
    if (position_x is not None and position_x > pos_treshold or
        position_y is not None and position_y > pos_treshold or
        position_z is not None and position_z > pos_treshold or
        pressure is not None and pressure < pres_treshold):
        sendAlarm(alarm_host, alarm_port)
    else:
        print("is ok")

def sendAlarm(host, port):
    sender = tcp_sender(host, port)
    sender.connect()
    sender.send("alarm alarm=true")
    sender.disconnect()


servers: list([tcp_receiver]) = []

for port in host_ports:
    newServer = tcp_receiver(host_urls, port, handle_message)
    newServer.start()
    servers.append(newServer)