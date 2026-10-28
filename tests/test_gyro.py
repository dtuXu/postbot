#!/usr/bin/env python3

from utils import sound
from utils.brick import TouchSensor, EV3GyroSensor, wait_ready_sensors, reset_brick
from time import sleep

print("Program start.\nWaiting for sensors to turn on...")

EMMERGENCY_STOP = TouchSensor(1)    # Emmergency Sptop Touch Sensor on Port S1
GYRO = EV3GyroSensor(2)  # Gyro Sensor on Port S2
 
wait_ready_sensors(True)    # True for verbose.
print("Done waiting.")

def log_gyro():
    "Logs the gyro sensor values until the emergency stop is pressed."
    try:
        print("Starting to log gyro values")
        while not EMMERGENCY_STOP.is_pressed():
            angle = GYRO.get_value()  # Angle recorded by Gyro sensor
            print(f"Gyro Angle: {angle} degrees")
            sleep(0.5)  # Log every 0.5 seconds
            
    except BaseException as e:
        print(e)

    finally:
        print("Emmergency stop pressed. Stopping all actions")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()

if __name__ == "__main__":
    log_gyro()