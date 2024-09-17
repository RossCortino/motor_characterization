# Call this if "Failed to transmit: [Errno 105] No buffer space available"
# sudo ifconfig can0 txqueuelen 1000
import sys
import time
from math import sin, pi
from GrayDemoCommon import * # reausable script header
from datetime import datetime
sys.path.append('/home/pi/python-can-wrapper/')
from Motor import Motor
# from pyCANWrapper import PyCANWrapper


def readData(on_target):

    t = time.time() - t0

    i_RI8523 = RI8523.get_current() # A
    pos_RI8523 = RI8523.get_position(units = 1) #deg

    adc.update()
    futek_torque = adc.get_torque()-res_torque
    csv_writer.writerow([t, motor_tested, RI8523.get_current_command(), on_target,\
                            pos_RI8523, i_RI8523, futek_torque])

    return pos_RI8523, i_RI8523, futek_torque

def readLoop(t_loop, on_target):
    
    t0_loop = time.time()
    while time.time() - t0_loop < t_loop:
        readData(on_target)

    return

def hitTarget(i_target, hold_t, Motor_test):
    # i_target_mA = 0
    Motor_test.set_current(i_target)
    # read_check = readData(0)
    i_now = Motor_test.get_current()
    while abs(i_now) - abs(i_target) > .01:
        i_now = readData(0)[1]
        # print(i_now)
    time.sleep(.5)
    print('Hit target', str(i_target), 'A')
    target_torque = readData(1)[-1]
    print(f'Futek Torque: {target_torque:.3f}')
    readLoop(hold_t, 1)

    Motor_test.set_current(0)

    i_now = readData(0)[1]
    while abs(i_now - 0) > .01:
        i_now = readData(0)[1]

    print('Cooling down...')
    readLoop(2, 0)

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

    RI8523 = Motor(node_id=69, callback=False )
    RI8523.set_mode(mode = 0)

    motor_tested = "RI8523"

        
    try:
        i_range = [-13, 13] # A
        i_increment = 1# A
        n_targets = int(abs(i_range[0])/i_increment + abs(i_range[1])/i_increment + 1)

        i_targets = getTargets(i_range, n_targets) 
        print("Current Targets:", i_targets)

        assert (abs(i_range[0]) <= 10) and (abs(i_range[1]) <= 10)

        RI8523.set_current(0)
        time.sleep(0.5)

        adc.update()
        res_torque = adc.get_torque()
        t0 = time.time()


        for current in i_targets:
                hitTarget(current, 3, RI8523)

                RI8523.set_current(0)
                print('Setting current to zero...')

        RI8523.disconnect()

    except:

        RI8523.set_current(0)
        readLoop(2, 0)
        
        RI8523.disconnect()

        traceback.print_exception(*sys.exc_info())

if __name__ == '__main__':

    global csv_writer, adc
    num_trials = 5
    sleep_time = 300
    for i in range(num_trials):
        with open("data/current_test/RI8523_current_torque_locked_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
            csv_writer = csv.writer(fd)
            csv_writer.writerow(["t", "motor_tested", "curr_target_mA", "on_target",\
                                "i_q_RI8523_mA", "futek_torque_Nm"])
            with Hoop18NmFutek() as adc:
                main()
        print("\n\n\nMotors Resting between Trials...\n\n\n")
        time.sleep(sleep_time)