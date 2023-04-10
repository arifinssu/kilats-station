import minimalmodbus
from threading import Thread
from time import sleep

class Modbus():
    def __init__(self, address, baud, port, timeout=1, close_port=True):
        # modbus init
        self.modbus = minimalmodbus.Instrument(port, address)
        print(address, baud, port)
        self.modbus.serial.baudrate = baud
        self.modbus.serial.timeout = timeout
        self.modbus.close_port_after_each_call = close_port

        # modbus mode
        self.holding_register = False
        self.holding_register_data = None
        self.holding_register_length = None
        self.holding_register_write = False
        self.holding_register_write_value = None
        self.coil_status = False
        self.coil_status_data = None
        self.coil_status_length = None
        self.input_status = False
        self.input_status_data = None
        self.input_status_length = None
        self.input_register = False
        self.input_register_data = None
        self.input_register_length = None

    def set_timeout(self, timeout):
        self.modbus.serial.timeout = timeout

    def set_mode(self, mode, length):
        ##coil_status, input_status, holding_register, input_register
        if mode == 'HREG':
            self.holding_register = True
            self.holding_register_length = length
            return True
        elif mode == 'coil_status':
            self.coil_status = True
            self.coil_status_length = length
            return True
        elif mode == 'input_status':
            self.input_status = True
            self.input_status_length = length
            return True
        elif mode == 'input_register':
            self.input_register = True
            self.input_register_length = length
            return True
        else: return False

    def poll(self):
        while True:
            if self.holding_register:
                self.holding_register_data = self.modbus.read_registers(0, self.holding_register_length)
                sleep(0.005)

            if self.holding_register_write:
                self.modbus.write_register(self.holding_register_write_address, self.holding_register_write_value)
                sleep(0.005)
                self.holding_register_write = False

    def get_data(self, mode):
        if mode == 'HREG': return self.holding_register_data
        else: return False

    def set_data(self, mode, address, value):
        if mode == 'HREG':
            if not self.holding_register_write:
                self.holding_register_write = True
                self.holding_register_write_address = address
                self.holding_register_write_value = value
                while self.holding_register_write: continue
                return True
            else: return False

    def start(self):
        Thread(target=self.poll, args=(), daemon=True).start()
