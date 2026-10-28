#!/usr/bin/env python3

from utils import sound
from utils.brick import TouchSensor, EV3GyroSensor, EV3UltrasonicSensor, Motor, wait_ready_sensors, reset_brick
from time import sleep

print("Program start.\nWaiting for sensors to turn on...")

EMMERGENCY_STOP = TouchSensor(1)    # Emmergency Sptop Touch Sensor on Port S4
US_SENSOR = EV3UltrasonicSensor(3)  # Ultrasonic Sensor on Port S3
DRIVE_MOTOR_L = Motor("C")          # Drive motor on Port C
DRIVE_MOTOR_R = Motor("B")          # Drive motor on Port D

CORRECTION_FACTOR = 40
 
wait_ready_sensors(True)    # True for verbose.
print("Done waiting.")

def drive():
    "Drive straight until the emergency stop is pressed."
    try:
        while not EMMERGENCY_STOP.is_pressed():
            pass
        sleep(0.5)
        print("Starting driving")
        dist = 6

        while not EMMERGENCY_STOP.is_pressed():
            motorSpeedL = 400
            motorSpeedR = 400

            dist_err = US_SENSOR.get_value() - dist  # Calculate distance error

            motorSpeedL = motorSpeedL + (dist_err * CORRECTION_FACTOR)
            motorSpeedR = motorSpeedR - (dist_err * CORRECTION_FACTOR)

            DRIVE_MOTOR_L.set_dps(motorSpeedL)
            DRIVE_MOTOR_R.set_dps(motorSpeedR)
            
            sleep(0.1)
            
    except BaseException as e:
        print(e)

    finally:
        print("Emmergency stop pressed. Stopping all actions")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()

if __name__ == "__main__":
    drive()