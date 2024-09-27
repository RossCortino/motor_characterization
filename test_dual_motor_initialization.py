import sys
import time
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor

# driving_motor_id = 69
# driven_motor_id = 127


driving_motor_id = 127
driven_motor_id = 69

if __name__ == '__main__':
    try:
        driving_motor = Motor(node_id=driving_motor_id)
        driving_motor.set_mode(mode = 1)
        time.sleep(2)
        driven_motor = Motor(node_id = driven_motor_id)
        driven_motor.set_mode(mode=0)

        driving_motor.go_operational()
        driven_motor.go_operational()
        
        while True:
            driving_motor.set_velocity(50, units=1)
            driven_motor.set_current(0)
            vel1 = driving_motor.get_velocity(units = 1)
            vel2 = driven_motor.get_velocity(units = 1)

            print(f'{vel1}, {vel2}')
    except:
        
        driving_motor.set_velocity(0, units = 1)
        driving_motor.set_velocity(0, units = 1)
    finally:
        driving_motor.set_current(0)
        driven_motor.set_current(0)
        # driven_motor.disconnect()
        # print("Driven Motor Disconnect")
        # time.sleep(1)
        # driving_motor.disconnect()
        # # print("D")
        # print("Dual Motor initalization Works")