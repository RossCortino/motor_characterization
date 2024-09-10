import sys
import math
sys.path.append('/home/pi/hoop-exo/python-can-wrapper')
from pyCANWrapper import PyCANWrapper

class Motor:
    def __init__(self, node_id=127, can_network=None, control_mode=4,\
                 rated_current_mA=10000, max_current_mA=20000, current_slope_mA_sec=1000,\
                    max_velocity_RPM=1000, max_acceleration_RPM_sec=10000, max_deceleration_RPM_sec=10000,\
                        profile_velocity_RPM=1000, profile_acceleration_RPM_sec=8000, profile_deceleraton_RPM_sec=8000,\
                            encoder_res_cts_rev=40000, winding_type=0):
        
        self.node_id = node_id
        self.control_mode = control_mode # 1=profliled position, 3=profiled velocity, 4=profiled torque, 6=homing, 7=initerp. pos

        self.rated_current_mA = rated_current_mA
        self.max_current_mA = max_current_mA
        self.current_slope_mA_sec = current_slope_mA_sec

        self.max_velocity_RPM = max_velocity_RPM
        self.max_acceleration_RPM_sec = max_acceleration_RPM_sec
        self.max_deceleration_RPM_sec = max_deceleration_RPM_sec

        self.profile_velocity_RPM = profile_velocity_RPM
        self.profile_acceleration_RPM_sec = profile_acceleration_RPM_sec
        self.profile_deceleration_RPM_sec = profile_deceleraton_RPM_sec

        self.encoder_res_cts_rev = encoder_res_cts_rev
        self.winding_type = winding_type # 0: delta wound, 1: wye wound

        self.mA_to_rated_1000 = 1000/self.rated_current_mA
        self.rated_1000_to_mA = self.rated_current_mA/1000
        self.deg_to_cts = self.encoder_res_cts_rev/360
        self.cts_to_deg = 360/self.encoder_res_cts_rev
        self.RPM_to_cts_sec = self.encoder_res_cts_rev/60
        self.cts_sec_to_RPM = 60/self.encoder_res_cts_rev
        # Elmo reports line current amplitude as active/actual current (based on vector mag invariant Clarke-Park on wye motors)
        self.elmo_i_to_i_q = math.sqrt(3/2) if self.winding_type==1 else math.sqrt(1/2)
        self.i_q_to_elmo_i = math.sqrt(2/3) if self.winding_type==1 else math.sqrt(2)

        self.pos_command_deg = 0
        self.vel_command_RPM = 0
        self.current_command_mA = 0
        self.pos_command_rel_deg = 0

        self.init = False

        self.pcw = PyCANWrapper(can_network=can_network, node=self.node_id, verbose=False, \
                                eds_file_loc="/home/pi/hoop-exo/python-can-wrapper/GoldSoloTwitter.eds")
        
        self.config=[
            ('controlword', 0x000F),
            ('modes_of_operation', self.control_mode), # 1=profliled position, 3=profiled velocity, 4=profiled torque, 6=homing, 7=initerp. pos
            # Profiled Torque Mode
            ('max_torque', int(self.max_current_mA*self.mA_to_rated_1000)), # max torque command, units of motor_rated_torque/1000
            ('max_current', int(self.max_current_mA*self.mA_to_rated_1000)), # max current command, units of motor_rated_current/1000
            ('motor_rated_current', self.rated_current_mA), # continuous motor current, units of mA
            ('motor_rated_torque', self.rated_current_mA), # continuous torque, units of mNm
            ('torque_slope', int(self.current_slope_mA_sec*self.mA_to_rated_1000)), # units of motor_rated_torque/1000/second
            ('target_torque', 0),
            # Profiled Velocity Mode
            ('sensor_selection_code', 0), # 0=Position Encoder, 1=Velocity Encoder
            ('target_velocity', 0),
            # Profiled Position
            # Can be switched b/w relative & absolute by changing 
            # the relative flag in the controlword for profiled position
            # ('target_position', 0), # Target Position in User Defined Units (counts)
            ('max_profile_velocity', int(self.max_velocity_RPM*self.RPM_to_cts_sec)), # counts/sec
            ('max_motor_speed', int(self.max_velocity_RPM*self.RPM_to_cts_sec)), # counts/sec
            ('profile_velocity', int(self.profile_velocity_RPM*self.RPM_to_cts_sec)), # Motor speed during profiled position motion, counts/sec
            ('end_velocity', 0), # Velocity when the position target is reached
            ('profile_acceleration', int(self.profile_acceleration_RPM_sec*self.RPM_to_cts_sec)), # Acceleration limit for profiled position & velocity, counts/sec/sec
            ('profile_deceleration' , int(self.profile_deceleration_RPM_sec*self.RPM_to_cts_sec)), # Deceleration limit for profiled position & velocity, counts/sec/sec
            ('quick_stop_deceleration', int(0.5*self.max_deceleration_RPM_sec*self.RPM_to_cts_sec)), # Deceleration when quick stop is enabled, counts/sec/sec
            ('motion_profile_type', 0), # Motion Profile - Trapezoidal Ramp (No other profiles available)
            ('max_acceleration', int(self.max_acceleration_RPM_sec*self.RPM_to_cts_sec)), # Configured max. acceleration in counts/sec/sec
            ('max_deceleration', int(self.max_deceleration_RPM_sec*self.RPM_to_cts_sec)) # Configured max. deceleration in counts/sec/sec   
        ]
        
        self.pcw.config(config=self.config)
        self.pcw.config(config=[('controlword', 0x81)])

        if can_network is None:
            self.pcw.network.sync.start(0.1)
        
        self.pcw.go_operational(timeout_s=15, sync_timing=0.1, node_guarding_period=0.01)

        print('Motor ID', str(self.node_id), 'operational.')

    def disconnect(self, kill_network=0):
        self.pcw.disconnect()
        print('Motor ID', str(self.node_id), 'disconnected.')
        if kill_network:
            self.pcw.disconnect_network()
            print('CAN Network disconnected.')
        

    def get_position():
        pass
    
    def get_velocity():
        pass

    def get_current():
        pass

    def set_position_rel_deg(self, pos_command_rel_deg, pos0_deg, verbose=False):
        self.pos_command_rel_deg = pos_command_rel_deg
        pos_command_abs_cts = (pos0_deg + pos_command_rel_deg)*self.deg_to_cts
        self.pcw.config(config=[('controlword', 0xF), ('modes_of_operation', 1), ('target_position', int(pos_command_abs_cts)), ('controlword', 0x1F)])
        if verbose:
            print('Motor', str(self.node_id), 'Position command:', str(pos_command_rel_deg), 'deg (relative)')
            print('Absolute encoder counts:', str(pos_command_abs_cts))

    def set_velocity_RPM(self, vel_command_RPM, verbose=False):
        self.vel_command_RPM = vel_command_RPM
        vel_command_cts = vel_command_RPM*self.RPM_to_cts_sec
        self.pcw.config(config=[('controlword', 0x81), ('modes_of_operation', 3), ('target_velocity', int(vel_command_cts))])
        if verbose:
            print('Motor', str(self.node_id), 'Velocity command:', str(vel_command_RPM), 'RPM')

    def set_current_mA(self, current_command_mA, verbose=False):
        self.current_command_mA = current_command_mA
        current_command = current_command_mA*self.i_q_to_elmo_i*self.mA_to_rated_1000
        self.pcw.config(config=[('controlword', 0x81), ('modes_of_operation', 4), ('target_torque', int(current_command))])
        if verbose:
            print('Motor', str(self.node_id), 'Current command:', str(current_command_mA), 'mA')