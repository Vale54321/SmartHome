from pymodbus.client import ModbusTcpClient
from enum import IntEnum

class REG(IntEnum):
    # Static Device Information Registers
    MAGIC_BYTE                  =  1
    FIRMWARE                    =  2
    REGISTER_COUNT              =  3
    MANUFACTURER                =  4
    MODEL                       = 20
    SERIAL_NUMBER               = 36
    FIRMWARE_VERSION            = 52

    # Dynamic Metrics Registers
    PV_POWER                    = 68
    BATTERY_POWER               = 70
    HOUSE_CONSUMPTION           = 72
    GRID_POWER                  = 74
    ADDITIONAL_FEED_IN          = 76
    WALLBOX_CONSUMPTION         = 78
    WALLBOX_SOLAR_CONSUMPTION   = 80
    EFFICIENCY                  = 82
    BATTERY_SOC                 = 83

    # Emergency Power & EMS
    EMERGENCY_POWER_STATUS      = 40084
    EMS_STATUS                  = 40085
    EMS_REMOTE_CONTROL          = 40086
    EMS_CTRL                    = 40087

class BatteryModbusClient:
    def __init__(self, ip, port, slave=1):
        self.client = ModbusTcpClient(ip, port=port)
        self.client.connect()
        self.slave = slave

    def log_device_info(self):
        """
        Reads and prints static device information registers in a formatted way.
        """
        print("-------------- Device Info --------------")
        magic_byte = self.read_metric(REG.MAGIC_BYTE)
        if magic_byte is not None:
            print(f"Magic Byte:           {hex(magic_byte)}")

        major_version, minor_version = self.read_metric(REG.FIRMWARE)
        if major_version is not None:
            print(f"Firmware:             {major_version}.{minor_version}")

        reg_count = self.read_metric(REG.REGISTER_COUNT)
        if reg_count is not None:
            print(f"Register Count:       {reg_count}")

        manufacturer = self.read_metric(REG.MANUFACTURER)
        if manufacturer is not None:
            print(f"Manufacturer:         {manufacturer}")

        model_string = self.read_metric(REG.MODEL)
        if model_string is not None:
            print(f"Model:                {model_string}")

        serial_num = self.read_metric(REG.SERIAL_NUMBER)
        if serial_num is not None:
            print(f"Serial Number:        {serial_num}")

        firmware_version = self.read_metric(REG.FIRMWARE_VERSION)
        if firmware_version is not None:
            print(f"Firmware Version:     {firmware_version}")
        print("-----------------------------------------")      

    def get_ems_status_bits(self):
        """
        Reads the EMS status register and returns a dictionary of booleans for each bit.
        """
        status = self.read_metric(REG.EMS_STATUS)
        if status is None:
            return None

        return {
            "battery_charging_locked": bool((status >> 0) & 1),
            "battery_discharging_locked": bool((status >> 1) & 1),
            "emergency_power_possible": bool((status >> 2) & 1),
            "weather_based_charging": bool((status >> 3) & 1),
            "curtailment_active": bool((status >> 4) & 1),
            "charging_lock_active": bool((status >> 5) & 1),
            "discharging_lock_active": bool((status >> 6) & 1),
        }

    def read_metric(self, metric: REG):
        """
        Reads a metric from the modbus device, handling different data types.
        """
        # String metrics
        if metric in [REG.MANUFACTURER, REG.MODEL, REG.SERIAL_NUMBER, REG.FIRMWARE_VERSION]:
            return self._read_string(metric, 16)
        # int32 metrics
        elif metric in [REG.PV_POWER, REG.BATTERY_POWER, REG.HOUSE_CONSUMPTION, REG.GRID_POWER, REG.ADDITIONAL_FEED_IN, REG.WALLBOX_CONSUMPTION, REG.WALLBOX_SOLAR_CONSUMPTION]:
            return self._read_int32(metric)
        # uint8 tuple metrics
        elif metric in [REG.FIRMWARE, REG.EFFICIENCY]:
            return self._read_uint8_tuple(metric)
        # single register metrics (uint16)
        elif metric in [REG.MAGIC_BYTE, REG.REGISTER_COUNT, REG.BATTERY_SOC, REG.EMERGENCY_POWER_STATUS, REG.EMS_STATUS, REG.EMS_REMOTE_CONTROL, REG.EMS_CTRL]:
            return self._read_register(metric)
        else:
            print(f"Unknown metric: {metric}")
            return None

    def _read_register(self, register_number):
        address = register_number - 1
        response = self.client.read_holding_registers(address=address, count=1, slave=self.slave)
        if not response.isError():
            return response.registers[0]
        else:
            print(f"Error reading register {register_number}: {response}")
            return None

    def _read_uint8_tuple(self, register_number):
        """
        Reads a single register and splits it into two 8-bit unsigned integers (high byte, low byte).
        """
        val = self._read_register(register_number)
        if val is not None:
            high_byte = val >> 8
            low_byte = val & 0xFF
            return high_byte, low_byte
        return None, None

    def _read_string(self, start_register, num_registers):
        address = start_register - 1
        response = self.client.read_holding_registers(address=address, count=num_registers, slave=self.slave)
        if not response.isError():
            decoded = self.client.convert_from_registers(
                response.registers,
                data_type=self.client.DATATYPE.STRING
            )
            return decoded.strip('\x00')
        else:
            print(f"Error reading string from register {start_register}: {response}")
            return None

    def _read_int32(self, start_register):
        address = start_register - 1
        response = self.client.read_holding_registers(address=address, count=2, slave=self.slave)
        if not response.isError():
            return self.client.convert_from_registers(
                response.registers,
                data_type=self.client.DATATYPE.INT32,
                word_order='little'
            )
        else:
            print(f"Error reading 32-bit integer from register {start_register}: {response}")
            return None

    def __del__(self):
        self.client.close()