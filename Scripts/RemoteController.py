#! python3

import socket
import re

re_PLC = re.compile(r'''PLC(\d):(-?\d+\.?\d*)''')
TCP_IP = '192.168.111.20'
TCP_PORT = 10000
BUFFER_SIZE = 1024
server_address = (TCP_IP,TCP_PORT)

#Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind the socket to the port
print('Starting up on %s port %s' % server_address)
sock.connect((TCP_IP, TCP_PORT))

def sendSetpoints(SP1,SP2,SP3):
    #format and encode message
    try:
        msg = str(SP1)+','+str(SP2)+','+str(SP3)
        msg = str.encode(msg)
    except:
        print('Message string encoding error!')
    #Send mesage over TCP to IoT_Gateway
    try:
        #print('Sending %s' %msg)
        sock.send(msg)
    except:
        print('TCP transmision error!')

#Receive and extract TCP message data
def receiveActVelocity():
    #receive TCP Data
    try:
        TCP_data = sock.recv(BUFFER_SIZE)
        TCP_data = TCP_data.decode('utf-8')
        print(TCP_data)
        ValTuple = re_PLC.findall(TCP_data)#Extract PLC number and PLC's velocity into a Tuple
    except:
        print('Error while receiving and extracting TCP data')
    return ValTuple

try:
    SP1 = 150.25
    SP2 = 1234
    SP3 = -1500
    sendSetpoints(SP1,SP2,SP3)
    while True:
        ActVelocityTuple = receiveActVelocity()
        for i in ActVelocityTuple:
            PLC_num = i[0]
            try:
                SpeedVal = float(i[1])
            except:
                print('ActVelocity type error!')
            if PLC_num=='1':
                if SpeedVal <1500:
                    SP1 = SpeedVal+1
                else:
                    SP1 =SpeedVal
            elif PLC_num == '2':
                if SpeedVal <1500:
                    SP2 = SpeedVal+1
            elif PLC_num == '3':
                if SpeedVal <1500:
                    SP3 =SpeedVal+1
            print("Received value from PLC %s: " % PLC_num, SpeedVal)
        sendSetpoints(SP1,SP2,SP3)
            
finally:
    sock.close()
    print('Closing socket')
