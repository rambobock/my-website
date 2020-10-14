#! python3

import socket
import re

re_PLC = re.compile(r'''PLC(\d):(-?\d+\.?\d*)''')

TCP_IP = '192.168.111.20'
TCP_PORT = 10000
BUFFER_SIZE = 1024
MESSAGE = '-1500,1500,-1500'
MESSAGE = str.encode(MESSAGE)
server_address = (TCP_IP,TCP_PORT)

#Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind the socket to the port
print('Starting up on %s port %s' % server_address)
sock.connect((TCP_IP, TCP_PORT))

try:
    #Send data
    print('Sending "%s"' %MESSAGE)
    sock.send(MESSAGE)

    try:
        while True:
            #Receive and Print Values:
            TCP_data = sock.recv(BUFFER_SIZE)
            TCP_data = TCP_data.decode('utf-8')
            print(TCP_data)
            ValTuple = re_PLC.findall(TCP_data)
            for i in ValTuple:
                PLC_num = i[0]
                SpeedVal = float(i[1])
                print("Received value from PLC %s: " % PLC_num, SpeedVal)
    except:
        print('done')


finally:
    sock.close()
    print('Closing socket')


