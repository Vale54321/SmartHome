from clients.battery_modbus_client import BatteryModbusClient, REG
from clients.influx_writer import InfluxDBWriter
from dotenv import load_dotenv
import os
import time
import signal

running = True

def signal_handler(sig, frame):
    """Handles signals and initiates a graceful shutdown."""
    global running
    print(f"Caught signal {sig}, shutting down gracefully...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

load_dotenv()

# Modbus Client Setup
ip = os.getenv("E3DC_IP")
port = int(os.getenv("E3DC_PORT"))
modbus_client = BatteryModbusClient(ip, port)
modbus_client.log_device_info()
print()

# InfluxDB Client Setup
token = os.environ.get("INFLUXDB_TOKEN")
org = os.environ.get("INFLUXDB_ORG")
url = os.environ.get("INFLUXDB_HOST")
bucket = os.environ.get("INFLUXDB_BUCKET")
influx_writer = InfluxDBWriter(url=url, token=token, org=org, bucket=bucket)

# Polling Configuration
polling_interval_ms = os.getenv("POLLING_INTERVAL_MS", "1000")
polling_interval_s = int(polling_interval_ms) / 1000

print("------- InfluxDB & Polling Config -------")
print(f"URL:                  {url}")
print(f"Org:                  {org}")
print(f"Bucket:               {bucket}")
print(f"Polling Interval:     {polling_interval_s}s")
print("-----------------------------------------")
print()

def poll_and_write_metrics():
    """Polls all metrics from the Modbus device and writes them to InfluxDB."""
    # Power Metrics
    influx_writer.write_watts_metric("pv_power", modbus_client.read_metric(REG.PV_POWER))
    influx_writer.write_watts_metric("battery_power", modbus_client.read_metric(REG.BATTERY_POWER))
    influx_writer.write_watts_metric("house_consumption", modbus_client.read_metric(REG.HOUSE_CONSUMPTION))
    influx_writer.write_watts_metric("grid_power", modbus_client.read_metric(REG.GRID_POWER))
    influx_writer.write_watts_metric("additional_feed_in_power", modbus_client.read_metric(REG.ADDITIONAL_FEED_IN))
    influx_writer.write_watts_metric("wallbox_consumption", modbus_client.read_metric(REG.WALLBOX_CONSUMPTION))
    influx_writer.write_watts_metric("wallbox_solar_consumption", modbus_client.read_metric(REG.WALLBOX_SOLAR_CONSUMPTION))

    # Efficiency Metrics
    self_sufficiency, self_consumption = modbus_client.read_metric(REG.EFFICIENCY)
    influx_writer.write_percent_metric("self_sufficiency", self_sufficiency)
    influx_writer.write_percent_metric("self_consumption", self_consumption)

    # Battery SoC
    influx_writer.write_percent_metric("battery_soc", modbus_client.read_metric(REG.BATTERY_SOC))

    # Emergency Power & EMS
    influx_writer.write_int_metric("emergency_power_status", modbus_client.read_metric(REG.EMERGENCY_POWER_STATUS))
    influx_writer.write_int_metric("ems_remote_control", modbus_client.read_metric(REG.EMS_REMOTE_CONTROL))
    influx_writer.write_int_metric("ems_ctrl", modbus_client.read_metric(REG.EMS_CTRL))

    ems_status_bits = modbus_client.get_ems_status_bits()
    if ems_status_bits:
        for key, value in ems_status_bits.items():
            influx_writer.write_bool_metric(f"ems_{key}", value)

while running:
    poll_and_write_metrics()
    time.sleep(polling_interval_s)

print("Application stopped.")
