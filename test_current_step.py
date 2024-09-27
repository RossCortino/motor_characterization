import sys
import time
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor

motor_id = 69 # CAN ID (127 for MN1005 and 69 for RI8523)
current_command = -.1 #Amps
t_test = 5# seconds


if __name__ == '__main__':
    
    test_motor = Motor(node_id=motor_id)
    test_motor.go_operational()
    test_motor.set_mode(mode = 0)

    time.sleep(2)
    test_motor.set_current(current_command)
    loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.002)
    try:
        for t in loop:
            if t_test-t > 0:
                print(*["Velocity (RPM): ", test_motor.get_velocity(units = 1), "Current (A): ", test_motor.get_current()])
            else:
                break
        test_motor.set_current(0)
    except:
        test_motor.set_current(0)
    finally:
        test_motor.disconnect()
        print("Current Test Finished")