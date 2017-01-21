import numpy as np
import matplotlib.pyplot as plt
import SWG_Altisat as Altisat
import SWG_PyPM as PyPM

coord = PyPM.Lat_Lon(-16.14,-45.075)

rec = Altisat.read_sral_wf('/home/philippe/Documentos/Alti-SF/Sentinel-3/',323,coord,10000.0,9)
print len(rec), 'Records remain'
for i in range(20,40):
    print rec[i].alt, rec[i].lat, rec[i].lon, rec[i].ice1, rec[i].geoid, rec[i].ayear
##    plt.figure(i)
##    plt.plot(rec[i].wf, 'ko-')
plt.show()

    
    



