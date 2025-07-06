from battery_modbus_client import BatteryModbusClient
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

ip = os.getenv("E3DC_IP")
port = int(os.getenv("E3DC_PORT"))
modbus_client = BatteryModbusClient(ip, port)

magic_byte = modbus_client.read_register(1)
if magic_byte is not None:
    print(f"Register 40001 (Magic Byte): {hex(magic_byte)}")

firmware_reg = modbus_client.read_register(2)
if firmware_reg is not None:
    major_version = firmware_reg >> 8
    minor_version = firmware_reg & 0xFF
    print(f"Register 40002 (Firmware): {major_version}.{minor_version}")

reg_count = modbus_client.read_register(3)
if reg_count is not None:
    print(f"Register 40003 (Register Count): {reg_count}")

manufacturer = modbus_client.read_string(4, 16)
if manufacturer is not None:
    print(f"Register 40004-40019 (Manufacturer): {manufacturer}")

model_string = modbus_client.read_string(20, 16)
if model_string is not None:
    print(f"Register 40020-40035 (Modell): {model_string}")

serial_num = modbus_client.read_string(36, 16)
if serial_num is not None:
    print(f"Register 40036-40051 (Serial Number): {serial_num}")

firmware_version = modbus_client.read_string(52, 16)
if firmware_version is not None:
    print(f"Register 40052-40068 (Serial Number): {firmware_version}")


token = os.environ.get("INFLUXDB_TOKEN")
org = os.environ.get("INFLUXDB_ORG")
url = os.environ.get("INFLUXDB_HOST")

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket=os.environ.get("INFLUXDB_BUCKET")

write_api = write_client.write_api(write_options=SYNCHRONOUS)
   
def write_power_metric(register, metric_name):
    value = modbus_client.read_int32(register)
    point = (
        Point("battery_modbus_metrics")
        .tag("metric", metric_name)
        .field("value_watts", value)
    )
    write_api.write(bucket=bucket, org=org, record=point)

def write_efficiency(register):
    """
    Reads register, splits into autarkie% and eigenverbrauch%, and writes both as fields in one point.
    """
    val = modbus_client.read_register(register)
    if val is None:
        return
    autarkie = val >> 8
    eigenverbrauch = val & 0xFF
    point = (
        Point("battery_modbus_metrics")
        .tag("metric", "self_consumption")
        .field("value_percent", eigenverbrauch)
    )
    point = (
        Point("battery_modbus_metrics")
        .tag("metric", "self_sufficiency")
        .field("value_percent", autarkie)
    )
    write_api.write(bucket=bucket, org=org, record=point)

def write_battery_soc(register):
    """
    Reads battery state-of-charge percentage and writes it as a field.
    """
    soc = modbus_client.read_register(register)
    if soc is None:
        return
    point = (
        Point("battery_modbus_metrics")
        .tag("metric", "battery_soc")
        .field("value_percent", soc)
    )
    write_api.write(bucket=bucket, org=org, record=point)

while True:
  write_power_metric(68, "pv_power")
  write_power_metric(70, "battery_power")
  write_power_metric(72, "house_consumption")
  write_power_metric(74, "grid_power")
  write_power_metric(76, "additional_feed_in_power")
  write_power_metric(78, "wallbox_consumption")
  write_power_metric(80, "wallbox_solar_consumption")
  write_efficiency(82)
  write_battery_soc(83)
  print(f"Wrote data at {datetime.now().isoformat()}")

  time.sleep(1)

modbus_client.close()
