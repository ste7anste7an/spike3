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
    """
    This funtion converts a bytes string to the format of the argument of the color_matrix_show() function.
    """
    val_int=int(b.hex(),16) # convert from bytes to hex to decimal integer
    base11=numberToBase(val_int,11) # convert integer base 10 to integer base 11
    l=len(base11)
    q=[0]*(18-l)+base11 # add zero's for total length of 18
    return [(i,j) for i,j in zip(q[1::2],q[::2])] # convert list of 18 base-11 digits, to list of 2-tuples

def send_to_esp(b):
    color_matrix.show(1,to_color(b))
    
for i in range(100):
    # send data to lms-esp32
    send_to_esp(f'cnt:{i}'.encode('utf-8'))
    # receive 8 bytes from lms-esp and convert them to unsigned bytes.
    print([i+128 for i in device.data(1)])
    time.sleep_ms(20)
