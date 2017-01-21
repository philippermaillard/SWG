import numpy as np
import sys
#!/usr/bin/python(
from math import cos, sin, acos
import matplotlib.pyplot as plt
from pylab import *
import datetime as dt
from netCDF4 import Dataset
from Tkinter import *
import SWG_GUI


try:
    fparam = open("param.txt", "r")
    s1 = fparam.readline()
    s2 = s1.split(' ')
    d_path = s2[0]
    d_tabname = s2[1]
    d_txtname = s2[2]
    d_bilpath = s2[3]
    d_shapename = s2[4]
    fparam.close()
except IOError:
    d_path = ""
    d_tabname = ""
    d_txtname = ""
    d_bilpath = ""
    d_shapename = ""

#if __name__ == "__main__":
flag = 1
app = SWG_GUI.Sapp_tk(None,d_path,d_tabname,d_txtname,d_bilpath,d_shapename)
app.title('SWG - Satellite Water Gauging')
if flag == 0:
    print app.path, app.tabname, app.txtname, app.bilpath, app.year
app.mainloop()
fparam = open("param.txt", "w")
fparam.write(app.path+' ')
fparam.write(app.tabname+' ')
fparam.write(app.txtname+' ')
fparam.write(app.bilpath+' ')
fparam.write(app.shapename)
fparam.close()


