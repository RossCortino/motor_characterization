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

def readData(on_target):

    t = time.time() - t0
    pos_MN1005, i_MN1005 = MN1005.pcw.get_tpdo_results(index=1)
    pos_split, i_split = Split.pcw.get_tpdo_results(index=1)
    pos_MN1005 *= MN1005.cts_to_deg
    pos_split *= Split.cts_to_deg
    i_MN1005 *= MN1005.rated_1000_to_mA*MN1005.elmo_i_to_i_q
    i_split *= Split.rated_1000_to_mA*Split.elmo_i_to_i_q
    adc.update()
    futek_torque = adc.get_torque()-res_torque
    if motor_tested == 1:
        csv_writer.writerow([t, motor_tested, MN1005.current_command_mA, Split.pos_command_rel_deg, on_target,\
                             pos_MN1005, pos_split, i_MN1005, i_split, futek_torque])
    elif motor_tested == 2:
        csv_writer.writerow([t, motor_tested, Split.current_command_mA, MN1005.pos_command_rel_deg, on_target,\
                             pos_MN1005, pos_split, i_MN1005, i_split, futek_torque])

    return pos_MN1005, pos_split, i_MN1005, i_split, futek_torque

def readLoop(t_loop, on_target):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readData(on_target)

    return

def hitTarget(i_target_mA, hold_t, Motor_test):

    Motor_test.set_current_mA(current_command_mA=i_target_mA, verbose=True)

    i_now = readData(0)[motor_tested+1]
    while abs(i_now - i_target_mA) > 10:
        i_now = readData(0)[motor_tested+1]

    print('Hit target', str(i_target_mA), 'mA')
    target_torque = readData(1)[4]
    print(f'Futek Torque: {target_torque:.3f}')
    readLoop(hold_t, 1)

    Motor_test.set_current_mA(current_command_mA=0)

    i_now = readData(0)[motor_tested+1]
    while abs(i_now - 0) > 10:
        i_now = readData(0)[motor_tested+1]

    print('Cooling down...')
    readLoop(5, 0)

def getTargets(i_range, n_targets):

    i_targets_mA = []

    for i in range(n_targets):
        i_span = i_range[1] - i_range[0]
        i_step = i_span/(n_targets - 1)
        i_targets_mA.append(i_range[0] + i*i_step)

    ordered_targets =[]
    neg_targets_mA = []
    pos_targets_mA = []
    zero_target_mA = []
    for val in i_targets_mA:
        if val < 0:
            neg_targets_mA.append(val)
        elif val > 0:
            pos_targets_mA.append(val)
        else:
            zero_target_mA.append(val)
    target_lists = [neg_targets_mA, zero_target_mA, pos_targets_mA]
    for targets in target_lists:
        for i in range(int(len(targets)//2)):
            ordered_targets.append(targets[i])
            ordered_targets.append(targets[-i-1])
        if len(targets)%2 == 1:
            ordered_targets.append(targets[int(len(targets)//2)])

    return ordered_targets

def main():

    global t0, pos0_split, pos0_MN1005, res_torque, motor_tested, MN1005, Split

    MN1005 = Motor(node_id=126, can_network=None, control_mode=4,\
                    rated_current_mA=12210, max_current_mA=23390, current_slope_mA_sec=5000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    Split = Motor(node_id=127, can_network=MN1005.pcw.network, control_mode=4,\
                    rated_current_mA=11160, max_current_mA=23504, current_slope_mA_sec=5000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=600, max_deceleration_RPM_sec=500,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
        
    try:

        MN1005.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                              trans_type = 254, event_timer = 10, enabled = True)
        Split.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                             trans_type = 254, event_timer = 10, enabled = True)

        motor_tested = 2 # 1: testing MN1005, split motor in pos control, 2: testing split motor, MN1005 in position control
        i_range = [-10000, 10000] # mA
        n_targets = 21
        n_positions = 1

        i_targets = getTargets(i_range, n_targets) # converted to cts/s
        positions = [x*360./n_positions for x in range(n_positions)]
        print("Current Targets:", i_targets)
        print("Positions:", positions)

        assert (motor_tested == 1) or (motor_tested == 2)

        MN1005.set_current_mA(current_command_mA=0)
        Split.set_current_mA(current_command_mA=0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()
        pos_MN1005, pos_split = readData(0)[0:2]
        pos0_MN1005 = pos_MN1005
        pos0_split = pos_split

        for pos_deg in positions:

            if motor_tested == 1: # split motor in position control
                    Split.set_position_rel_deg(pos_command_rel_deg=pos_deg, pos0_deg=pos0_split, verbose=True)

                    for current_mA in i_targets:
                        hitTarget(current_mA, 3, MN1005)

                    MN1005.set_current_mA(current_command_mA=0)
                    print('Setting current to zero...')

            elif motor_tested == 2: # MN1005 in position control
                MN1005.set_position_rel_deg(pos_command_rel_deg=pos_deg, pos0_deg=pos0_split, verbose=True)

                for current_mA in i_targets:
                    hitTarget(current_mA, 3, Split)

                Split.set_current_mA(current_command_mA=0)
                print('Setting current to zero...')
                
            print("Sleeping between positions.")
            readLoop(10, 0)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

    except:

        if motor_tested == 1:
            MN1005.pcw.config([('torque_slope', 15000)])
            MN1005.set_current_mA(current_command_mA=0, verbose=True)
            readLoop(2, 0)
            Split.set_current_mA(current_command_mA=0, verbose=True)
        elif motor_tested == 2:
            Split.pcw.config([('torque_slope', 15000)])
            Split.set_current_mA(current_command_mA=0, verbose=True)
            readLoop(2, 0)
            MN1005.set_current_mA(current_command_mA=0, verbose=True)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_writer, adc
    
    with open("data/MN1005_current_torque_posdep_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "motor_tested", "curr_target_mA", "rel_pos_target_deg", "on_target",\
                             "abs_pos_MN1005_deg", "abs_pos_split_deg", "i_q_MN1005_mA", "i_q_split_mA", "futek_torque_Nm"])
        with Hoop18NmFutek() as adc:
            main()