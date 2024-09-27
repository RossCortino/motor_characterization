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

def readData(on_target):

    t = time.time() - t0
    # vel_MN1005, i_MN1005 = MN1005.pcw.get_tpdo_results(index=1)
    # vel_RI8523, i_RI8523 = RI8523.pcw.get_tpdo_results(index=1)

    vel_MN1005 = MN1005.get_velocity(units = 1)
    i_MN1005 = MN1005.get_current()

    vel_RI8523 = RI8523.get_velocity(units = 1)
    i_RI8523 = RI8523.get_current()

    adc.update()
    futek_torque = adc.get_torque()-res_torque
    if curr_motor == 1: # MN1005 in current control
        csv_writer.writerow([t, curr_motor, MN1005.get_current_command(), RI8523.get_velocity_command(), on_target,\
                             vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque])
    elif curr_motor == 2: # RI8523 Motor in current control
        csv_writer.writerow([t, curr_motor, RI8523.get_current_command(), MN1005.get_velocity_command(), on_target,\
                             vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque])

    return vel_MN1005, vel_RI8523, i_MN1005, i_RI8523, futek_torque

def readLoop(t_loop, on_target):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readData(on_target)
        time.sleep(1/500)

    return

def hitCurrTarget(i_target_A, hold_t, Motor_test):

    ramp_curr(Motor_test,i_target_A,2,500)
    # Motor_test.set_current(i_target_A)

    i_now = readData(0)[curr_motor+1]
    while abs(i_now - i_target_A) > 0.01:
        i_now = readData(0)[curr_motor+1]
    time.sleep(1)
    print('Hit target', str(i_target_A), 'A')
    target_torque = readData(1)[4]
    print(f'Futek Torque: {target_torque:.3f}')
    readLoop(hold_t, 1)

    # Motor_test.set_current(0)
    ramp_curr(Motor_test,0,2,500)

    i_now = readData(0)[curr_motor+1]
    while abs(i_now - 0) > .1:
        i_now = readData(0)[curr_motor+1]

    print('Cooling down...')
    # readLoop(2, 0)
    time.sleep(2)

def ramp_vel(motor, vel_desired, ramp_time, sample_freq):
    vel_now = motor.get_velocity(units = 1)
    vel_command = np.linspace(vel_now,vel_desired, sample_freq*ramp_time)
    print("Starting Velocity Ramp...\n")
    time.sleep(1)
    # loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.01)
    for v in vel_command:
        motor.set_velocity(v, units = 1)
        print(*["Commanding Vel: ", motor.get_velocity(units=1)," Current Command: ", motor.get_current()])
        time.sleep(1/sample_freq)
        # if abs(motor.get_current()) >= 4:
        #             print("Velocity Control Fault. Error with Command")
        #             raise Exception("Velocity Control Fault. Error with Command")
    print("Velocity Successfully Ramped\n\n")
    time.sleep(1)
    # time.sleep(5)

def ramp_curr(motor, current_desired, ramp_time, sample_freq):
    current_now = motor.get_current()
    current_command = np.linspace(current_now,current_desired, sample_freq*ramp_time)
    print("Starting Current Ramp...\n")
    time.sleep(1)
    # loop = SoftRealtimeLoop(dt = 1/500, report = False, fade = 0.01)
    for c in current_command:
        motor.set_current(c)
        print(*["Measured Vel: ", motor.get_velocity(units=1)," Current Command: ", motor.get_current()])
        time.sleep(1/sample_freq)
        # if abs(motor.get_current()) >= 4:
        #             print("Velocity Control Fault. Error with Command")
        #             raise Exception("Velocity Control Fault. Error with Command")
    print("Current Successfully Ramped\n\n")
    time.sleep(1)
    # time.sleep(5)

def hitVelTargets(vel_targets, i_targets, Vel_Motor, Curr_Motor):

    global res_torque, vel_RPM

    # Vel_Motor.set_mode(1) # Set to Velocity Mode
    # time.sleep(1)
    # Curr_Motor.set_mode(0) # Set to Current Mode
    # time.sleep(1)

    for vel_RPM in vel_targets:

        ramp_vel(Vel_Motor,vel_RPM,2,500)
        # Vel_Motor.set_velocity(vel_RPM,units = 1)

        vel_now = readData(0)[1 if curr_motor==1 else 0]
        while abs(vel_now - vel_RPM) > 2: # allow velocity to ramp up
            vel_now = readData(0)[1 if curr_motor==1 else 0]
        print('Hit target', str(vel_RPM), 'RPM')

        for current in i_targets:
            hitCurrTarget(current, 3, Curr_Motor)

        Vel_Motor.set_velocity(0, units = 1)

        vel_now = readData(0)[1 if curr_motor==1 else 0]
        while abs(vel_now - 0) > 2: # allow velocity to ramp down
            vel_now = readData(0)[1 if curr_motor==1 else 0]

        Vel_Motor.set_current(0)

        print("Sleeping between tests.")
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

    sort_indexes = np.argsort(np.abs(vel_targets))
    # print(sort_indexes[::-1])
    final_targets = np.zeros(np.size(sort_indexes))
    i = 0
    for s in sort_indexes:
        final_targets[i] = vel_targets[s]
        i += 1

    return final_targets

def getCurrTargets(i_range, n_targets):

    i_targets = []

    for i in range(n_targets):
        i_span = i_range[1] - i_range[0]
        i_step = i_span/(n_targets - 1)
        i_targets.append(i_range[0] + i*i_step)

    # ordered_targets =[]
    # neg_targets_mA = []
    # pos_targets_mA = []
    # zero_target_mA = []
    # for val in i_targets_mA:
    #     if val < 0:
    #         neg_targets_mA.append(val)
    #     elif val > 0:
    #         pos_targets_mA.append(val)
    #     else:
    #         zero_target_mA.append(val)
    # target_lists = [neg_targets_mA, zero_target_mA, pos_targets_mA]
    # for targets in target_lists:
    #     for i in range(int(len(targets)//2)):
    #         ordered_targets.append(targets[i])
    #         ordered_targets.append(targets[-i-1])
    #     if len(targets)%2 == 1:
    #         ordered_targets.append(targets[int(len(targets)//2)])

    sort_indexes = np.argsort(np.abs(i_targets))
    # print(sort_indexes[::-1])
    final_targets = np.zeros(np.size(sort_indexes))
    i = 0
    for s in sort_indexes:
        final_targets[i] = i_targets[s]
        i += 1

    return final_targets

def main():

    global t0, res_torque, curr_motor, MN1005, RI8523, csv_writer

    RI8523_drive = True

    MN1005 = Motor(node_id=127)
    if RI8523_drive:
        MN1005.set_mode(mode = 0)
    else:
        MN1005.set_mode(mode = 1)
    time.sleep(2)
    RI8523 = Motor(node_id=69)
    if RI8523_drive:
        RI8523.set_mode(mode = 1)
    else:
        RI8523.set_mode(mode = 0)
    time.sleep(2)



    MN1005.go_operational()
    RI8523.go_operational()

    
    
        
    try:


        i_range = [-10, 10] # A
        i_increment = 2  #A
        n_i_targets = int(abs(i_range[0])/i_increment + abs(i_range[1])/i_increment + 1)
        vel_range = [-100, 100] # RPM
        vel_increment = 100 # RPM
        n_vel_targets = int(abs(vel_range[0])/vel_increment + abs(vel_range[1])/vel_increment + 1)

        i_targets = getCurrTargets(i_range, n_i_targets)
        vel_targets = [-100, 100] #getVelTargets(vel_range, n_vel_targets)
        
        print("Current Targets:", i_targets)
        print("Velocity Targets:", vel_targets)

        MN1005.set_current(0)
        time.sleep(1)
        RI8523.set_current(0)
        time.sleep(1)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()


        if RI8523_drive:
            curr_motor = 1 # 1: MN1005 current control, RI8523 motor velocity control
            print("Performing Driving Test")
            with open("data/efficiency_test/driving/efficiency_RI8523_velocity_Driving_%s.csv"% csv_timestamp,'w') as fd:
                csv_writer = csv.writer(fd)
                csv_writer.writerow(csv_header)
                hitVelTargets(vel_targets, i_targets, Vel_Motor=RI8523, Curr_Motor=MN1005)
        else:
            curr_motor = 2 # 2: RI8523 motor current control, MN1005 velocity control
            print("Performing Driven Test")
            with open("data/efficiency_test/driven/efficiency_RI8523_current_Driven_%s.csv"% csv_timestamp,'w') as fd:
                csv_writer = csv.writer(fd)
                csv_writer.writerow(csv_header)
                hitVelTargets(vel_targets[0:], i_targets, Vel_Motor=MN1005, Curr_Motor=RI8523)

        MN1005.set_current(0)
        time.sleep(1)
        RI8523.set_current(0)

    except:

        if curr_motor == 1:
            MN1005.set_current(0)
            time.sleep(2)
            RI8523.set_current(0)
            time.sleep(2)
        elif curr_motor == 2:
            RI8523.set_current(0)
            time.sleep(2)
            MN1005.set_current(0)

        MN1005.disconnect()
        RI8523.disconnect()

        traceback.print_exception(*sys.exc_info())
    finally:
        MN1005.set_current(0)
        time.sleep(2)
        RI8523.set_current(0)
        time.sleep(2)


if __name__ == '__main__':

    global csv_header, csv_timestamp, adc
    csv_timestamp = datetime.now().strftime("%Y-%b-%d-%H%M%S")
    csv_header = ["t", "curr_motor", "curr_target_A", "vel_target_RPM", "on_target",\
                  "vel_MN1005_RPM", "vel_RI8523_RPM", "i_q_MN1005_A", "i_q_RI8523_A", "futek_torque_Nm"]
    with Hoop18NmFutek() as adc:
        main()