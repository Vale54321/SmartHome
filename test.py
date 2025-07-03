from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from dotenv import load_dotenv
import os

load_dotenv()

def read_modbus_register(client, register_number):
    """
    Reads a single Modbus holding register using its human-readable number.
    Calculates the required address offset automatically.
    """
    address = register_number - 1
    
    response = client.read_holding_registers(address=address, count=1, slave=1)
    
    if not response.isError():
        return response.registers[0]
    else:
        print(f"Fehler beim Lesen von Register {register_number}: {response}")
        return None
    
def read_modbus_string(client, start_register, num_registers):
    """
    Reads a string from a sequence of Modbus holding registers.
    """
    address = start_register - 1
    response = client.read_holding_registers(address=address, count=num_registers, slave=1)

    if not response.isError():
        # Convert registers to string using DATATYPE enum
        decoded = client.convert_from_registers(
            response.registers,
            data_type=client.DATATYPE.STRING,
        )
        return decoded.strip('\x00')
    else:
        print(f"Fehler beim Lesen des Strings ab Register {start_register}: {response}")
        return None

ip = os.getenv("E3DC_IP")
port = int(os.getenv("E3DC_PORT"))

client = ModbusTcpClient(ip, port=port)
client.connect()

magic_byte = read_modbus_register(client, 1)
if magic_byte is not None:
    print(f"Register 40001 (Magic Byte): {hex(magic_byte)}")

firmware_reg = read_modbus_register(client, 2)
if firmware_reg is not None:
    major_version = firmware_reg >> 8
    minor_version = firmware_reg & 0xFF
    print(f"Register 40002 (Firmware): {major_version}.{minor_version}")

reg_count = read_modbus_register(client, 3)
if reg_count is not None:
    print(f"Register 40003 (Register Count): {reg_count}")

manufacturer = read_modbus_string(client, 4, 16)
if manufacturer is not None:
    print(f"Register 40004-40019 (Manufacturer): {manufacturer}")

model_string = read_modbus_string(client, 20, 16)
if model_string is not None:
    print(f"Register 40020-40035 (Modell): {model_string}")

serial_num = read_modbus_string(client, 36, 16)
if serial_num is not None:
    print(f"Register 40036-40051 (Serial Number): {serial_num}")

firmware_version = read_modbus_string(client, 52, 16)
if firmware_version is not None:
    print(f"Register 40052-40068 (Serial Number): {firmware_version}")

response = client.read_holding_registers(address=72-1, count=2, slave=1)
if not response.isError():
    hausverbrauch = client.convert_from_registers(
        response.registers,
        data_type=client.DATATYPE.INT32,
        word_order='little'
    )
    hausverbrauch_kw = hausverbrauch / 1000
    print(f"Register 40072 (Hausverbrauchs-Leistung): {hausverbrauch} Watt ({hausverbrauch_kw:.2f} kW)")
else:
    print(f"Fehler beim Lesen von Register 40072: {response}")

response = client.read_holding_registers(address=74-1, count=2, slave=1)
if not response.isError():
    netzleistung = client.convert_from_registers(
        response.registers,
        data_type=client.DATATYPE.INT32,
        word_order='little'
    )
    print(f"Register 40074 (Netzleistung): {netzleistung} Watt")
else:
    print(f"Fehler beim Lesen von Register 40072: {response}")

efficency = read_modbus_register(client, 82)
if efficency is not None:
    autarkie = efficency >> 8
    eigenverbrauch = efficency & 0xFF
    print(f"Register 40082: Autarkie: {autarkie}%, Eigenverbrauch: {eigenverbrauch}%")

client.close()
