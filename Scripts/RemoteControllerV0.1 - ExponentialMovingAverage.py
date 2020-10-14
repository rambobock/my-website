#! python3

#Import all required library and modules
import socket, re, threading, subprocess, time

re_PLC = re.compile(r'''PLC(\d):(-?\d+\.?\d*)''')#Regular expresion to extract PLC numbers and their measured motor velocities
TCP_IP = '192.168.111.20'#Industrial network address
#TCP_IP = '192.168.0.4'#Consumer network address
TCP_PORT = 10000#TCP/ip connection port
BUFFER_SIZE = 1024#TCP/IP Message buffer size
server_address = (TCP_IP,TCP_PORT)

#Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind the socket to the port
print('Starting up on %s port %s' % server_address)
sock.connect((TCP_IP, TCP_PORT))


def sendSetpoints(SP1,SP2,SP3):#Format and send set-points to the IoT gateway
    #format and encode message
    try:
        msg = str(SP1)+','+str(SP2)+','+str(SP3)+'$'
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

def step1():#First step for motor1 @ 0.4Seconds
    global SetPoint1
    SetPoint1 = 1500
    sendSetpoints(SetPoint1,0,0)

def step2():#Second step for motor1  @ 3.0Seconds
    global SetPoint1
    SetPoint1 = -1500

def end():#Copy measurement log files from IoT gateway to Remote server for result analysis @ 7.0Seconds
    subprocess.call([r'C:\Users\Randolph\Desktop\CopyMeasurementsFromNR.bat'])#Copy velocity log files from IoT gateway to remote server computer (Industrial network address)
    #subprocess.call([r'C:\Users\Randolph\Desktop\CopyMeasurementsFromNR_ConNet.bat'])#Copy velocity log files from IoT gateway to remote server computer (Consumer network address)

#Create interrupts required for step1, step2 and end functions
t1 = threading.Timer(0.4, step1)
t2 = threading.Timer(7.0, step2)
t3 = threading.Timer(12.0, end)

try:
    global SetPoint1, SetPoint2, SetPoint3#Setpoint variables
    global ActVelocity1, ActVelocity2, ActVelocity3#Measurement value variables
    global m1St, m2St, m3St, a # Exponential Moving average variables.

    #Initialize variables
    a = 0.8
    m1St, m2St, m3St = 0, 0, 0
    start = False# test start variable
    SetPoint1, SetPoint2, SetPoint3, ActVelocity1, ActVelocity2, ActVelocity3 = 0,0,0,0,0,0

    sendSetpoints(SetPoint1,SetPoint2,SetPoint3)#Send 0 rpm setpoint to reset any setpoint in the motors

    time.sleep(0.2)
    print('Test starting!!!!!!')
    t1.start()
    t2.start()
    t3.start()
    while True:
        #receive and interpret motor measurements received
        ActVelocityTuple = receiveActVelocity()
        for i in ActVelocityTuple:
            PLC_num = i[0]
            try:
                SpeedVal = float(i[1])
            except:
                print('ActVelocity type error!')
            if PLC_num == '1':
                ActVelocity1 = SpeedVal
                m1St = (a*SpeedVal) + (1-a)*m1St
            elif PLC_num == '2':
                ActVelocity2 = SpeedVal
                m2St = (a*SpeedVal) + (1-a)*m2St
            elif PLC_num == '3':
                ActVelocity3 = SpeedVal
                m3St = (a*SpeedVal) + (1-a)*m3St
            #Calculate setpoints accourding to mission scheme
            SetPoint2 = -m1St
            SetPoint3=(-2/3)*m2St                
            print("Received value from PLC %s: " % PLC_num, SpeedVal)
        sendSetpoints(SetPoint1,SetPoint2,SetPoint3)#Send set-points
        #time.sleep(0.01)
            
finally:
    sock.close()#Close connection socket
    print('Closing socket')
