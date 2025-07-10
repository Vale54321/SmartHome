import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBWriter:
    def __init__(self, url, token, org, bucket):
        self.bucket = bucket
        self.org = org
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_watts_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value_watts", value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_percent_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value_percent", value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_volts_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value_volts", value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_ampere_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value_ampere", value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_int_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value", value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_bool_metric(self, metric_name, value):
        if value is None:
            return
        point = (
            Point("battery_modbus_metrics")
            .tag("metric", metric_name)
            .field("value", int(value))
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def __del__(self):
        self.client.close()
