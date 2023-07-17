from sen55 import Sen55
import time

sen55 = Sen55()
sen55.start()
timestamp = time.ticks_us()

while True:
    timestamp = time.ticks_us()
    pm1, pm25, pm4, pm10, hum, temp, voc, nox = sen55.readVals()
    net_cycle_time_us = time.ticks_diff(time.ticks_us(), timestamp)

    # print the values as JSON
    # format:
    # {
    #     "timestamp" : 8672981, // timestamp_us_since_boot, uint64_t,
    #     "netCycleTimeUs": 14, // netCycleTimeUs uint32_t,
    #     "errors": "0b00000000000000000000000000000001", // device_errors, 32 flags
    #     "device" : {
    #             "pm1" : 10.5, // float,
    #             "pm2.5" : 20.5, // float,
    #             "pm4" : 30.6, // float,
    #             "pm10" : 100.7, // float
    #             "voc" : 15.0, // float
    #             "nox" : 1.0, // float  
    #             "rh" : 45, // float
    #             "temp" : 23 // float
    #     } 
    # }

    print('{')
    print('"timestamp":', timestamp, ',')
    print('"netCycleTimeUs":', net_cycle_time_us, ',')
    print('"errors":', bin(sen55.errors), ',')
    print('"device": {')
    print('"pm1":', pm1, ',')
    print('"pm2.5":', pm25, ',')
    print('"pm4":', pm4, ',')
    print('"pm10":', pm10, ',')
    print('"voc":', voc, ',')
    print('"nox":', nox, ',')
    print('"rh":', hum, ',')
    print('"temp":', temp)
    print('}')
    print('}')
    print()
    time.sleep(1 - net_cycle_time_us / 1_000_000)

