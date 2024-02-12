_="""
import hub


a=hub.port.A
da=a.device

while 1:
      print(da.get(0))

"""
_="""
from pybricks.iodevices import PUPDevice
p=PUPDevice(Port.A)
p.read(0)
"""

_="""
# SPIKE3
import hub
import device
device.data(hub.port.A)

import binascii
import struct
def parse(a):
    s=b''
    s+=struct.pack('b',a[0])
    s+=struct.pack('i',a[1])
    s+=struct.pack('h',a[2])
    #print(a)
    print(binascii.hexlify(s))
    
parse(device.data(hub.port.A))
"""


import gc,utime
import micropython
import lpf2_new as LPF2
from machine import Pin
from utime import ticks_ms,ticks_diff
micropython.alloc_emergency_exception_buf(200)

# num_bits = LPF2.__num_bits()

# Name, Format [# datasets, type, figures, decimals], 
# raw [min,max], Percent [min,max], SI [min,max], Symbol, functionMap [type, ?], view, tot_datasize, tot_bits
#modes[0]= {'symbol': 'PCT', 'format': {'datasets': 1, 'type': 0, 'figures': 1, 'decimals': 0}, 'capability': b'\x10\x00\x00\x00\x01\x04', 'map_out': 16, 'name': 'POWER', 'pct': (-100.0, 100.0), 'map_in': 0, 'si': (-100.0, 100.0), 'raw': (-100.0, 100.0)}
#modes[1]= {'symbol': 'PCT', 'format': {'datasets': 1, 'type': 0, 'figures': 4, 'decimals': 0}, 'capability': b'\x10\x00\x00\x00\x01\x04', 'map_out': 16, 'name': 'SPEED', 'pct': (-100.0, 100.0), 'map_in': 16, 'si': (-100.0, 100.0), 'raw': (-100.0, 100.0)}
#modes[2]= {'symbol': 'DEG', 'format': {'datasets': 1, 'type': 2, 'figures': 4, 'decimals': 0}, 'capability': b'\x10\x00\x00\x00\x01\x04', 'map_out': 8, 'name': 'POS', 'pct': (-100.0, 100.0), 'map_in': 8, 'si': (-360.0, 360.0), 'raw': (-360.0, 360.0)}
#modes[3]= {'symbol': 'DEG', 'format': {'datasets': 1, 'type': 1, 'figures': 3, 'decimals': 0}, 'capability': b'"\x00\x00\x00\x01\x04', 'map_out': 8, 'name': 'APOS', 'pct': (-200.0, 200.0), 'map_in': 8, 'si': (-180.0, 179.0), 'raw': (-180.0, 179.0)}
#modes[4]= {'symbol': 'PCT', 'format': {'datasets': 1, 'type': 0, 'figures': 1, 'decimals': 0}, 'capability': b' @\x00\x00\x01\x04', 'map_out': 8, 'name': 'LOAD', 'pct': (0.0, 100.0), 'map_in': 8, 'si': (0.0, 127.0), 'raw': (0.0, 127.0)}


# 0x00 0x30 0x00 0x00 0x00 0x05 0x04
pwr=b'\x00\x80\x00\x00\x00\x05\x04'
mode0 = [b'LEV O'+pwr,[9,LPF2.DATA8,1,0],[-9,9],[-100,100],[-9,9],'PCT',[0x0,0x50],True,1,0]
mode0 = [b'LEV O'+pwr,[8,LPF2.DATA8,1,0],[-9,9],[-100,100],[-9,9],'PCT',[0x0,0x50],True,8,3]
# 0x00 0x21 0x00 0x00 0x00 0x05 0x04
mode1 = [b'COL O'+pwr,[1,LPF2.DATA8,2,0],[0,10],[0,100],[0,10],'PCT',[0x0,0x44],True,1,0]
#  0x00 0x00 0x00 0x24 0x00 0x00 0x00 0x05 0x04
mode2 = [b'PIX O'+pwr,[9,LPF2.DATA8,3,0],[0,170],[0,100],[0,170],'   ',[0x0,0x10],True,16,4]
#  0x00 0x00 0x22 0x00 0x00 0x00 0x05 0x04 0x00 0x00 0x00 0x00
mode3 = [b'TRANS'+pwr,[1,LPF2.DATA8,1,0],[0,2],[0,100],[0,2],'   ',[0x0,0x10],True,1,0]
# 0x00 0x22 0x40 0x00 0x00 0x05 0x04
modes=[mode0,mode1,mode2,mode3]#,mode4]#,mode5]
#led = Pin(2, mode=Pin.OUT)
#led.on()
txpin=19
rxpin=18

from neopixel import NeoPixel
np=NeoPixel(Pin(21),64)

colors=[(0,0,0),(200,200,255),(255,0,255),(0,0,255),(0,255,255),(0,255,150),(0,255,0),(255,255,0),(255,140,0),(255,0,0),(255,255,255)]
pix=[0,1,2,8,9,10,16,17,18]

def process2(data):
    h=data.hex()
    print(h)
    for p in range(9):
        col=colors[int(h[p*2+1],16)]
        bright=int(h[p*2],16)
        colnew=(int(col[0]/10.0*bright),int(col[1]/10.0*bright),int(col[2]/10.0*bright))
        #print(p,int(h[p*2],16),int(h[p*2+1],16),col,colnew)
        np[pix[p]+3]=colnew
    np.write()

def process(data):
    print(data.hex())
    raw_int=int(data.hex()[:18],11)
    #print(raw_int)
    print(raw_int.to_bytes(8,'big'))
    
connected = False
last_heartbeat = ticks_ms()
heartbeat_interval = 20
small_grey_motor=48
light_sensor=0x3d
lpup = LPF2.ESP_LPF2(modes,sensor_id=0x40,debug=False)
buf=None
value=0
old_mode=0
old_tick=0
ms20_tick=0
data_old=None
while 1:
        # Get data from the hub and return previously stored payloads
        data = lpup.heartbeat()
        if data!=None:
            if data!=data_old:
                #print(data.hex())
                data_old=data
                process(data)
        if ticks_diff(ticks_ms(),old_tick)>50:
            old_tick=ticks_ms()
            #print([value+2*i+(value+2*i+10)*256 for i in range(8)])
            value = value + 1
            value = value %140
        mode=lpup.current_mode
        if old_mode != mode:
            old_mode=mode
            print("mode=",mode)
        if ticks_diff(ticks_ms(),ms20_tick)>20:
            ms20_tick=ticks_ms()
            if lpup.connected:
                if mode==0:
                   ar=[value+i for i in range(8)]
                   #ar[0]=value
                   buf=lpup.send_payload(ar,LPF2.DATA8)
                   if buf!=None:
                       print(buf)
                if mode==1:
                   ar=[value+i for i in range(1)]
                   #ar[0]=value
                   buf=lpup.send_payload(ar,LPF2.DATA8)
                   if buf!=None:
                       print(buf)
                if mode==2:
                   ar=[value+i*5 for i in range(9)]
                   ar=[b+128 if b<=127 else b-128 for b in ar]
                   buf=lpup.send_payload(ar,LPF2.DATA8)
                   if buf!=None:
                       print('buf mode2=',buf)
                if mode==3:
                   ar=[value+i*2 for i in range(9)]
                   buf=lpup.send_payload(ar,LPF2.DATA8)
                   if buf!=None:
                       print(buf)
                
           #elif mode==1:
        #   lpup.send_payload(value*2,LPF2.DATA16)
        #print(value)
        #utime.sleep_ms(20)

