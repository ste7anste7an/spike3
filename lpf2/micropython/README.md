# LPF2 for SPIKE3
## init baudrate at 115200
```
  def init(self):
        self.write_tx_pin(0, 450)
        self.write_tx_pin(1, 0)
        self.fast_uart()
        self.writeIt(b"\x04")
```
Removed change speed command in initilasation

```
def initialize(self):
        self.connected = False
        # self.send_timer = machine.Timer(-1)  # default is 200 ms
        # self.period=int(1000/self.freq)
        self.init()
        utime.sleep_ms(10)
        # empty read buffer
        self.uart.read()
        self.writeIt(
            self.setType(self.sensor_id)
        )  # set sensor_id to 35 (WeDo Ultrasonic) 61 (Spike color), 62 (Spike ultrasonic)
        self.writeIt(self.defineModes())  # tell how many modes
        **#self.writeIt(self.defineBaud(115200))**
        self.writeIt(self.defineVers(2, 2))
        num = len(self.modes) - 1
        for mode in reversed(self.modes):
            utime.sleep_ms(20)
            self.setupMode(mode, num)
            num -= 1

        # empty read buffer
        #self.uart.read()
        self.writeIt(b"\x04")  # ACK
        # Check for ACK reply
        #self.uart.read()
        #while r!=b'\x04':
        #    r=self.uart.read(1)
        #    utime.sleep_ms(1)
        self.connected = True
        utime.sleep_ms(100)
        #self.connected = self.waitFor(b"\x04")
        print("Successfully connected to hub" if self.connected else "Failed to connect to hub")
        self.last_nack = utime.ticks_ms()

        # Reset Serial to High Speed
        if self.connected:
            #self.write_tx_pin(0, 10)

            # Change baudrate
            #self.fast_uart()
            self.load_payload(b'\x00')

            # start callback  - MAKE SURE YOU RESTART THE CHIP EVERY TIME (CMD D) to kill previous callbacks running
            # self.send_timer.init(period=self.period, mode=machine.Timer.PERIODIC, callback= self.hubCallback)
        return
```

