import sys
import time
import numpy as np
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor

motor_id = 69 # CAN ID (127 for MN1005 and 69 for RI8523)
vel_command = -1000 #RPM
t_test = 2# seconds
t_command_ramp = 5
test_sample_freq = 500

def ramp_vel(motor, vel_desired, ramp_time, sample_freq):
    vel_now = motor.get_velocity(units = 1)
    vel_command = np.linspace(vel_now,vel_desired, sample_freq*ramp_time)
    print("Starting Velocity Ramp...\n")
    time.sleep(1)
    # loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.01)
    for v in vel_command:
        motor.set_velocity(v, units = 1)
        print(*["Commanding Vel: ", motor.get_velocity(units=1)," Current Command: ", motor.get_current()])
        time.sleep(1/sample_freq)
        if abs(motor.get_current()) >= 20:
                    print("Velocity Control Fault. Error with Command")
                    raise Exception("Velocity Control Fault. Error with Command")
    print("Velocity Successfully Ramped\n\n")
    time.sleep(.5)
    # time.sleep(5)
if __name__ == '__main__':
    
    test_motor = Motor(node_id=motor_id)

    test_motor.go_operational()

    test_motor.set_mode(mode =  1)
    
    try:
        ramp_vel(test_motor,vel_command,t_command_ramp,test_sample_freq)
        
        t0 = time.time()
        while time.time()-t0 <= t_test:
            print(*["Commanding Vel: ", test_motor.get_velocity(units=1)])


        # loop = SoftRealtimeLoop(dt = 1/test_sample_freq, report = False, fade = 0.01)
        #     for t in loop:
                    
        #         if t_test-t > 0:
        #             if abs(test_motor.get_current()) > 1.5:
        #                 print("Velocity Control Fault")
        #                 break
        #             print(*["Velocity (RPM): ", int(test_motor.get_velocity(units = 1)), "Current (A): ",test_motor.get_current()])
        #         else:
        #             break
        test_motor.set_velocity(0, units = 1)
    except:
        test_motor.set_velocity(0, units = 1)
    finally:
        test_motor.set_current(0)
        test_motor.disconnect()
        print("Velocity Test Finished")
