import threading

def hello():
    global a
    print('Hello')
    a=1

def hello2():
    global b
    print('msp')
    b=1
    
t1 = threading.Timer(1, hello)
t2 = threading.Timer(2, hello2)
t1.start()
t2.start()

a=0
b=0
while(a==0):
   print("you're here")

while(b==0):
    print('.')
print('Good By')
