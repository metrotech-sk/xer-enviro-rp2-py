from machine import Pin, SoftI2C
import time

class _reg:
    product_name = 0xD014
    serial_number = 0xD033 
    read_values = 0x03c4
    start_measurement = 0x0021
    stop_measurement = 0x0104
    read_device_status = 0xd206

    @staticmethod
    def to_bytes(val: int):
        return val.to_bytes(2, 'big')


class Sen55:
    # 32 bit flags for errors, not used yet
    errors = 0

    def __init__(self) -> None:
        self.i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100_000)

    def start(self):
        self.i2c.writeto(0x69, _reg.to_bytes(_reg.start_measurement))
        time.sleep(0.1)

    def readVals(self):
        self.i2c.writeto(0x69, _reg.to_bytes(_reg.read_values))
        # wait for 50ms for the sensor to collect data
        time.sleep(0.05)
        # read 24 bytes from the sensor
        raw_data = self.i2c.readfrom(0x69, 24)
        # remove every 3rd byte (checksum)
        data = bytes([raw_data[i] for i in range(len(raw_data)) if i % 3 != 2])
        # convert to 8 uint16_t:
        data2 = [data[i:i+2] for i in range(0, len(data), 2)]
        data2 = [int.from_bytes(d, 'big') for d in data2]
        # data2 contains data acc. to this table:
        # Byte # Datatype Scale factor Description
        # 0..1 big-endian, uint16 10 Mass Concentration PM1.0 [µg/m³]
        # 2 Checksum for bytes 0, 1
        # 3..4 big-endian, uint16 10 Mass Concentration PM2.5 [µg/m³]
        # 5 Checksum for bytes 3, 4
        # 6..7 big-endian, uint16 10 Mass Concentration PM4.0 [µg/m³]
        # 8 Checksum for bytes 6, 7
        # 9..10 big-endian, uint16 10 Mass Concentration PM10 [µg/m³]
        # 11 Checksum for bytes 9, 10
        # 12..13 big-endian, int16 100 Compensated Ambient Humidity [%RH]
        # 14 Checksum for bytes 12, 13
        # 15..16 big-endian, int16 200 Compensated Ambient Temperature [°C]
        # 17 Checksum for bytes 15, 16
        # 18..19 big-endian, int16 10 VOC Index
        # 20 Checksum for bytes 18, 19
        # 21..22 big-endian, int16 10 NOx Index
        # 23 Checksum for bytes 21, 22

        # downscale to the actual values
        # scale factors see table above/data sheet
        scale = [10, 10, 10, 10, 100, 200, 10, 10]
        scaled = [data2[i] / scale[i] for i in range(len(data2))]
        return scaled
