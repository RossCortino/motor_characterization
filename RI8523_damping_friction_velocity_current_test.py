# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
from math import sin, pi
sys.path.append('..')
from GrayDemoCommon import * # reausable script header
from datetime import datetime
from motor import Motor
sys.path.append('/home/pi/hoop-exo/python-can-wrapper')
from pyCANWrapper import PyCANWrapper

def readVelocityCurrent(on_target, RI8523, csv_writer):

    t = time.time() - t0
    vel_RI8523, i_RI8523 = RI8523.pcw.get_tpdo_results(index=1)
    vel_RI8523 *= RI8523.cts_sec_to_RPM
    i_RI8523 *= RI8523.rated_1000_to_mA
    csv_writer.writerow([t, RI8523.vel_command_RPM, on_target, vel_RI8523, i_RI8523])

    return vel_RI8523, i_RI8523


def readLoop(t_loop, on_target, RI8523, csv_writer):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readVelocityCurrent(on_target, RI8523, csv_writer)

    return

def hitTarget(vel_target_RPM, hold_t, RI8523, t0, csv_writer):

    RI8523.set_current_mA(current_command_mA=0)
    readLoop(0.5, 0, RI8523, csv_writer)

    RI8523.set_velocity_RPM(vel_command_RPM=vel_target_RPM)

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

    RI8523 = Motor(node_id=127, can_network=None, control_mode=4,\
                    rated_current_mA=12500, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=2750, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
        
    try:

        RI8523.pcw.setup_tpdo(['velocity_sensor_actual_value', 'current_actual_value'], index=1, \
                            trans_type = 254, event_timer = 10, enabled = True)

        vel_range = [-1200, 1200] # RPM
        vel_increment = 100 # RPM
        n_targets = int(abs(vel_range[0])/vel_increment + abs(vel_range[1])/vel_increment + 1)
        vel_targets = getTargets(vel_range, n_targets)

        t0 = time.time()
        for vel in vel_targets:
            hitTarget(vel, 5, RI8523, t0, csv_writer)

        RI8523.set_current_mA(current_command_mA=0)
        print('Setting current to zero...')
        readLoop(2, 0, RI8523, csv_writer)

        RI8523.disconnect(kill_network=1)

    except:

        RI8523.set_current_mA(current_command_mA=0)
        print('Setting current to zero...')

        RI8523.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':
    
    with open("data/velocity_current_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "vel_target_RPM", "on_target", "vel_RI8523_RPM", "i_RI8523_mA"])
        main(csv_writer)