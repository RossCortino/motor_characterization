from sys import path
from os import getcwd
path.append("/home/pi/hoop-exo/python-can-wrapper")
from Motor import Motor
import time
import csv

def main(csv_writer):
    MN1005 = Motor(node_id=126, callback=False)

    try:
        t0 = time.time()
        while True:
            t = time.time() - t0
            i = MN1005.get_current()
            v = MN1005.get_velocity(0)
            csv_writer.writerow([t, v, i])
    except:
        MN1005.disconnect()

if __name__=='__main__':
    with open("../data/testCANcomm.csv",'w') as fd:
            csv_writer = csv.writer(fd)
            csv_writer.writerow(["t", "velocity_m_s", "current_A"])
            main(csv_writer)