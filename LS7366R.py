#!/usr/bin/python

#Python library to interface with the chip LS7366R for the Raspberry Pi
#Written by Federico Bolanos
#Last Edit: February 8th 2016
#Reason: Refactoring some names

from GrayDemoCommon import * # reausable script header
from read_futek import res_torque

import spidev
import csv
from time import sleep, time


# Usage: import LS7366R then create an object by calling enc = LS7366R(CSX, CLK, BTMD)
# CSX is either CE1 (1) or CE2 (2),
# CLK is the speed,
# BTMD is the bytemode 1-4 the resolution of your counter,
# CTMD is the countmode for index handling either none (0) LCNTR (1) or RCNTR (2).
# example: lever.Encoder(1, 1000000, 4)
# These are the values I normally use.

class LS7366R():

    #-------------------------------------------
    # Constants

    #   Commands
    CLEAR_COUNTER = 0x20 # 00 100 000
    CLEAR_STATUS = 0x30 # 00 110 000
    READ_COUNTER = 0x60 # 01 100 000
    READ_STATUS = 0x70 # 01 110 000
    WRITE_MODE0 = 0x88 # 10 001 000
    WRITE_MODE1 = 0x90 # 10 010 000

    WRITE_DTR = 0x98 # 10 011 000
    READ_DTR = 0x58 # 01 011 000

    #   Modes
    FOURX_COUNT = 0x03 # 0 0 00 00 11
    FOURX_COUNT_LCNTR = 0x13 # 0 0 01 00 11
    FOURX_COUNT_RCNTR = 0x23 # 0 0 10 00 11
    # FOURX_COUNT_RCNTR = 0x63 # 0 1 10 00 11

    COUNT_MODE = [FOURX_COUNT, FOURX_COUNT_LCNTR, FOURX_COUNT_RCNTR]

    FOURBYTE_COUNTER = 0x00
    THREEBYTE_COUNTER = 0x01
    TWOBYTE_COUNTER = 0x02
    ONEBYTE_COUNTER = 0x03

    BYTE_MODE = [ONEBYTE_COUNTER, TWOBYTE_COUNTER, THREEBYTE_COUNTER, FOURBYTE_COUNTER]

    #   Values
    max_val = 4294967295
    
    # Global Variables

    counterSize = 4 #Default 4
    
    #----------------------------------------------
    # Constructor

    def __init__(self, CSX, CLK, BTMD, CTMD = 0):
        self.counterSize = BTMD #Sets the byte mode that will be used
        self.CSX = CSX #chip select line


        self.spi = spidev.SpiDev() #Initialize object
        self.spi.open(0, CSX) #Which CS line will be used
        self.spi.max_speed_hz = CLK #Speed of clk (modifies speed transaction) 

        #Init the Encoder
        #print 'Clearing Encoder CS%s\'s Count...\t' % (str(CSX)), self.clearCounter()
        #print 'Clearing Encoder CS%s\'s Status..\t' % (str(CSX)), self.clearStatus()
        print("Initializing encoder at slave %s..." % str(CSX))

        self.spi.xfer2([self.WRITE_MODE0, self.COUNT_MODE[CTMD]])
        
        sleep(.1) #Rest
        
        self.spi.xfer2([self.WRITE_MODE1, self.BYTE_MODE[self.counterSize-1]])

        # DTR_value = [self.CENTER_VAL]
        # for i in range(self.counterSize):
        #     DTR_value.append(0)

        # self.CENTER_VAL = [0x98]
        # self.CENTER_VAL.append(0) # 38,912
        # writeTransaction = [self.WRITE_DTR]
        # writeTransaction.append(0x98)
        # writeTransaction.append(0)
        # self.spi.xfer2(writeTransaction)
        # readTransaction = [self.READ_DTR]
        # for i in range(self.counterSize):
        #     readTransaction.append(0)
        # dataReg = self.spi.xfer2(readTransaction)
        # dataRegValue = 0
        # for i in range(self.counterSize):
        #     dataRegValue = (dataRegValue << 8) + dataReg[i+1]
        # print("Data register: ", dataReg, " | Value: ", dataRegValue)

    def close(self):
        self.spi.close()

    def clearCounter(self):
        self.spi.xfer2([self.CLEAR_COUNTER])

        return '[DONE]'

    def clearStatus(self):
        self.spi.xfer2([self.CLEAR_STATUS])

        return '[DONE]'

    def readCounter(self):
        try:
            # self.spi.open(0, self.CSX) # Switch CS line
            readTransaction = [self.READ_COUNTER]
            for i in range(self.counterSize):
                readTransaction.append(0)
            
            data = self.spi.xfer2(readTransaction)

            EncoderCount = 0
            for i in range(self.counterSize):
                EncoderCount = (EncoderCount << 8) + data[i+1]

            return EncoderCount

            # if data[1] != 255:    
            #     return EncoderCount
            # else:
            #     return (EncoderCount - (self.max_val+1))  
        except:
            print('Motor encoder read error...')
            print("Encoder count: ", EncoderCount)

    def readStatus(self):
        data = self.spi.xfer2([self.READ_STATUS, 0xFF])
        
        return data[1]


if __name__ == "__main__":
    from time import sleep
    
    encoder_us = LS7366R(2, 1000000, 4, 0)
    encoder_s = LS7366R(1, 1000000, 4, 0)
    encoder_us.clearCounter()
    encoder_s.clearCounter()
    sleep(0.1)

    record = 1

    if record:

        with Hoop18NmFutek() as adc:
            with open("../data/encCompareTorque_60RPM_12A.csv", "w") as fd:
                try:
                    csv_writer = csv.writer(fd)
                    csv_writer.writerow(["t", "pos_unsplit_cts", "pos_split_cts", "T_futek_Nm"])

                    print('Sensing residual torque...')
                    res_T = res_torque(adc, 1)
                    print(f'residual torque = {res_T:.3f}')

                    t0 = time()
                    while True:
                        t = time() - t0
                        count_us = encoder_us.readCounter()
                        count_s = encoder_s.readCounter()
                        adc.update()
                        torque = adc.get_torque() - res_T
                        csv_writer.writerow([t, count_us, count_s, torque])
                        if t % 0.5 < 0.002:
                            print("Un-split count: %d | Split count: %d | Torque: %f" % (count_us, count_s, torque))
                        sleep(0.001)
                except KeyboardInterrupt:
                    encoder_us.close()
                    encoder_s.close()
                    print("All done, bye bois.")

    else:

        try:
            while True:
                count_us = encoder_us.readCounter()
                count_s = encoder_s.readCounter()
                print("Un-split count: %d | Split count: %d" % (count_us, count_s))
                sleep(0.2)
        except KeyboardInterrupt:
            encoder_us.close()
            encoder_s.close()
            print("All done, bye bois.")