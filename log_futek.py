from GrayDemoCommon import * # reausable script header
import time
from datetime import datetime

def main(adc, csv_writer):
    adc.update()
    res_t = adc.get_torque()
    t0 = time.time()
    t = time.time() - t0
    while t < 300:
        t = time.time() - t0
        adc.update()
        torque = adc.get_torque() - res_t
        csv_writer.writerow([t, torque])

if __name__ == '__main__':

    with open("data/futek_MN1005cogging_1RPM_%s.csv"% datetime.now().strftime("%Y-%b-%d-%H%M%S"),'w') as fd:
        csv_writer = csv.writer(fd)
        csv_writer.writerow(["t_sec", "torque_Nm"])
        with Hoop18NmFutek() as adc:
            main(adc, csv_writer)