# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
from math import sin, pi
from GrayDemoCommon import * # reausable script header
from datetime import datetime
from motor import Motor
sys.path.append('/home/pi/hoop-exo/python-can-wrapper')
from pyCANWrapper import PyCANWrapper

def readVelocityCurrent(on_target, MN1005, Split, csv_writer):

    t = time.time() - t0
    vel_MN1005, i_MN1005 = MN1005.pcw.get_tpdo_results(index=1)
    vel_split, i_split = Split.pcw.get_tpdo_results(index=1)
    vel_MN1005 *= MN1005.cts_sec_to_RPM
    vel_split *= Split.cts_sec_to_RPM
    i_MN1005 *= MN1005.rated_1000_to_mA
    i_split *= Split.rated_1000_to_mA
    csv_writer.writerow([t, Split.vel_command_RPM, on_target, vel_MN1005, vel_split, i_MN1005, i_split])

    return vel_MN1005, vel_split, i_MN1005, i_split

def readLoop(t_loop, on_target, MN1005, Split, csv_writer):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readVelocityCurrent(on_target, MN1005, Split, csv_writer)

    return

def hitTarget(vel_target_RPM, hold_t, MN1005, Split, t0, csv_writer):

    MN1005.set_current_mA(current_command_mA=0)
    Split.set_current_mA(current_command_mA=0)
    readLoop(0.5, 0, MN1005, Split, csv_writer)

    MN1005.set_velocity_RPM(vel_command_RPM=vel_target_RPM)
    Split.set_velocity_RPM(vel_command_RPM=vel_target_RPM)

    MN1005_on = False
    split_on = False
    while not (MN1005_on and split_on):
        vel_MN1005, vel_split, i_MN1005, i_split = readVelocityCurrent(0, MN1005, Split, csv_writer)
        if not MN1005_on and abs(vel_target_RPM - vel_MN1005) < 1:
            MN1005_on = True
            print('MN1005 on target', str(vel_target_RPM), 'RPM.')
        if not split_on and abs(vel_target_RPM - vel_split) < 1:
            split_on = True
            print('Split Motor on target', str(vel_target_RPM), 'RPM.')

def getTargets(vel_range, n_targets):

    vel_targets = []

    for i in range(n_targets):
        vel_span = vel_range[1] - vel_range[0]
        vel_step = vel_span/(n_targets - 1)
        vel_targets.append(vel_range[0] + i*vel_step)

    return vel_targets

def main(csv_writer):

    global t0

    MN1005 = Motor(node_id=126, can_network=None, control_mode=4,\
                    rated_current_mA=12210, max_current_mA=23390,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1500, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    Split = Motor(node_id=127, can_network=MN1005.pcw.network, control_mode=4,\
                    rated_current_mA=11160, max_current_mA=23504,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=600, max_deceleration_RPM_sec=500,\
                        profile_velocity_RPM=1500, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
        
    try:

        MN1005.pcw.setup_tpdo(['velocity_sensor_actual_value', 'current_actual_value'], index=1, \
                            trans_type = 254, event_timer = 10, enabled = True)
        Split.pcw.setup_tpdo(['velocity_sensor_actual_value', 'current_actual_value'], index=1, \
                            trans_type = 254, event_timer = 10, enabled = True)

        vel_range = [-1200, 1200] # RPM
        n_targets = 25
        vel_targets = getTargets(vel_range, n_targets)

        t0 = time.time()
        for vel in vel_targets:
            hitTarget(vel, 5, MN1005, Split, t0, csv_writer)

        MN1005.set_current_mA(current_command_mA=0)
        Split.set_current_mA(current_command_mA=0)
        print('Setting current to zero...')
        readLoop(2, 0, MN1005, Split, csv_writer)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

    except:

        MN1005.set_current_mA(current_command_mA=0)
        Split.set_current_mA(current_command_mA=0)
        print('Setting current to zero...')

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':
    
    with open("data/velocity_current_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "vel_target_RPM", "on_target", "vel_MN1005_RPM", "vel_split_RPM", "i_MN1005_mA", "i_split_mA"])
        main(csv_writer)