#!/usr/bin/env python3

from utils import sound
from utils.brick import TouchSensor, EV3ColorSensor, EV3UltrasonicSensor, EV3GyroSensor, Motor, wait_ready_sensors, reset_brick
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

EMMERGENCY_STOP = TouchSensor(1)        # Emmergency Sptop Touch Sensor on Port S1
COLOR_SENSOR = EV3ColorSensor(2)        # Color Sensor on Port S2
US_SENSOR = EV3UltrasonicSensor(3)      # Ultrasonic Sensor on Port S3
GYRO_SENSOR = EV3GyroSensor(4, "abs")   # Gyro Sensor on Port S4
COLOR_MOTOR = Motor("A")                # Color Sensor motor on Port A
DRIVE_MOTOR_R = Motor("B")              # Right drive motor on Port B
DRIVE_MOTOR_L = Motor("C")              # Left drive motor on Port C
DROP_MOTOR = Motor("D")                 # Cube dropping motor on Port D

SOUND_DURATION = 0.2
SOUND_VOLUME = 100

DELIVERY_SOUND = [sound.Sound(duration=SOUND_DURATION, pitch="A4", volume=SOUND_VOLUME),
                  sound.Sound(duration=SOUND_DURATION, pitch="B4", volume=SOUND_VOLUME),
                  sound.Sound(duration=SOUND_DURATION, pitch="D5", volume=SOUND_VOLUME)]

COMPLETE_SOUND = [sound.Sound(duration=SOUND_DURATION, pitch="G4", volume=SOUND_VOLUME),
                    sound.Sound(duration=SOUND_DURATION, pitch="A4", volume=SOUND_VOLUME),
                    sound.Sound(duration=SOUND_DURATION, pitch="C5", volume=SOUND_VOLUME)]

wait_ready_sensors(True)    # True for verbose.
print("Done waiting.")

def play_sound(sound):
    "Play a sound on the speaker."
    if sound == 0:
        for note in DELIVERY_SOUND:
            note.play()
            note.wait_done()
    elif sound == 1:
        for note in COMPLETE_SOUND:
            note.play()
            note.wait_done()


def detect_color(value):
    """ Detect color from RGB value. """
    total = sum(value)
    normalized = tuple(v / total for v in value)

    closest = [None, float('inf')]  # [color_name, distance]

    for color_name, color_value in COLORS.items():
        distance = sum((normalized[i] - color_value[i]) ** 2 for i in range(3))
        if distance < closest[1]:
            closest[1] = distance
            closest[0] = color_name
    
    return closest[0]


def office_movement(DRIVE_SPEED, office, deliveries):
    "Manage movement into offices"
    COLOR_MOTOR.reset_encoder()
    COLOR_MOTOR.set_limits(power=20)
    ARM_MOVEMENT = 50

    office_dist = {1:33,2:33,3:33,4:81}
    
    angle_offset = GYRO_SENSOR.get_abs_measure()

    red_detected, delivered = False, False
    count = 0

    # Red sticker detection
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:  
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)
        
        # Get angle from Gyro Sensor
        angle = GYRO_SENSOR.get_abs_measure() - angle_offset
        
        if angle in range(-16, 30):
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*-0.6)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*0.6)
        
        else:
            # Move color sensor arm
            if not COLOR_MOTOR.is_moving():
                COLOR_MOTOR.set_position_relative(ARM_MOVEMENT)
                ARM_MOVEMENT *= -1
            
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*-0.12)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*0.12)
            
            if count >= 15:
                break

            count += 1
            
            # Red sticker detected
            if color == "red":
                red_detected = True
        
        sleep(0.1)
    
    # Reset arm position
    COLOR_MOTOR.set_position_relative(60)
    sleep(1)
    COLOR_MOTOR.reset_encoder()
        
    # Leave Red sticker
    while not EMMERGENCY_STOP.is_pressed():
        # Get angle from Gyro Sensor
        angle = GYRO_SENSOR.get_abs_measure() - angle_offset
        
        DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*0.6)
        DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*-0.6)

        if angle in range(-4, 4):
            DRIVE_MOTOR_L.set_dps(0)
            DRIVE_MOTOR_R.set_dps(0)
            break
    
    print("March and turn to prepare for office entry")
    # Prepare Green sticker detection
    count = 0
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        if count < 15:
            # Get distance from Ultrasonic Sensor
            distance = US_SENSOR.get_value()
            dist_err = distance - 6  # Calculate distance error
            left_drive_speed = DRIVE_SPEED + (dist_err * 20)
            right_drive_speed = DRIVE_SPEED - (dist_err * 20)
            DRIVE_MOTOR_L.set_dps(left_drive_speed)
            DRIVE_MOTOR_R.set_dps(right_drive_speed)
        else:
            # Get angle from Gyro Sensor
            angle = GYRO_SENSOR.get_abs_measure() - angle_offset
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*-0.8)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*0.8)

            if angle in range(-100, -80):
                break
        
        count += 1
        sleep(0.1)
    
    print("Go back a bit to start at office entrance")
    count = 0
    # Go back a bit
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)
        
        DRIVE_MOTOR_L.set_dps(-DRIVE_SPEED)
        DRIVE_MOTOR_R.set_dps(-DRIVE_SPEED)

        if color == "orange":
            DRIVE_MOTOR_L.set_dps(0)
            DRIVE_MOTOR_R.set_dps(0)
            break
        
        sleep(0.1)
    
    print("Bring back robot arm")
    # Prepare arm position
    ARM_MOVEMENT = -160
    count = 0
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        if count == 0:
            COLOR_MOTOR.set_position_relative(ARM_MOVEMENT)
            ARM_MOVEMENT *= -1
            
        if count >= 25:
            break
        
        count += 1
        sleep(0.1)

    print("Start to detect green sticker")
    # Green sticker detection
    DROP_MOTOR.set_limits(power=20)
    green_detected = False
    count = 0
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)

        # Get distance from Ultrasonic Sensor
        distance = US_SENSOR.get_value()

        if not green_detected:
            # Drive straight
            dist_err = distance - office_dist[office]  # Calculate distance error
            left_drive_speed = DRIVE_SPEED*0.2 + (dist_err * 35)
            right_drive_speed = DRIVE_SPEED*0.2 - (dist_err * 35)
            DRIVE_MOTOR_L.set_dps(left_drive_speed)
            DRIVE_MOTOR_R.set_dps(right_drive_speed)

            # Move color sensor arm
            if not COLOR_MOTOR.is_moving():
                COLOR_MOTOR.set_position_relative(ARM_MOVEMENT)
                ARM_MOVEMENT *= -1
            
            # Green sticker detected
            if color == "green":
                print("Green sticker detected.")
                count = 0
                COLOR_MOTOR.set_dps(0)
                green_detected = True
            
            # No sticker detected in office
            if count >= 140:
                DRIVE_MOTOR_L.set_dps(0)
                DRIVE_MOTOR_R.set_dps(0)
                print("No sticker detected, leaving office.")
                break
        
        # Delivering foam cube
        if green_detected:
            if count < 14:
                DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*-0.25)
                DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*-0.25)

            else:
                COLOR_MOTOR.set_limits(power=15)
                print(COLOR_MOTOR.get_position())
                arm_offset = 10 - COLOR_MOTOR.get_position()/5 + 10*deliveries
                print(arm_offset)
                COLOR_MOTOR.set_position_relative(arm_offset)
                sleep(0.5)
                DROP_MOTOR.set_position_relative(-130)
                DRIVE_MOTOR_L.set_dps(0)
                DRIVE_MOTOR_R.set_dps(0)
                sleep(1)
                
                print("Play delivered sound")
                play_sound(0)
                delivered = True
                
                DROP_MOTOR.set_position_relative(45)
                sleep(1)
                break
        

        count += 1

        sleep(0.1)
    
    
    outside = False
    # Prepare arm position
    COLOR_MOTOR.set_limits(power=20)
    count = 0
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)
        
        if color == "orange":  # Detect orange line (door)
            print("Outside detected")
            outside = True
        
        if count == 0:
            COLOR_MOTOR.set_position_relative(160)
            ARM_MOVEMENT *= -1
            
        if count >= 25:
            break
        
        count += 1
        sleep(0.1)
    

    print("Leaving office")
    # Leave office
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)
        
        # Still inside office
        if not outside:
            DRIVE_MOTOR_L.set_dps(-DRIVE_SPEED)
            DRIVE_MOTOR_R.set_dps(-DRIVE_SPEED)
            
            if color == "orange":  # Detect orange line (door)
                print("Outside detected")
                outside = True

        # Outside office, realign with main path
        else:
            # Get angle from Gyro Sensor
            angle = GYRO_SENSOR.get_abs_measure() - angle_offset
            
            if angle in range(4, 15):
                print("Alligned with path, going straight")
                break
            
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*0.08)
    
    print("Go back a bit")
    # Go back a bit
    count = 0
    while not EMMERGENCY_STOP.is_pressed() and not red_detected:
        if count < 10:
            # Get distance from Ultrasonic Sensor
            distance = US_SENSOR.get_value()
            dist_err = distance - 6  # Calculate distance error
            left_drive_speed = -DRIVE_SPEED + (dist_err * 20)
            right_drive_speed = -DRIVE_SPEED - (dist_err * 20)
            DRIVE_MOTOR_L.set_dps(left_drive_speed)
            DRIVE_MOTOR_R.set_dps(right_drive_speed)
        else:
            break
        
        count += 1
        sleep(0.1)
    
    print("Going back to driving straight")
    return (EMMERGENCY_STOP.is_pressed(),delivered)
        

def mail_room_movement(DRIVE_SPEED):
    "Manage movement into mail room"
    angle_offset = GYRO_SENSOR.get_abs_measure()
    inside = False
    countdown = 31

    while not EMMERGENCY_STOP.is_pressed():
        # Get color detected by the Color Sensor
        rgb = COLOR_SENSOR.get_rgb()
        if (rgb and rgb[0] and rgb[1] and rgb[2]):
            color = detect_color(rgb)
        
        # Get distance from Ultrasonic Sensor
        distance = US_SENSOR.get_value()

        # Get angle from Gyro Sensor
        angle = GYRO_SENSOR.get_abs_measure() - angle_offset
        
        if angle in range(-55, 50):
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*0.35)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*1.25)
        
        elif angle in range(-80, -55):
            DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*1)
            DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*1.25)
            
        else:  # Drive straight after turn
            print(distance)
            #dist_err = distance - 54  # Calculate distance error
            dist_err = 0
            left_drive_speed = DRIVE_SPEED + (dist_err * 15)
            right_drive_speed = DRIVE_SPEED - (dist_err * 15)
            DRIVE_MOTOR_L.set_dps(left_drive_speed)
            DRIVE_MOTOR_R.set_dps(right_drive_speed)
        
        if color == "orange":  # Detect if inside mail room
            inside = True
            print("inside")
        
        if inside:
            countdown -= 1
        
        if countdown <= 0:
            print("FINISHED!")
            DRIVE_MOTOR_L.set_dps(0)
            DRIVE_MOTOR_R.set_dps(0)
            play_sound(1)
            break
        
        sleep(0.1)

def robot():
    "Manage autonomous control of the robot."
    CORRECTION_FACTOR = 30
    DRIVE_DIST = 6  # Desired distance from wall in cm
    DRIVE_SPEED = 200  # Base driving speed in dps

    # State -> 0: driving straight, 1 to 4: offices navigation, 5: turning left, 6: mail room approach
    state = 0

    deliveries = 0  # Number of deliveries made
    lineNb = 0  # Number of lines counted
    color = None  # Current detected color
    last_color = "white"  # Last detected color
    angle_offset = 0  # Initial angle measured

    turn = {4:False, 7:False, 10:False, 12:False}  # Track if turn has been made
    
    office = {1:False, 3:False, 6:False, 9:False}  # Track if office has been visited
    officeNb = {1:4, 3:3, 6:2, 9:1}  # Map line number to office state
    countdown = 0
    
    try:
        while not EMMERGENCY_STOP.is_pressed():  # Waiting for button press to start program
            pass
        sleep(0.5)

        print("Starting program. Press the emergency stop to end.")

        while not EMMERGENCY_STOP.is_pressed():
            # Get color detected by the Color Sensor
            rgb = COLOR_SENSOR.get_rgb()
            if (rgb and rgb[0] and rgb[1] and rgb[2]):
                color = detect_color(rgb)
            
            # Get distance from Ultrasonic Sensor
            distance = US_SENSOR.get_value()

            # Get angle from Gyro Sensor
            angle = GYRO_SENSOR.get_abs_measure()

            if state == 0:  # Driving straight state
                # Drive straight with wall distance correction
                dist_err = distance - DRIVE_DIST  # Calculate distance error
                left_drive_speed = DRIVE_SPEED + (dist_err * CORRECTION_FACTOR)
                right_drive_speed = DRIVE_SPEED - (dist_err * CORRECTION_FACTOR)
                DRIVE_MOTOR_L.set_dps(left_drive_speed)
                DRIVE_MOTOR_R.set_dps(right_drive_speed)

                
                # Line detection
                if color == "black" and last_color != "black" and countdown <= 0:
                    lineNb += 1
                    print(f"Line {lineNb} detected.")

                # Turn at the end of a map side
                if lineNb in (4, 7, 10, 12) and not turn[lineNb]:  
                    angle_offset = angle  # Set angle offset for turn
                    state = 5  # Turn left
                    if lineNb == 12: lineNb = 1
                    turn[lineNb] = True
                
                # Enter offices if not yet visited and deliveries not completed
                elif lineNb in (1,3,6,9) and not office[lineNb] and deliveries < 2:
                    state = officeNb[lineNb]
                    office[lineNb] = True
                
                # Go to mail room after deliveries completed
                elif lineNb in (2, 8) and deliveries >= 2:
                    state = 6
                
                countdown -= 1  # Decrease countdown to avoid multiple line counts
            

            if state in (1, 2, 3, 4):  # Go to office
                data = office_movement(DRIVE_SPEED, state, deliveries)

                if data[0]: break  # Emmergency stop pressed
                
                if data[1]: deliveries += 1  # Delivery made
                
                countdown = 10
                state = 0

            elif state == 5:  # Turn left
                DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*0.5)
                DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*1.25)
                
                if angle-angle_offset in range(-80, -65):
                    DRIVE_MOTOR_L.set_dps(DRIVE_SPEED*0.95)
                    DRIVE_MOTOR_R.set_dps(DRIVE_SPEED*1.25)
                    
                if angle-angle_offset in range(-92, -80):
                    print("Turn completed.")
                    state = 0
            
            elif state == 6:  # Go to mail room
                mail_room_movement(DRIVE_SPEED)
                break

            last_color = color  # Update last color

            sleep(0.1)
            
    except BaseException as e:
        print(e)

    finally:
        print("Emmergency stop pressed. Stopping all actions")
        reset_brick() # Turn off everything on the brick's hardware, and reset it
        exit()


if __name__ == "__main__":
    robot()
