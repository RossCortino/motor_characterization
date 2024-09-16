# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
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
    csv_writer.writerow([t, test_motor.get_velocity_command(), on_target, vel_motor, i_motor])

    return vel_motor, i_motor


def readLoop(t_loop, loop_freq, on_target, test_motor, csv_writer):
    
    t0_loop = time.time()
    loop = SoftRealtimeLoop(dt = 1/loop_freq, report=False, fade=0.01)
    for t in loop:
        if time.time() - t0_loop < t_loop:
            readVelocityCurrent(on_target, test_motor, csv_writer)
        else:
            break
    return

def hitTarget(vel_target_RPM, RI8523, csv_writer):

    RI8523.set_current(0)
    readLoop(0.5, 500,0, RI8523, csv_writer)
    
    RI8523.set_velocity(vel_target_RPM, units = 1)

    RI8523_on = False
    while not (RI8523_on):
        vel_RI8523, i_RI8523 = readVelocityCurrent(0, RI8523, csv_writer)
        if not RI8523_on and abs(vel_target_RPM - vel_RI8523) < 1:
            RI8523_on = True
            print('RI8523 Motor on target', str(vel_target_RPM), 'RPM.')


def getTargets(vel_range, n_targets):

    vel_targets = []

    for i in range(n_targets):
        vel_span = vel_range[1] - vel_range[0]
        vel_step = vel_span/(n_targets - 1)
        vel_targets.append(vel_range[0] + i*vel_step)

    return vel_targets

def main(csv_writer):

    global t0

    RI8523 = Motor(node_id=127)
    RI8523.set_mode(mode = 1)
        
    try:

        vel_range = [-1200, -1200] # RPM
        vel_increment = 100 # RPM
        n_targets = int(abs(vel_range[0])/vel_increment + abs(vel_range[1])/vel_increment + 1)
        vel_targets = getTargets(vel_range, n_targets)

        t0 = time.time()
        loop_freq = 500 #hz
        for vel in vel_targets:
            hitTarget(vel, RI8523, csv_writer)
            readLoop(5, loop_freq, 1, RI8523, csv_writer)


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
    
    with open("data/velocity_current_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "vel_target_RPM", "on_target", "vel_RI8523_RPM", "i_RI8523_mA"])
        main(csv_writer)