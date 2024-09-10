# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import traceback
import time
from math import sin, pi
from GrayDemoCommon import * # reausable script header
from datetime import datetime
from motor import Motor
sys.path.append('/home/pi/hoop-exo/python-can-wrapper')
from pyCANWrapper import PyCANWrapper

def readData(verbose=False):

    t = time.time() - t0
    pos_MN1005, i_MN1005 = MN1005.pcw.get_tpdo_results(index=1)
    if verbose:
        print(f"\rTPDO pos: {pos_MN1005:.3f}", end='')
    pos_split, i_split = Split.pcw.get_tpdo_results(index=1)
    pos_MN1005 *= MN1005.cts_to_deg
    pos_split *= Split.cts_to_deg
    i_MN1005 *= MN1005.rated_1000_to_mA*MN1005.elmo_i_to_i_q
    i_split *= Split.rated_1000_to_mA*MN1005.elmo_i_to_i_q
    adc.update()
    futek_torque = adc.get_torque()-res_torque
    csv_writer.writerow([t, pos_MN1005, pos_split, i_MN1005, i_split, futek_torque])

    return pos_MN1005, pos_split, i_MN1005, i_split, futek_torque

def readLoop(t_loop):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData(verbose=True)
        # print('Current:', str(i_split), 'mA, Torque:', str(futek_torque), 'Nm')

    return

def main():

    global t0, res_torque, pos0_MN1005, pos0_split, motor_tested, MN1005, Split

    MN1005 = Motor(node_id=126, can_network=None, control_mode=1,\
                   rated_current_mA=12210, max_current_mA=23390, current_slope_mA_sec=1000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=15000, max_deceleration_RPM_sec=15000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=10000, profile_deceleraton_RPM_sec=10000)
    Split = Motor(node_id=127, can_network=MN1005.pcw.network, control_mode=1,\
                  rated_current_mA=12210, max_current_mA=23390, current_slope_mA_sec=1000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=15000, max_deceleration_RPM_sec=15000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=10000, profile_deceleraton_RPM_sec=10000)

    try:

        MN1005.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                              trans_type = 254, event_timer = 10, enabled = True)
        Split.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                             trans_type = 254, event_timer = 10, enabled = True)
        
        MN1005.set_current_mA(current_command_mA=0)
        Split.set_current_mA(current_command_mA=0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()

        pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData(verbose=True)
        pos0_MN1005 = pos_MN1005
        
        pos0_split = pos_split
        
        # pos_des = (0 + pos0_split)*MN1005.deg_to_cts
        # MN1005.pcw.config(config=[('modes_of_operation', 1), ('controlword', 0xF), ('target_position', int(pos_des)), ('controlword', 0x1F)])
        # time.sleep(10)
        # pos_des = (60 + pos0_split)*MN1005.deg_to_cts
        # MN1005.pcw.config(config=[('modes_of_operation', 1), ('controlword', 0xF), ('target_position', int(pos_des)), ('controlword', 0x1F)])
        # time.sleep(10)
        # pos_des = (0 + pos0_split)*MN1005.deg_to_cts
        # MN1005.pcw.config(config=[('modes_of_operation', 1), ('controlword', 0xF), ('target_position', int(pos_des)), ('controlword', 0x1F)])

        MN1005.set_position_rel_deg(pos_command_rel_deg=0, pos0_deg=pos0_MN1005, verbose = True)
        readLoop(3)
        MN1005.set_position_rel_deg(pos_command_rel_deg=60, pos0_deg=pos0_MN1005, verbose = True)
        readLoop(3)
        MN1005.set_position_rel_deg(pos_command_rel_deg=0, pos0_deg=pos0_MN1005, verbose = True)

        # MN1005.set_position_abs_cts(pos_MN1005*MN1005.deg_to_cts)
        # readLoop(0.5)

        # motor_tested = 2
        # current_command_mA = 10000

        # Split.set_current_mA(current_command_mA=current_command_mA)
        # pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData()
        # while abs(i_split - current_command_mA) > 10:
        #     pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData()
        # readLoop(float('inf'))
        # Split.set_current_mA(current_command_mA=0)
        # pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData()
        # while abs(i_split - 0) > 10:
        #     pos_MN1005, pos_split, i_MN1005, i_split, futek_torque = readData()

        # MN1005.set_current_mA(current_command_mA=0)

        time.sleep(0.1)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

    except:

        Split.set_current_mA(current_command_mA=0)
        MN1005.set_current_mA(current_command_mA=0)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_writer, adc
    
    # with open("data/test_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
    with open("data/test.csv",'w') as fd:
        csv_writer = csv.writer(fd)
        # csv_writer.writerow(["t", "vel_target_RPM", "vel_MN1005_RPM", "vel_split_RPM", "i_MN1005_A", "i_split_A"])
        # csv_writer.writerow(["t", "pos_target_deg", "pos_MN1005_deg", "pos_split_deg", "i_MN1005_A", "i_split_A"])
        csv_writer.writerow(["t", "pos_MN1005_deg", "pos_split_deg", "i_MN1005_mA", "i_split_mA", "futek_torque_Nm"])
        with Hoop18NmFutek() as adc:
            main()