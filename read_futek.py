from GrayDemoCommon import * # reausable script header
import time
import csv

def res_torque(adc, duration):
    
    t_start = time.time()
    t = time.time() - t_start
    torques = []
    while t < duration:
        adc.update()
        torques.append(adc.get_torque())
        t = time.time() - t_start
    res_T = sum(torques)/len(torques)

    return res_T

def main(adc, csv_writer):
    
    print('Sensing residual torque...')
    res_T = res_torque(adc, 1)
    print(f'residual torque = {res_T:.3f}')

    t0 = time.time()
    t = time.time() - t0
    while t < 300:
        t = time.time() - t0
        adc.update()

        # csv_writer.writerow([t, adc.get_torque() - res_T])
        # # time.sleep(0.001)

        torque = adc.get_torque() - res_T
        print(f'\rtorque = {torque:.3f}', end='')
        time.sleep(0.2)

if __name__ == '__main__':
    with Hoop18NmFutek() as adc:

        main(adc, None)

        # name = "dynamicKt_split_RLMsplit_120RPM_10A_fromstatic"
        # with open("../data/" + name + ".csv",'w') as fd:
        #     csv_writer = csv.writer(fd)
        #     csv_writer.writerow(["t", "futek_torque_Nm"])
        #     main(adc, csv_writer)