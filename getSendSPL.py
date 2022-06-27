import sys
import os
from datetime import datetime
import numpy as np
import time
from ISStreamer.Streamer import Streamer

import wensn

import ITaccess as ITA
SENSOR_LOCATION_NAME = "My Terrace"

def main(saveData,now,scriptWD):

    wsn = wensn.wensn()
    ret = wsn.measureSPLForSpecificTime(60*10)

    if saveData:
        dFile = open("%s/data/terraceSPL_%s.data" % (scriptWD, now.strftime("%Y-%m")), "a")
        dFile.write("%s %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), ret['mean'],ret['max'],ret['min'],ret['std'],ret['25%'],ret['50%'],ret['75%']))
        dFile.close()
        print('data saved to file')

        # send data to initial state
        streamer = Streamer(bucket_name=ITA.BUCKET_NAME, bucket_key=ITA.BUCKET_KEY, access_key=ITA.ACCESS_KEY)
        #print(np.round(humidity, 2),np.round(pressure, 2),temperature,temp_c[0][3],temp_c[1][3],np.round(currentH20Content, 3),np.round(lux,4))
        streamer.log(SENSOR_LOCATION_NAME + " SPL mean (dB)", np.float(np.round(ret['mean'], 2)))
        streamer.log(SENSOR_LOCATION_NAME + " SPL std (dB)", np.round(ret['std'], 2))
        streamer.log(SENSOR_LOCATION_NAME + " SPL min (dB)", np.round(ret['min'], 2))
        streamer.log(SENSOR_LOCATION_NAME + " SPL max (dB)", np.round(ret['max'], 2))
        streamer.log(SENSOR_LOCATION_NAME + " SPL 25% (dB)", np.round(ret['25%'], 2))
        streamer.log(SENSOR_LOCATION_NAME + " SPL 50% (dB)", np.round(ret['50%'], 2))
        streamer.log(SENSOR_LOCATION_NAME + " SPL 75% (dB)", np.round(ret['75%'], 2))
        streamer.flush()
        print('Upload code finished')


if __name__=="__main__":
    try:
        sys.argv[1]
    except:
        saveData = False
    else:
        if sys.argv[1] == 'save':
            saveData = True
            print('Data will be saved.')
            print(saveData)
    now = datetime.now()
    print('run at %s' % now.strftime("%Y-%m-%d %H:%M:%S"))
    scriptWD = os.path.dirname(os.path.realpath(__file__))
    main(saveData,now,scriptWD)