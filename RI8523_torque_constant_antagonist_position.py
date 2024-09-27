import sys
import time
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor

current_motor_id = 69
velocity_motor_id = 127
sample_rate = 100
test_time = 3
ramp_time = 2

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
        # if abs(motor.get_current()) >= 4:
        #             print("Velocity Control Fault. Error with Command")
        #             raise Exception("Velocity Control Fault. Error with Command")
    print("Velocity Successfully Ramped\n\n")
    time.sleep(1)
    # time.sleep(5)

def ramp_curr(motor, current_desired, ramp_time, sample_freq):
    current_now = motor.get_current()
    current_command = np.linspace(current_now,current_desired, sample_freq*ramp_time)
    print("Starting Current Ramp...\n")
    time.sleep(1)
    # loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.01)
    for c in current_command:
        motor.set_current(c)
        print(*["Measured Vel: ", motor.get_velocity(units=1)," Current Command: ", motor.get_current()])
        time.sleep(1/sample_freq)
        # if abs(motor.get_current()) >= 4:
        #             print("Velocity Control Fault. Error with Command")
        #             raise Exception("Velocity Control Fault. Error with Command")
    print("Current Successfully Ramped\n\n")
    time.sleep(1)
    # time.sleep(5)

if __name__ == '__main__':
    current_motor = Motor(node_id = current_motor_id)
    current_motor.set_mode(mode = 0)
    time.sleep(.5)

    velocity_motor = Motor(node_id = velocity_motor_id)
    velocity_motor.set_mode(mode = 1)
    time.sleep(.5)

    velocity_motor.set_velocity(0, units = 1)
    current_motor.set_current(0)
    time.sleep(.5)

    current_motor.go_operational()
    velocity_motor.go_operational()
    time.sleep(.5)

    ramp_curr(current_motor, 1, ramp_time, sample_rate)
    t0 = time.time()
    while test_time - t0 > 0:
        print(*["Current Motor Current (A): ", current_motor.get_current(), " Velocity Motor Velocity (RPM): ", velocity_motor.get_velocity(units = 1)])
        time.sleep(1/sample_rate)
    ramp_curr(current_motor, 0, ramp_time, sample_rate)
    time.sleep(.5)
    velocity_motor.set_current(0)
    print("Constant Current Test Finished....")

    