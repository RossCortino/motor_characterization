from datetime import datetime
import numpy as np
import csv
import sys
from scipy.signal import butter, lfilter
sys.path.append('/home/pi/python-can-wrapper')
from Motor import Motor
from opensourceleg.tools.utilities import SoftRealtimeLoop

def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def gen_perturbation(mag, fs, duration, cutoff, order=5):

    raw = np.random.uniform(-mag, mag, fs*duration)
    pert = butter_lowpass_filter(raw, cutoff, fs, order=order)

    return pert

def control_loop(csv_writer):

    fs = 750 # [Hz]
    duration = 30 # [sec]
    mag = 3.3 # [A]
    cutoff = 350 # [Hz]

    pert = gen_perturbation(mag, fs, duration, cutoff, order=10)

    M = Motor(node_id=126, object_dic='/home/pi/python-can-wrapper/GoldSoloTwitter.eds', config_file='/home/pi/python-can-wrapper/config.yaml', callback=False)
    M.set_mode(mode=0)

    loop = SoftRealtimeLoop(dt=1.0/fs, report=True, fade=0.1)

    try:
        print('Loop starting.')
        i = 0
        for t in loop:
            if i >= len(pert):
                break
            curr_comm = pert[i]
            M.set_current(curr_comm)
            curr_act = M.get_current()
            csv_writer.writerow([t, curr_comm, curr_act])
            i += 1
 
    except Exception as error:
        print(error)
        M.set_current(0)
    
    finally:
        print('Loop finished. Exiting.')
        M.set_current(0)
        M.disconnect()

if __name__=='__main__':
    with open("../data/MN1005_controlFreqResp_current_3o3A_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t", "curr_comm_A", "curr_act_A"])
        control_loop(csv_writer)