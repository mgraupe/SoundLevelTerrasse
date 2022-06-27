import usb.core
#import logroll
import datetime
import time


# Inspired by ebswift, https://www.ebswift.com/reverse-engineering-spl-usb.html

# The Wensn WS1381 answers these bRequests
# 1 seems to be constant - array of 2 bytes returned
# 2 readMode - array of 1 byte returned
# 3 setMode - array of 1 byte returned
# 4 read SPL - array of 2 bytes returned
# 82 array of 4 bytes returned

class wensn:
    def __init__(self):
        self.ranges = ["30-80", "40-90", "50-100", "60-110", "70-120", "80-130", "30-130"]
        self.speeds = ["fast", "slow"]
        self.weights = ["A", "C"]
        self.maxModes = ["instant", "max"]


        self.dev = usb.core.find(idVendor=0x16c0, idProduct=0x5dc)
        assert self.dev is not None
        print(self.dev)
        #return self.dev

        self.peak = 0
    def readBRequest(self,bRequest):
        ret = self.dev.ctrl_transfer(0xC0, bRequest, 0, 10, 200)
        print(ret),
        for elem in ret:
            print(format(elem, '#010b')),
        print

    def readMode(self):
        ret = self.dev.ctrl_transfer(0xC0, 2, 0, 10, 200)
        #print(ret)
        #print(format(ret[0], '#010b'))

        rangeN = (ret[0]&7) # bits 1,2,3 in ret[0] return rangeN from 0 to 6
        weightN = (ret[0]&8)>>3 # bit 3 in ret[0] returns weight
        speedN = (ret[0]&16)>>4 # bit 4 in ret[0] returns speed
        maxModeN = (ret[0]&32)>>5 # bit 5 in ret[0] returns maxMode

        return(self.ranges[rangeN], self.weights[weightN],
               self.speeds[speedN], self.maxModes[maxModeN])

    def setMode(self, range="30-80", speed="slow", weight="A", maxMode="instant"):
        rangeN = self.ranges[0:4].index(range)
        # For rangeN, setting over USB supports only 2 bits of range,
        #   although 7 values (0 to 6) can be set with buttons on unit.
        speedN = self.speeds.index(speed)
        weightN = self.weights.index(weight)
        maxModeN = self.maxModes.index(maxMode)

        print("setMode: range:%s weight:%s speed:%s maxMode:%s" %
              (range, weight, speed, maxMode))
        #wvalue = rangeN | weightN<<3 | speedN<<4 | maxModeN<<5
        wvalue = (rangeN&3) | (weightN&1)<<3 | (speedN&1)<<4 | (maxModeN&1)<<5
        # Function of bits 6 and 7 is unknown (nothing?)

        self.dev.ctrl_transfer(0xC0, 3, wvalue, 0, 200)


    def readSPL(self):
        #global peak

        ret = self.dev.ctrl_transfer(0xC0, 4, 0, 10, 200) # wvalue (3rd arg) is ignored
        #print(ret)
        #print(format(ret[1], '#010b'))

        rangeN = (ret[1]&28)>>2 # bits 2,3,4 in ret[1] return rangeN from 0 to 6
        weightN = (ret[1]&32)>>5 # bit 5 in ret[1] return weightN
        speedN = (ret[1]&64)>>6 # bit 6 in ret[1] return speedN
        # bit 7 seems to alternate every 1 second?

        dB = (ret[0] + ((ret[1] & 3) * 256)) * 0.1 + 30
        if dB > self.peak:
            self.peak = dB
        return(dB, self.ranges[rangeN], self.weights[weightN], self.speeds[speedN])

    def readSPLMultipleTimes(self,nMeasurements):

        for i in range(nMeasurements):
            now = datetime.datetime.now()
            # roll over to a new log whenever the filename changes - in this case, every hour.
            #log.open_or_reopen(now.strftime('%Y-%m-%d-%H-%M.log'))
            dB, range, weight, speed = self.readSPL()
            print("%.2f,%s,%s,%s/%s,%s" % (dB, weight, speed, i+1,nMeasurements, now.strftime('%Y,%m,%d,%H,%M,%S')))
            #print("%.2f,%s,%s,%s" % (dB, weight, speed, now.strftime('%Y,%m,%d,%H,%M,%S')))

            #log.fp.flush()
            time.sleep(1)

def main():

    wsn = wensn()
    wsn.setMode()
    wsn.readSPLMultipleTimes(10)


if __name__=="__main__":
    main()