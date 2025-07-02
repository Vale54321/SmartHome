from pymodbus.client import ModbusTcpClient
from dotenv import load_dotenv
import os

load_dotenv()

ip = os.getenv("E3DC_IP")
port = int(os.getenv("E3DC_PORT"))

client = ModbusTcpClient(ip, port=port)
client.connect()

response = client.read_holding_registers(address=70, count=1, slave=1)

if not response.isError():
    soc = response.registers[0]
    print("Battery SoC:", soc, "%")
else:
    print("Fehler beim Lesen der Register:", response)

client.close()
