""" A reusable header that loads the Dephy libraries and names the useful data fields """

import os, sys
import time
import csv
# from GracefulDeathLoop import GracefulDeathLoop # helps with the shutdown process
import traceback
import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np


class ADC(object):
    def __init__(self, csv_file_name=None, gain=0.6666666666666666):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c, data_rate=860, gain=gain)
        self.chan = AnalogIn(self.ads, ADS.P0)
        self.save_csv = not (csv_file_name is None)
        self.csv_file_name = csv_file_name
        self.csv_file = None
        self.csv_writer = None
        self.volts = -42.0 # error code

    def __enter__(self):
        if self.save_csv:
            with open(self.csv_file_name,'w') as fd:
                writer = csv.writer(fd)
                writer.writerow(["pi_time", "voltage", "test_duration"])
            self.csv_file = open(self.csv_file_name,'a').__enter__()
            self.csv_writer = csv.writer(self.csv_file)
        return self

    def __exit__(self, etype, value, tb):
        """ Closes the file properly """
        if self.save_csv:
            self.csv_file.__exit__(etype, value, tb)
        if not (etype is None):
            traceback.print_exception(etype, value, tb)


    def update(self):
        t0=time.time()
        self.volts = self.chan.voltage
        dur = time.time()-t0
        if self.save_csv:
            self.csv_writer.writerow([time.time(),self.volts, dur])
        return self.volts

# Offers conversions to output torque and position
class Hoop18NmFutek(ADC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_torque(self):
        return (self.volts-2.5)*((18./5.)*2.) 
        # 40 = 100 Nm / 5 V * 2