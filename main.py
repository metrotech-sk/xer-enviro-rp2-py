import time

import machine

from src.sen55 import Sen55

sen55 = Sen55()
backoff_delay = 1
max_backoff = 60

while True:
    sen55.start()
    if sen55.errors == 0:
        break

    print(f"Error while starting sensor: {sen55.errors}, retrying in {backoff_delay}s")
    time.sleep(backoff_delay)
    backoff_delay = min(backoff_delay * 2, max_backoff)

if backoff_delay > 1:
    print("Sensor started successfully after retries")


def enclose(_f):
    """
    decorator function to enclose text returned by _f in curly
    braces and add tab to each line
    """

    def wrapper(*args, **kwargs):
        return "{\n" + "\n".join(["  " + line for line in _f(*args, **kwargs).split("\n")]) + "\n}"

    return wrapper


@enclose
def values_to_json(vals: list) -> str:
    # convert list of values to json
    return ",\n".join(
        [f'"{k}": {v}' for k, v in zip(["pm1", "pm2.5", "pm4", "pm10", "rh", "temp", "voc", "nox"], vals)]
    )


@enclose
def format_output(vals: list, timestamp: int, net_cycle_time_us: int, errors: int) -> str:
    text = f'"timestamp": {timestamp},\n'
    text += f'"netCycleTimeUs": {net_cycle_time_us},\n'
    text += f'"errors": {bin(errors)},\n'
    text += '"device": ' + values_to_json(vals)
    return text


num_err = 0
while True:
    timestamp = time.ticks_us()
    measurements = sen55.readVals()
    if not any(measurements):
        # no measurements available, restart is needed
        num_err += 1
        if num_err > 3:
            print("Too many errors, restarting")
            time.sleep(1)
            machine.soft_reset()

    pm1, pm25, pm4, pm10, hum, temp, voc, nox = measurements
    net_cycle_time_us = time.ticks_diff(time.ticks_us(), timestamp)

    print(format_output(measurements, timestamp, net_cycle_time_us, sen55.errors))

    time.sleep(1 - net_cycle_time_us / 1_000_000)
