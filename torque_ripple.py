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

def main():
    global t0, res_torque, pos0, curr_motor, MN1005, Split, csv_writer

    MN1005 = Motor(node_id=126, can_network=None, control_mode=4,\
                    rated_current_mA=40000, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    Split = Motor(node_id=127, can_network=MN1005.pcw.network, control_mode=4,\
                    rated_current_mA=40000, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=1800, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    
    try:
        Driver = MN1005

        Driver = pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                                trans_type = 254, event_timer = 10, enabled = True)

        Driver.set_current_mA(current_command_mA=0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        pos0 = Driver.pcw.get_tpdo_results(index=1)[0]
        t0 = time.time()

        Driver.set_velocity_RPM(vel_command_RPM=60)
        print('Set velocity.')

        while True:
            t = time.time() - t0
            pos, curr = Driver.pcw.get_tpdo_results(index=1)
            pos = (pos - pos0)*Driver.cts_to_deg
            curr *= Driver.rated_1000_to_mA*Driver.elmo_i_to_i_q
            adc.update()
            torque = adc.get_torque() - res_torque
            csv_writer.writerow([t, pos, curr, torque])

    except:
        Driver.pcw.config([('torque_slope', 15000)])
        Driver.set_current_mA(current_command_mA=0, verbose=True)
        time.sleep(2)

        MN1005.disconnect()
        Split.disconnect(kill_network=1)

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_header, adc
    
    with open("data/Split_torqueripple_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "abs_pos_deg", "driving_curr_mA", "futek_torque_Nm"])
        with Hoop18NmFutek() as adc:
            main()