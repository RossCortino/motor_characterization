# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
import os
from math import sin, pi,log10, floor
sys.path.append('/home/pi/NeuroLocoMiddleware')
from SoftRealtimeLoop import SoftRealtimeLoop
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor
def readVelocityCurrent(on_target, test_motor, csv_writer):

    t = time.time() - t0
    vel_motor =  test_motor.get_velocity(units = 1)
    i_motor =  test_motor.get_current()
    csv_writer.writerow([t, "RI8523", test_motor.get_velocity_command(), on_target, vel_motor, i_motor])

    return vel_motor, i_motor


def readLoop(t_loop, loop_freq, on_target, test_motor, csv_writer):
    
    t0_loop = time.time()
    # loop = SoftRealtimeLoop(dt = 1/loop_freq, report=False, fade=0.01)
    while time.time() - t0_loop < t_loop:
        readVelocityCurrent(on_target, test_motor, csv_writer)
        time.sleep(1/loop_freq)

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
    time.sleep(.5)
    # time.sleep(5)

def hitTarget(vel_target_RPM, RI8523, csv_writer):

    RI8523.set_current(0)
    readLoop(0.5, 500,0, RI8523, csv_writer)
    
    RI8523.set_velocity(0, units = 1)
    ramp_vel(RI8523,vel_target_RPM,1,500)

    RI8523_on = False
    while not (RI8523_on):
        vel_RI8523, i_RI8523 = readVelocityCurrent(0, RI8523, csv_writer)
        if not RI8523_on and abs(vel_target_RPM - vel_RI8523) < 2:
            RI8523_on = True
            print('RI8523 Motor on target', str(vel_target_RPM), 'RPM.')

    time.sleep(1)
def getTargets(vel_range, n_targets):

    vel_targets = []

    for i in range(n_targets):
        vel_span = vel_range[1] - vel_range[0]
        vel_step = vel_span/(n_targets - 1)
        vel_targets.append(vel_range[0] + i*vel_step)

    sort_indexes = np.argsort(np.abs(vel_targets))
    # print(sort_indexes[::-1])
    final_targets = np.zeros(np.size(sort_indexes))
    i = 0
    for s in sort_indexes:
        final_targets[i] = vel_targets[s]
        i += 1

    return final_targets
def cls():
    os.system('cls' if os.name=='nt' else 'clear')
def main(csv_writer):

    global t0

    RI8523 = Motor(node_id=69)
    RI8523.set_mode(mode = 1)
    RI8523.go_operational()
    time.sleep(.5)
        
    try:

        vel_range = [-400,400] # RPM
        vel_increment = 50 # RPM
        n_targets = int(abs(vel_range[0])/vel_increment + abs(vel_range[1])/vel_increment + 1)
        vel_targets = getTargets(vel_range, n_targets)

        t0 = time.time()
        loop_freq = 500 #hz
        for vel in vel_targets:
            hitTarget(vel, RI8523, csv_writer)
            readLoop(2, loop_freq, 1, RI8523, csv_writer)
            print(*["Finished Vel Target: ", vel,"\n\n"])
            ramp_vel(RI8523,0,1,500)
            time.sleep(1)
            cls()
            time.sleep(1)


        RI8523.set_current(0)
        
        print('Setting current to zero...')
        readLoop(2,loop_freq, 0, RI8523, csv_writer)


        RI8523.disconnect()

    except:

        RI8523.set_current(0)
        print('Setting current to zero...')

        RI8523.disconnect()

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':
    for i in range(1):
        print(*["Starting Trial #",i+1])
        with open("data/velocity_test/velocity_control/RI8523_damping_friction_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
            csv_writer = csv.writer(fd)
            csv_writer.writerow(["t", "motor_tested", "vel_target_RPM", "on_target", "vel_RI8523_RPM", "i_RI8523_mA"])
            main(csv_writer)
        print("Resting Between Data Collections...\n\n\n")
        time.sleep(10)