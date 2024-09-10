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

def readData(on_target):

    t = time.time() - t0
    vel_MN1005, i_MN1005 = MN1005.pcw.get_tpdo_results(index=1)
    vel_RI8523, i_RI8523 = RI8523.pcw.get_tpdo_results(index=1)
    vel_MN1005 *= MN1005.cts_sec_to_RPM
    vel_RI8523 *= RI8523.cts_sec_to_RPM
    i_MN1005 *= MN1005.rated_1000_to_mA*MN1005.elmo_i_to_i_q
    i_RI8523 *= RI8523.rated_1000_to_mA*RI8523.elmo_i_to_i_q
    adc.update()
    futek_torque = adc.get_torque()-res_torque
    if curr_motor == 1: # MN1005 in current control
        csv_writer.writerow([t, curr_motor, MN1005.current_command_mA, RI8523.vel_command_RPM, on_target,\
                             vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque])
    elif curr_motor == 2: # RI8523 Motor in current control
        csv_writer.writerow([t, curr_motor, RI8523.current_command_mA, MN1005.vel_command_RPM, on_target,\
                             vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque])

    return vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque

def readLoop(t_loop, on_target):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readData(on_target)

    return

def hitCurrTarget(i_target_mA, hold_t, Motor_test):

    Motor_test.set_current_mA(current_command_mA=i_target_mA, verbose=True)

    i_now = readData(0)[curr_motor+1]
    while abs(i_now - i_target_mA) > abs(i_target_mA/1000) + 10:
        i_now = readData(0)[curr_motor+1]

    print('Hit target', str(i_target_mA), 'mA')
    target_torque = readData(1)[4]
    print(f'Futek Torque: {target_torque:.3f}')
    readLoop(hold_t, 1)

    Motor_test.set_current_mA(current_command_mA=0)

    i_now = readData(0)[curr_motor+1]
    while abs(i_now - 0) > 10:
        i_now = readData(0)[curr_motor+1]

    print('Cooling down...')
    # readLoop(2, 0)
    time.sleep(2)

def hitVelTargets(vel_targets, i_targets, Vel_Motor, Curr_Motor):

    global res_torque, vel_RPM

    for vel_RPM in vel_targets:

        Vel_Motor.set_velocity_RPM(vel_command_RPM=vel_RPM, verbose=True)

        vel_now = readData(0)[1 if curr_motor==1 else 0]
        while abs(vel_now - vel_RPM) > 2: # allow velocity to ramp up
            vel_now = readData(0)[1 if curr_motor==1 else 0]
        print('Hit target', str(vel_RPM), 'RPM')

        for current_mA in i_targets:
            hitCurrTarget(current_mA, 2, Curr_Motor)

        Vel_Motor.set_velocity_RPM(vel_command_RPM=0, verbose=True)

        vel_now = readData(0)[1 if curr_motor==1 else 0]
        while abs(vel_now - 0) > 2: # allow velocity to ramp down
            vel_now = readData(0)[1 if curr_motor==1 else 0]

        Vel_Motor.set_current_mA(current_command_mA=0)

        print("Sleeping between positions.")
        # readLoop(120, 0)
        sleep_time = 300
        t_wait0 = time.time()
        t = time.time() - t_wait0
        while t < sleep_time:
            t = time.time() - t_wait0
            print(f"\rSleep Time: {int(sleep_time-t)}         ", end='')
            time.sleep(1)
        print("\n")
        adc.update()
        res_torque = adc.get_torque()


def getVelTargets(vel_range, n_targets):

    vel_targets = []

    for i in range(n_targets):
        vel_span = vel_range[1] - vel_range[0]
        vel_step = vel_span/(n_targets - 1)
        vel_targets.append(vel_range[0] + i*vel_step)

    return vel_targets

def getCurrTargets(i_range, n_targets):

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

    global t0, res_torque, curr_motor, MN1005, RI8523, csv_writer

    MN1005 = Motor(node_id=126, can_network=None, control_mode=4,\
                    rated_current_mA=40000, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    RI8523 = Motor(node_id=127, can_network=MN1005.pcw.network, control_mode=4,\
                    rated_current_mA=12500, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=2750, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
        
    try:

        MN1005.pcw.setup_tpdo(['velocity_sensor_actual_value', 'current_actual_value'], index=1, \
                              trans_type = 254, event_timer = 10, enabled = True)
        RI8523.pcw.setup_tpdo(['velocity_sensor_actual_value', 'current_actual_value'], index=1, \
                             trans_type = 254, event_timer = 10, enabled = True)

        i_range = [-10000, 10000] # mA
        i_increment = 1000 # mA
        n_i_targets = int(abs(i_range[0])/i_increment + abs(i_range[1])/i_increment + 1)
        vel_range = [-1200, 1200] # RPM
        vel_increment = 100 # RPM
        n_vel_targets = int(abs(vel_range[0])/vel_increment + abs(vel_range[1])/vel_increment + 1)

        i_targets = getCurrTargets(i_range, n_i_targets)
        vel_targets = getVelTargets(vel_range, n_vel_targets)
        
        print("Current Targets:", i_targets)
        print("Velocity Targets:", vel_targets)

        MN1005.set_current_mA(current_command_mA=0)
        RI8523.set_current_mA(current_command_mA=0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()

        # curr_motor = 1 # 1: MN1005 current control, RI8523 motor velocity control
        # with open("data/efficiency_PAIRED_MN1005-curr_RI8523-vel_%s.csv"% csv_timestamp,'w') as fd:
        #     csv_writer = csv.writer(fd)
        #     csv_writer.writerow(csv_header)
        #     hitVelTargets(vel_targets, i_targets, Vel_Motor=RI8523, Curr_Motor=MN1005)
        curr_motor = 2 # 2: RI8523 motor current control, MN1005 velocity control
        with open("data/efficiency_PAIRED_RI8523-curr_MN1005-vel_%s.csv"% csv_timestamp,'w') as fd:
            csv_writer = csv.writer(fd)
            csv_writer.writerow(csv_header)
            hitVelTargets(vel_targets, i_targets, Vel_Motor=MN1005, Curr_Motor=RI8523)

        MN1005.disconnect()
        RI8523.disconnect(kill_network=1)

    except:

        if curr_motor == 1:
            MN1005.pcw.config([('torque_slope', 15000)])
            MN1005.set_current_mA(current_command_mA=0, verbose=True)
            # readLoop(2, 0)
            time.sleep(2)
            RI8523.set_current_mA(current_command_mA=0, verbose=True)
        elif curr_motor == 2:
            RI8523.pcw.config([('torque_slope', 15000)])
            RI8523.set_current_mA(current_command_mA=0, verbose=True)
            # readLoop(2, 0)
            time.sleep(2)
            MN1005.set_current_mA(current_command_mA=0, verbose=True)

        MN1005.disconnect()
        RI8523.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_header, csv_timestamp, adc
    csv_timestamp = datetime.now().strftime("%Y-%b-%d-%H%M%S")
    csv_header = ["t", "curr_motor", "curr_target_mA", "vel_target_RPM", "on_target",\
                  "vel_MN1005_RPM", "vel_RI8523_RPM", "i_q_MN1005_mA", "i_q_RI8523_mA", "futek_torque_Nm"]
    # with open("data/efficiency_MN1005-vel_RI8523-curr_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
    #     csv_writer = csv.writer(fd)
    #     csv_writer.writerow(["t", "curr_motor", "curr_target_mA", "vel_target_RPM", "on_target",\
    #                          "vel_MN1005_RPM", "vel_RI8523_RPM", "i_q_MN1005_mA", "i_q_RI8523_mA", "futek_torque_Nm"])
    with Hoop18NmFutek() as adc:
        main()