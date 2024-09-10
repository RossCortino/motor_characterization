# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
from math import sin, pi
from GrayDemoCommon import * # reausable script header
from datetime import datetime
from motor import Motor
sys.path.append('/home/pi/python-can-wrapper/')
from pyCANWrapper import PyCANWrapper


def readData(on_target):

    t = time.time() - t0
    pos_RI8523, i_RI8523 = RI8523.pcw.get_tdpo_results()
    pos_RI8523 *= RI8523.cts_to_deg
    i_RI8523 *= RI8523.rated_1000_to_mA*RI8523.elmo_i_to_i_q
    adc.update()
    futek_torque = adc.get_torque()-res_torque
    csv_writer.writerow([t, motor_tested, RI8523.current_command_mA, on_target,\
                            pos_RI8523, i_RI8523, futek_torque])

    return pos_RI8523, i_RI8523, futek_torque

def readLoop(t_loop, on_target):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readData(on_target)

    return

def hitTarget(i_target_mA, hold_t, Motor_test):
    # i_target_mA = 0
    Motor_test.set_current_mA(current_command_mA=i_target_mA, verbose=True)
    # read_check = readData(0)
    i_now = readData(0)[1]
    while abs(i_now - i_target_mA) > 10:
        i_now = readData(0)[1]

    print('Hit target', str(i_target_mA), 'mA')
    target_torque = readData(1)[-1]
    print(f'Futek Torque: {target_torque:.3f}')
    readLoop(hold_t, 1)

    Motor_test.set_current_mA(current_command_mA=0)

    i_now = readData(0)[1]
    while abs(i_now - 0) > 10:
        i_now = readData(0)[1]

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

    return sorted(ordered_targets)

def main():

    global t0, res_torque, motor_tested, RI8523

    RI8523 = Motor(node_id=69, can_network=None, control_mode=4,\
                    rated_current_mA=12500, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=2750, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
        
    try:

        # MN1005.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
        #                       trans_type = 254, event_timer = 10, enabled = True)
        RI8523.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                             trans_type = 254, event_timer = 10, enabled = True)

        motor_tested = 2 # 1: testing MN1005, RI8523 motor in pos control, 2: testing RI8523 motor, MN1005 in position control
        i_range = [-1000, 1000] # mA
        i_increment = 1000 # mA
        n_targets = int(abs(i_range[0])/i_increment + abs(i_range[1])/i_increment + 1)
        # n_positions = 1

        i_targets = getTargets(i_range, n_targets) # converted to cts/s
        # positions = [x*360./n_positions for x in range(n_positions)]
        print("Current Targets:", i_targets)
        # print("Positions:", positions)

        assert (motor_tested == 1) or (motor_tested == 2)
        assert (abs(i_range[0]) <= RI8523.rated_current_mA) and (abs(i_range[1]) <= RI8523.rated_current_mA)
        # MN1005.set_current_mA(current_command_mA=0)
        RI8523.set_current_mA(current_command_mA=0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()


        for current_mA in i_targets:
                hitTarget(current_mA, 3, RI8523)

                RI8523.set_current_mA(current_command_mA=0)
                print('Setting current to zero...')

        RI8523.disconnect(kill_network=1)

    except:

        RI8523.pcw.config([('torque_slope', 15000)])
        RI8523.set_current_mA(current_command_mA=0, verbose=True)
        readLoop(2, 0)
        
        RI8523.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_writer, adc
    
    with open("data/RI8523_current_torque_locked_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "motor_tested", "curr_target_mA", "on_target",\
                             "i_q_RI8523_mA", "futek_torque_Nm"])
        with Hoop18NmFutek() as adc:
            main()