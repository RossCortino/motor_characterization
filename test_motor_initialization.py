import sys
import time
from math import sin, pi
from GrayDemoCommon import * # reausable script header
from datetime import datetime
from motor import Motor
sys.path.append('/home/pi/python-can-wrapper/')
from pyCANWrapper import PyCANWrapper

if __name__ == '__main__':
    test_motor = Motor(node_id=69, can_network=None, control_mode=4,\
                    rated_current_mA=12500, max_current_mA=40000, current_slope_mA_sec=5000,\
                    max_velocity_RPM=2750, max_acceleration_RPM_sec=1000, max_deceleration_RPM_sec=1000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=500, profile_deceleraton_RPM_sec=500)
    
    test_motor.pcw.setup_tpdo(['position_actual_internal_value', 'current_actual_value'], index=1, \
                             trans_type = 254, event_timer = 10, enabled = True)
    
    test_motor.pcw.get_tdpo_results()