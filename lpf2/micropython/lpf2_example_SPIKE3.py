import device
import color_matrix
import time

def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def to_color(b):
    val_int=int(b.hex(),16)
    base11=numberToBase(val_int,11)
    l=len(base11)
    q=[0]*(18-l)+base11
    return [(i,j) for i,j in zip(q[1::2],q[::2])]

def send_to_esp(b):
    color_matrix.show(1,to_color(b))
    
for i in range(100):
    send_to_esp(f'cnt:{i}'.encode('utf-8'))
    print([i+128 for i in device.data(1)])
    time.sleep_ms(20)