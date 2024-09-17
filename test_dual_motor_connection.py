import sys
import time
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor



driving_motor_id = 69 # CAN ID (127 for MN1005 and 69 for RI8523)
driving_vel_command = 100 #RPM

driven_motor_id = 127
driven_current_command = 1 #Amp
t_test = 5 # seconds


if __name__ == '__main__':
    
    driving_motor = Motor(node_id=driving_motor_id)
    driving_motor.set_mode(mode = 1)
    time.sleep(2)
    driven_motor = Motor(can_network = driving_motor.network,node_id = driven_motor_id)
    driven_motor.set_mode(mode=0)
 
    loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.01)
    vel_ready = False
    current_ready = False
    try:
        driving_motor.set_velocity(driving_vel_command,units = 1)
        for t in loop:
            driving_vel = driving_motor.get_velocity(units = 1)
            driven_current = driven_motor.get_current()
            if abs(driving_vel-driving_vel_command) >2 and not(vel_ready): 
                print("Velocity Goal Reached")
                vel_ready = True
                driven_motor.set_current(driven_current)
            else:
                vel_ready = 0

            if vel_ready:
                if abs(driven_current - driven_current_command) > .1 and not(current_ready):
                    print("Current Goal Reached")
                    current_ready = True
                    t0 = time.time()
            else:
                current_ready = False
            if current_ready and vel_ready:   
                if abs(t-t0) <= t_test:
                    print(*["Velocity (RPM): ", int(driving_motor.get_velocity(units = 1)), "Current (A): ",driven_motor.get_current()])
                else:
                    break
        driven_motor.set_current(0)
        print("Stopping Driven Motor")
        time.sleep(1)
        driving_motor.set_velocity(0)
        print("Stopping Driving Motor")
        time.sleep(1)
    except:
        driven_motor.set_current(0)
        print("Stopping Driven Motor")
        time.sleep(1)
        driving_motor.set_velocity(0)
        print("Stopping Driving Motor")
        time.sleep(1)
    finally:
        driven_motor.disconnect()
        driving_motor.disconnect()
        print("Dual Motor Test Finished")
