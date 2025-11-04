from machine import Pin, I2C
import time


class _reg:
    product_name = 0xD014
    serial_number = 0xD033
    read_values = 0x03C4
    start_measurement = 0x0021
    stop_measurement = 0x0104
    read_device_status = 0xD206

    @staticmethod
    def to_bytes(val: int):
        return val.to_bytes(2, "big")


class Sen55:
    # 32 bit flags for errors, not used yet
    errors = 0
    _address = 0x69

    def __init__(self) -> None:
        self.i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=400_000)

    def start(self):
        self.__write_i2c(_reg.to_bytes(_reg.start_measurement))
        time.sleep(0.1)

    def __write_i2c(self, data: bytes) -> None:
        try:
            self.i2c.writeto(self._address, data)
        except OSError:
            self.errors |= 1
        except Exception:
            self.errors |= 2

    def __read_i2c(self, num_bytes: int) -> bytes | None:
        try:
            _data = self.i2c.readfrom(self._address, num_bytes)
        except OSError:
            self.errors |= 4
            return None
        except Exception:
            self.errors |= 8
            return None
        return _data

    def __read_reg(self, reg: bytes | int, num_bytes: int) -> bytes | None:
        if isinstance(reg, int):
            reg = _reg.to_bytes(reg)
        self.__write_i2c(reg)

        time.sleep(0.05)

        return self.__read_i2c(num_bytes)

    def readVals(self) -> list[float]:
        # read 24 bytes from the sensor
        raw_data = self.__read_reg(_reg.read_values, 24)

        if raw_data is None:  # error
            return [0, 0, 0, 0, 0, 0, 0, 0]

        # remove every 3rd byte (checksum)
        data = bytes([raw_data[i] for i in range(len(raw_data)) if i % 3 != 2])
        # convert to 8 uint16_t:
        data2 = [data[i : i + 2] for i in range(0, len(data), 2)]
        data2 = [int.from_bytes(d, "big") for d in data2]
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
