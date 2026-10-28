#!/usr/bin/env python3

from utils import sound
from utils.brick import TouchSensor, EV3ColorSensor, wait_ready_sensors, reset_brick
from time import sleep


values = []

print("Program start.\nWaiting for sensors to turn on...")

EMMERGENCY_STOP = TouchSensor(1)    # Emmergency Sptop Touch Sensor on Port S1
COLOR_SENSOR = EV3ColorSensor(2)    # Color Sensor on Port S2

wait_ready_sensors(True)    # True for verbose.
print("Done waiting.")

def collect_color_sensor_data():
    "Collect color sensor data."
    try:
        while not EMMERGENCY_STOP.is_pressed():
            pass
        
        sleep(0.5)
        
        print("Collecting color sensor data")

        while not EMMERGENCY_STOP.is_pressed():
            value = COLOR_SENSOR.get_rgb()
            if value:
                total = sum(value)
                normalized = tuple(v / total for v in value)
                values.append(normalized)
                print(normalized)

            sleep(0.5) 
            
    except BaseException as e:
        print(e)

    finally:
        print("Emmergency stop pressed. Stopping all actions")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    collect_color_sensor_data()
