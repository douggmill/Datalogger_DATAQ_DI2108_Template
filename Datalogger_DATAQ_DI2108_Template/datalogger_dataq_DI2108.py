import serial
import serial.tools.list_ports
import time


class DataQDevice:
    def __init__(self, slist, analog_ranges):
        self.ser = serial.Serial()
        self.slist = slist
        self.analog_ranges = analog_ranges
        self.range_table = []
        self.acquiring = False

    # -------------------------
    # Device Discovery
    # -------------------------
    def discover(self):
        ports = list(serial.tools.list_ports.comports())

        for p in ports:
            if "VID:PID=0683" in p.hwid:
                self.ser.port = p.device
                self.ser.baudrate = 115200
                self.ser.timeout = 0
                self.ser.open()
                return True

        return False

    # -------------------------
    # Send Command
    # -------------------------
    def send_cmd(self, cmd):
        self.ser.write((cmd + '\r').encode())
        time.sleep(0.05)

    # -------------------------
    # Configure Scan List
    # -------------------------
    def config_scan_list(self):
        self.range_table = []

        for i, item in enumerate(self.slist):
            self.send_cmd(f"slist {i} {item}")

            function = item & 0xF

            if function < 8:
                self.range_table.append(self.analog_ranges[item >> 8])
            else:
                self.range_table.append(0)

    # -------------------------
    # Initialize Device
    # -------------------------
    def setup(self):
        if not self.discover():
            raise RuntimeError("No DATAQ device found")

        self.send_cmd("stop")
        self.send_cmd("encode 0")
        self.send_cmd("ps 0")

        self.config_scan_list()

        # 10 Hz sample rate
        self.send_cmd("dec 512")
        self.send_cmd("srate 11718")

    # -------------------------
    # Start / Stop
    # -------------------------
    def start(self):
        self.ser.reset_input_buffer()
        time.sleep(0.2)
        self.send_cmd("start")
        self.acquiring = True

    def stop(self):
        self.send_cmd("stop")
        self.acquiring = False
        self.ser.flushInput()

    # -------------------------
    # Read One Frame
    # -------------------------
    # def read_latest(self):
    #     # Wait until at least one sample is available
    #     while self.ser.inWaiting() < 2:
    #         pass
    #
    #     # Flush everything except the newest 2 bytes
    #     while self.ser.inWaiting() > 2:
    #         self.ser.read(self.ser.inWaiting() - 2)
    #
    #     raw = self.ser.read(2)
    #
    #     value = int.from_bytes(raw, byteorder='little', signed=True)
    #     voltage = self.range_table[0] * value / 32768
    #
    #     return voltage

    def read_latest(self):
        frame_size = 2 * len(self.slist)  # 16 bytes

        # Wait for full frame
        while self.ser.inWaiting() < frame_size:
            pass

        # Drop old data, keep newest full frame
        while self.ser.inWaiting() > frame_size:
            self.ser.read(self.ser.inWaiting() - frame_size)

        data = self.ser.read(frame_size)

        values = []

        for i in range(len(self.slist)):
            raw = data[i * 2:(i * 2) + 2]

            value = int.from_bytes(raw, byteorder='little', signed=True)
            voltage = self.range_table[i] * value / 32768

            values.append(voltage)

        return values

    # -------------------------
    # Cleanup
    # -------------------------
    def close(self):
        self.stop()
        self.ser.close()

slist = [0x0000,0x0001,0x0002,0x0003,0x0004,0x0005,0x0006,0x0007]
analog_ranges = [10]
daq = DataQDevice(slist, analog_ranges)
daq.setup()
daq.start()

def readDAC():
        ch = daq.read_latest()
        # print(
        #     f"{ch[0]:6.3f}, {ch[1]:6.3f}, {ch[2]:6.3f}, {ch[3]:6.3f}, "
        #     f"{ch[4]:6.3f}, {ch[5]:6.3f}, {ch[6]:6.3f}, {ch[7]:6.3f}"
        # )
        return ch



def ch_conversion():
    ch0 = readDAC()[0]
    ch1 = readDAC()[1]
    ch2 = readDAC()[2]

    if ch0 >= 0.5 and ch0 <= 2.9:
        ch0_current_mA = (ch0 / 150) * 1000
        ch0_Vac = (ch0 - 0.5) * 300 / (2.9 - 0.5)
        print(f"{ch0_Vac:6.1f}V, {ch0:6.3f}V, {ch0_current_mA:6.2f}mA")
    elif ch0 < 0.5:
        print(f"CH0 not connected")
    else:
        print(f"CH0 Over Voltage")


    if ch1 >= 0.5 and ch1 <= 2.9:
        ch1_current_mA = (ch1 / 150) * 1000
        ch1_Vac = (ch1 - 0.5) * 300 / (2.9 - 0.5)
        print(f"{ch1_Vac:6.1f}V, {ch1:6.3f}V, {ch1_current_mA:6.2f}mA")
    elif ch1 < 0.5:
        print(f"CH1 not connected")
    else:
        print(f"CH1 Over Voltage")


    if ch2 >= 0.5 and ch2 <= 2.9:
        ch2_current_mA = (ch2 / 150) * 1000
        ch2_Vac = (ch2 - 0.5) * 300 / (2.9 - 0.5)
        print(f"{ch2_Vac:6.1f}V, {ch2:6.3f}V, {ch2_current_mA:6.2f}mA")
    elif ch2 < 0.5:
        print(f"CH2 not connected")
    else:
        print(f"CH2 Over Voltage")


try:
    while True:
        time.sleep(1)
        ch_conversion()
except KeyboardInterrupt:
    pass

finally:
    daq.close()