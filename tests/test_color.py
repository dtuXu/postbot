#!/usr/bin/env python3

from utils import sound
from utils.brick import TouchSensor, EV3ColorSensor, wait_ready_sensors, reset_brick
from time import sleep

COLORS = {
    "black": [0.3599624849747198,0.5059897222870935,0.13404779273818676],
    "white": [0.3616314073589884,0.46483559839385785,0.17353299424715346],
    "red": [0.8114720340669934,0.1442043953203483,0.04432357061265838],
    "green": [0.3360647896971045,0.6139654890273318,0.04996972127556407],
    "blue": [0.28526739489023833,0.4908453704122987,0.22388723469746255],
    "yellow": [0.48543819401739147,0.48051618683817254,0.034045619144436094],
    "orange": [0.6223831781731136,0.3432909998585928,0.03432582196829313]
}

print("Program start.\nWaiting for sensors to turn on...")

EMMERGENCY_STOP = TouchSensor(1)    # Emmergency Sptop Touch Sensor on Port S1
COLOR_SENSOR = EV3ColorSensor(2)    # Color Sensor on Port S2

wait_ready_sensors(True)    # True for verbose.
print("Done waiting.")

def collect_color_sensor_data():
    "Test color detection from color sensor data."
    try:
        print("Collecting color sensor data")

        while True:
            if EMMERGENCY_STOP.is_pressed():
                value = COLOR_SENSOR.get_rgb()
                if (value and value[0] and value[1] and value[2]):
                    total = sum(value)
                    normalized = tuple(v / total for v in value)
                    print(f"Normalized RGB: {normalized}")

                    closest = [None, float('inf')]  # [color_name, distance]

                    for color_name, color_value in COLORS.items():
                        distance = sum((normalized[i] - color_value[i]) ** 2 for i in range(3))
                        if distance < closest[1]:
                            closest[1] = distance
                            closest[0] = color_name

                    print(f"Detected color: {closest[0]} with RGB {normalized}")
            sleep(0.1)
            
    except BaseException as e:
        print(e)

    finally:
        print("Emmergency stop pressed. Stopping all actions")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    collect_color_sensor_data()
