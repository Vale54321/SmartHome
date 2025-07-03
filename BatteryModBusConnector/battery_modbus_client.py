from pymodbus.client import ModbusTcpClient

class BatteryModbusClient:
    def __init__(self, ip, port, slave=1):
        self.client = ModbusTcpClient(ip, port=port)
        self.client.connect()
        self.slave = slave

    def close(self):
        self.client.close()

    def read_register(self, register_number):
        address = register_number - 1
        response = self.client.read_holding_registers(address=address, count=1, slave=self.slave)
        if not response.isError():
            return response.registers[0]
        else:
            print(f"Fehler beim Lesen von Register {register_number}: {response}")
            return None

    def read_string(self, start_register, num_registers):
        address = start_register - 1
        response = self.client.read_holding_registers(address=address, count=num_registers, slave=self.slave)
        if not response.isError():
            decoded = self.client.convert_from_registers(
                response.registers,
                data_type=self.client.DATATYPE.STRING
            )
            return decoded.strip('\x00')
        else:
            print(f"Fehler beim Lesen des Strings ab Register {start_register}: {response}")
            return None

    def read_int32(self, start_register):
        address = start_register - 1
        response = self.client.read_holding_registers(address=address, count=2, slave=self.slave)
        if not response.isError():
            return self.client.convert_from_registers(
                response.registers,
                data_type=self.client.DATATYPE.INT32,
                word_order='little'
            )
        else:
            print(f"Fehler beim Lesen eines 32-Bit Integers ab Register {start_register}: {response}")
            return None