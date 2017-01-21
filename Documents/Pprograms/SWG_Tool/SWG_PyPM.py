import sys
import datetime as dt
import calendar
from pylab import *
import datetime as dt
import copy
import struct
import numpy as np
from math import cos, sin, acos, atan, sqrt, pi
import Tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkFileDialog
import array
import shapefile
import glob

class Vas:
    def __init__(self,cycle,hdate,cal,nh,lat,lon,h,d2w,wh,alt,m_lat,m_lon):
        self.cycle = cycle
        self.lat = lat
        self.lon = lon
        self.cal = cal
        self.nh = nh
        self.h = h
        self.hdate = hdate
        self.d2w = d2w
        self.wh = wh
        self.alt = alt
        self.m_lat = m_lat
        self.m_lon = m_lon

class Lat_Lon:
    def __init__(self,lat,lon):
        self.lat = lat
        self.lon = lon
        
class XYZ:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

class Light:
    def __init__(self,zenith,azimuth):
        self.zenith = zenith
        self.azimuth = azimuth

class Class_Vector:
    def __init__(self,name,variables):
        self.name = name
        self.variables = variables
        
class Polig:# uma classe que contem todos os vertices de cada poligono
    def __init__(self,v):
        self.v = v

class Vertice:# uma classe que contem vertices como pares de pontos
    def __init__(self,x1,y1,x2,y2,tag):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.tag = tag

class Point:# uma classe de pontos simples
    def __init__(self,x,y):
        self.x = x
        self.y = y
        
class VHS:# uma class para conter as informacoes iniciais de uma VHS
    def __init__(self,lat,lon,track,dist):
        self.lat = lat
        self.lon = lon
        self.track = track
        self.dist = dist

# *** BIL IMAGE HEADER CLASS *************************************************
class Image_Header:
    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.nbands = 1
        self.nbits = 8
        self.ulx = 0
        self.uly = 0
        self.xdim = 1
        self.ydim = 1
        self.pixtype = 'UCHAR'
    def show(self):
        print 'rows:', self.nrows, '\ncols:', self.ncols, '\nbands:', self.nbands
    def read(self, nome):
        try:
            f = open(nome,'rt')
        except IOError:
            return self
        t = f.readline()
        while t != '':
            t2 = t.split()
            if t2[0]=="NCOLS" or t2[0]=="ncols":
                self.ncols = int(t2[1])
            elif t2[0]=="NROWS" or t2[0]=="nrows":
                self.nrows = int(t2[1])
            elif t2[0]=="NBITS" or t2[0]=="nbits":
                self.nbits = int(t2[1])
            elif t2[0]=="NBANDS" or t2[0]=="nbands":
                self.nbands = int(t2[1])
            elif t2[0]=="ULXMAP" or t2[0]=="ulxmap":
                self.ulx = float(t2[1])
            elif t2[0]=="ULYMAP" or t2[0]=="ulymap":
                self.uly = float(t2[1])
            elif t2[0]=="XDIM" or t2[0]=="xdim":
                self.xdim = float(t2[1])
            elif t2[0]=="YDIM" or t2[0]=="ydim":
                self.ydim = float(t2[1])
            elif t2[0]=="PIXELTYPE" or t2[0]=="pixeltype":
                self.pixtype = t2[1]
            t = f.readline()
        f.close()
        return self
    def write(self,nome,hdr):
        try:
            f1 = open(nome+'.hdr','wt')
        except IOError:
            print 'Problem opening file'
            sys.exit()
            
        f1.write('layout bil' + '\n')
        f1.write('pixeltype unsignedint' + '\n')
        f1.write('byteorder I' + '\n')
        f1.write('nbits ' + str(hdr.nbits) + '\n')
        f1.write('xdim ' + str(hdr.xdim) + '\n')
        f1.write('ydim ' + str(hdr.ydim) + '\n')
        f1.write('ncols ' + str(hdr.ncols) + '\n')
        f1.write('nrows ' + str(hdr.nrows) + '\n')
        f1.write('nbands ' + str(hdr.nbands) + '\n')
        f1.write('mapunits METERS' + '\n')
        f1.write('ulxmap ' + str(hdr.ulx) + '\n')
        f1.write('ulymap ' + str(hdr.uly) + '\n')
        f1.close()
        return 1

# *** BIL IMAGE CLASS *****************************************************
class Imagem_Bil:
    def __init__(self, nome, header):
        self.nome = nome
        self.header = header
    def read(self, header):
        try:
            f = open(self.nome,'rb')
        except IOError:
          print "There was an error reading file ", self.nome
          sys.exit()
        if header.nbits == 16 and header.pixtype == 'SIGNEDINT':
            fmt = 'H'
        elif header.nbits == 16 and header.pixtype == 'UNSIGNEDINT':
            fmt = 'h'
        else:
            fmt = 'B'
        matriz=np.zeros((header.nrows,header.ncols,header.nbands))
        for i in range(0,header.nrows):
            for k in range(0,header.nbands):
                dados = f.read(header.ncols*(header.nbits/8))
                dados = struct.unpack(fmt*header.ncols,dados)
                for j in range(0,header.ncols):
                    matriz[i,j,k] = dados[j]
        f.close()
        return matriz

    def read_bloc(self, header, ul, lr):
        try:
            f = open(self.nome,'rb')
        except IOError:
          print "There was an error reading file ", self.nome
          sys.exit()
        if header.nbits == 16 and header.pixtype == 'SIGNEDINT':
            fmt = 'H'
        elif header.nbits == 16 and header.pixtype == 'UNSIGNEDINT':
            fmt = 'h'
        else:
            fmt = 'B'
        matriz=np.zeros((abs(lr.y-ul.y),abs(lr.x-ul.x)))
        for i in range(0,lr.y):
            dados = f.read(header.ncols*(header.nbits/8))
            dados = struct.unpack(fmt*header.ncols,dados)
            if i>=ul.y:
                for j in range(ul.x,lr.x):
                    matriz[i-ul.y,j-ul.x] = dados[j]
        f.close()
        return matriz

    def write(self,nome,matriz,header):
        try:
            f = open(nome+'.bil','wb')
        except IOError:
          print "There was an error reading file ", in_image_bin
          sys.exit()
        if header.nbits == 16 and header.pixtype == 'SIGNEDINT':
            fmt = 'H'
        elif header.nbits == 16 and header.pixtype == 'UNSIGNEDINT':
            fmt = 'h'
        else:
            fmt = 'B'
        for i in range(0,header.nrows):
            for k in range(0,header.nbands):
                pacmat = struct.pack(fmt*header.ncols, *matriz[i,:,k])
                f.write(pacmat)
        f.close()

# ________________________________________________________________________________

# *** EXTRACT PROFILE VALUES *****************************************************
def get_profile(dempath, c1, c2):
    f = 0.00000001
    latpart = '0'+str(abs(int(c1.lat+f))+1)
    if abs(c1.lat)+1 > 10:
        latpart = str(abs(int(c1.lat+f))+1)
    lonpart = '00'+str(abs(int(c1.lon+f))+1)
    if abs(c1.lon)+1 > 10:
        lonpart = '0'+str(abs(int(c1.lon+f))+1)
    if abs(c1.lon)+1 > 100:
        lonpart = str(abs(int(c1.lon+f))+1)

    if c1.lat < 0:
        latpart = 's'+latpart
    else:
        latpart = 'n'+latpart
    if c1.lon < 0:
        lonpart = 'w'+lonpart
    else:
        lonpart = 'e'+lonpart
    demname = dempath+'/'+latpart+'_'+lonpart+'*.hdr'
    print latpart, lonpart, demname
# ********************************************************
    dem = glob.glob(demname)
    imh = Image_Header()
    imh.read(dem[0])
    ulx = int((c1.lon-imh.ulx)/imh.xdim)
    uly = int((imh.uly-c1.lat)/imh.ydim)
    lrx = int((c2.lon-imh.ulx)/imh.xdim)+1
    lry = int((imh.uly-c2.lat)/imh.ydim)+1
    if c1.lon > c2.lon:
        ulx = int((c2.lon-imh.ulx)/imh.xdim)
        lrx = int((c1.lon-imh.ulx)/imh.xdim)+1
    if c1.lat < c2.lat:
        uly = int((imh.uly-c2.lat)/imh.ydim)
        lry = int((imh.uly-c1.lat)/imh.ydim)+1
    ul = Point(ulx, uly)
    lr = Point(lrx, lry)

    dembin = dem[0].replace('.hdr','.bil')
    demdata = Imagem_Bil(dembin,imh).read_bloc(imh,ul,lr)
    [rows,cols] = shape(demdata)
    if c1.lon - c2.lon != 0.0:
        m = (float(c1.lat - c2.lat) / float(c1.lon - c2.lon))*(-1.0)
    else:
        m = 10000000.0
    prof = []
    if abs(m)<1.0:
        for j in range(0,cols):
            i = int((m*float(j)))
            prof.append(demdata[i,j])
    else:
        for i in range(rows-1,0,-1):
            j = int((float(i)/m))
            prof.append(demdata[i,j])
    return prof

# _____________________________________________________________________________
# *** SPLIT COORDINATES IN 1 DEGREE TILES *************************************
def split_profile(coor1, coor2, dempath):
    if int(coor1.lat) - int(coor2.lat) == 0 and int(coor1.lon) - int(coor2.lon) == 0:
        prolat = []
        prolon = []
        prolat.append(coor2.lat)
        prolon.append(coor2.lon)
        prolat.append(coor1.lat)
        prolon.append(coor1.lon)
    else:
        m = float(coor1.lat - coor2.lat) / float(coor1.lon - coor2.lon)
        b = coor1.lat - (m * coor1.lon)
        latstep = 1
        lonstep = 1
        if int(coor2.lat-coor1.lat) < 0:
            latstep = -1
        if int(coor2.lon-coor1.lon) < 0:
            lonstep = -1
        prolat = []
        prolon = []
        prolat.append(coor1.lat)
        prolon.append(coor1.lon)
        if abs(int(coor1.lat)-int(coor2.lat)) > 0:
            f = -0.00000001 * latstep
            for lat in range(int(coor1.lat)-latstep,int(coor2.lat)+latstep,latstep):
                prolat.append(float(lat-f))
                prolon.append((float(lat)-b)/m)
        if abs(int(coor1.lon)-int(coor2.lon)) > 0:
            f = -0.00000001 * lonstep
            for lon in range(int(coor1.lon)-lonstep,int(coor2.lon)+lonstep,lonstep):
                prolat.append(b + (m*float(lon)))
                prolon.append(float(lon-f))
        prolat.append(coor2.lat)
        prolon.append(coor2.lon)
        for i in range(0,len(prolat)-1):
            for j in range(i,len(prolat)):
                if prolat[i] > prolat[j] and abs(coor1.lat-coor2.lat) > abs(coor1.lon-coor2.lon):
                    temp = prolat[j]
                    prolat[j] = prolat[i]
                    prolat[i] = temp
                    temp = prolon[j]
                    prolon[j] = prolon[i]
                    prolon[i] = temp
                elif prolon[i] > prolon[j] and abs(coor1.lon-coor2.lon) > abs(coor1.lat-coor2.lat):
                    temp = prolon[j]
                    prolon[j] = prolon[i]
                    prolon[i] = temp
                    temp = prolat[j]
                    prolat[j] = prolat[i]
                    prolat[i] = temp
    for i in range(0,len(prolat)-1):
        c1 = Lat_Lon(prolat[i],prolon[i])
        c2 = Lat_Lon(prolat[i+1],prolon[i+1])
        temp = Lat_Lon(0.,0.)
        if c2.lat < c1.lat:
            temp = c1
            c1 = c2
            c2 = temp
        profile_t = get_profile(dempath, c1, c2)
        if i == 0:
            profile = profile_t
        else:
            profile = np.concatenate([profile,profile_t])
    return profile
# _____________________________________________________________________

def open_winfile(d_name,d_dir,w_mode,rt,message):
    wfile = tkFileDialog.askopenfile(parent=rt,mode=w_mode,title=message,initialdir=d_dir,initialfile=d_name)
    if wfile != None:
#        print "%s was opened" % wfile
        return wfile
    else:
#        print "The file %s does not exists" % wfile
        return 0

# ___________________________________________________________________

def lut():
    cml = []
    c = ['k','r','g','b','c','y','m']
    m = ['o','D','h','+','.','s','*','^']
    l = ['-','--','-.',':']
    for i in range(0,3):
        for j in range(0,7):
            for k in range(0,6):
                cml.append(c[k]+m[j]+l[i])
    return cml
# ___________________________________________________________________

def dist_ll(lat1, lon1, lat2, lon2):
    a=lat1*0.0174533
    b=lat2*0.0174533
    P=abs((lon2-lon1)*0.0174533)
    dist = (sin(a)*sin(b))+(cos(a)*cos(b)*cos(P))
    if dist<1.0:
        dist=acos(dist)/0.0174533*111195
    else:
        dist=0.0
    return abs(dist);
# ___________________________________________________________________

def read_tab(d_name):
    try:
        f111 = open(d_name,"r")
    except IOError:
      print "There was an error reading file ", d_name
      sys.exit()
    h=[]
    lat=[]
    lon=[]
    cy=[]
    ye=[]
    da=[]
    alt=[]
    d=[]
    station = []
    cycleref = 0
    t1 = ""
    while t1 != "*999*":
        t = f111.readline()
        t1 = t[0:5]
    t2 = t.split(' ')
    ult = len(t2)
    for i in range(0,ult):
        if t2[i]=="H-&&&":
            i_h = i
        elif t2[i]=="longitude":
            i_lon = i
        elif t2[i]=="latitude":
            i_lat = i
        elif t2[i]=="*999*cycle":
            i_cycle = i
        elif t2[i]=="year":
            i_year = i
        elif t2[i]=="day":
            i_day = i
        elif t2[i]=="altitude":
            i_alt = i
    n = 0
    t=f111.readline()
    while len(t) > 6:
        t2 = t.split(' ')
        h.append(float(t2[i_h]))
        lon.append(float(t2[i_lon]))
        lat.append(float(t2[i_lat]))
        cy.append(int(t2[i_cycle]))
        da.append(float(t2[i_day]))
        ye.append(int(t2[i_year]))
        alt.append(float(t2[i_alt]))
        d.append(-1)
        t=f111.readline()
        n+=1
        cycleref = cy[0]
    f111.close()
    lat1 = []
    lon1 = []
    h1 = []
    alt1 = []
    ini = 0
    fin = 0
    for i in range(1,n):
        if cy[i] != cycleref or i == n-1:
            fin = i-1
            if i == n-1:
                fin = i
#            print 'ini: ', ini, 'fin: ', fin
            if lat[ini] > lat[fin]:
                lat1 = lat[ini:fin+1]
                lon1 = lon[ini:fin+1]
                h1 = h[ini:fin+1]
                alt1 = alt[ini:fin+1]
                d1 = d[ini:fin+1]
            else:
                lat1 = list(reversed(lat[ini:fin+1]))
                lon1 = list(reversed(lon[ini:fin+1]))
                h1 = list(reversed(h[ini:fin+1]))
                alt1 = list(reversed(alt[ini:fin+1]))
                d1 = d[ini:fin+1]
            thedate = dt.datetime(ye[ini],1,1) + dt.timedelta(da[ini]-1)
            station.append(Vas(cy[ini],thedate,-9999.,fin-ini+1,lat1,lon1,h1,d1,0,alt1,-9999.,-9999.))
            ini = fin+1
            cycleref = cy[i]
    return station;
# ___________________________________________________________________

def read_cprm(d_name,station):
    n=len(station)
    for i in range(0,n):
        station[i].cal = float(-9999.)
    try:
        f2 = open(d_name,'rt')
    except IOError:
        return
    for i in range(0,n):
        station[i].cal = float(-9999.)

    t = ""
    valvalue = []
    while t[0:15] != "//EstacaoCodigo":
        t = f2.readline()
    t2 = t.split(';')
    ult = len(t2)
    for j in range(0,ult):
        if t2[j]=="Data":
            j_date = j
        elif t2[j]=="Hora":
            j_time = j
        elif t2[j]=="Cota01":
            j_day1 = j
    surday = dt.date(1,1,1)
    for i in range(0,n):
        flag = 0
        j = 0
        t=f2.readline()
        t.replace(',', '.')
        while ((t != '') and (flag == 0)) and (surday <= station[i].hdate):
            t2 = t.split(';')
            d1, m1, y1 = (int(x) for x in t2[j_date].split('/'))
            surday =  dt.date(y1, m1, d1)
            if j>4:
                t=f2.readline()
                t.replace(',', '.')
            if (surday.year == station[i].hdate.year) and (surday.month == station[i].hdate.month):
                refvalue = t2[j_day1+int(station[i].hdate.day)-1]
                if refvalue != '':
                    station[i].cal = float(refvalue)/100
                else:
                    station[i].cal = float(-9999.)
                flag = 1
            j+=1
    f2.close()
    return
# ___________________________________________________________________

def conv_cprm(intxt,fout,iniyear,finyear,dist):
    try:
        fin = open(intxt,'rt')
    except IOError:
        return
    t = ""
    while t[0:15] != "//EstacaoCodigo":
        t = fin.readline()
    t2 = t.split(';')
    ult = len(t2)
    flag = 0
    inidate = dt.date(iniyear,1,1)
    outdate = []
    outval = []
    for j in range(0,ult):
        if t2[j]=="Data":
            j_date = j
        elif t2[j]=="Hora":
            j_time = j
        elif t2[j]=="Cota01":
            j_day1 = j
    surday = dt.date(1,1,1)
    while (t != '') and (surday.year <= finyear):
        t=fin.readline()
        t.replace(',', '.')
        t2 = t.split(';')
        d1, m1, y1 = (int(x) for x in t2[j_date].split('/'))
        surday =  dt.date(y1, m1, d1)
        t=fin.readline()
        t.replace(',', '.')
        if (surday.year >= iniyear) and (surday.year <= finyear):
           for day in range(1,31):
               surday = surday + dt.timedelta(days=1)
               val = t2[j_day1+int(day)-1]
               val = val.replace(',','.')
               if val != '':
                   outdate.append(surday)
                   outval.append(float(val))
    outval = np.array(outval)
    av = sum(outval)/len(outval)
    outval = outval-av
    for i in range(0,len(outval)):
        difdate = outdate[i]-inidate
        s = "%.1f %.2f %.2f\n" % (difdate.days,dist/1000,outval[i])
        fout.write(s)
    print min(outval), max(outval), '              ', max(outval)-min(outval)
    fin.close()
    return
# ___________________________________________________________________

def twopops_mean(station):
    mean = x_bar(station.h)
    topmean = 0
    botmean = 0
    n1 = 0
    n2 = 0
    for j in range(0,station.nh):
        if station.h[j] > mean:
            topmean+=station.h[j]
            n1+=1
        else:
            botmean+=station.h[j]
            n2+=1
    topmean = topmean/n1
    botmean = botmean/n2
    for j in range(0,station.nh):
        if station.h[j] > mean:
            station.h[j] = topmean
        else:
            station.h[j] = botmean
# ___________________________________________________________________

def x_bar(x):
    return (sum(x)/len(x))
# ___________________________________________________________________
    
def x_hat(x):
    return min(x)+((max(x)-min(x))/2)
# ___________________________________________________________________

def x_mode(x):
    return x_hat(x)+(3*(x_bar(x)-x_hat(x)))
# ___________________________________________________________________

def twopops_median(station):
    median = x_hat(station.h)
    topmedian = 0
    botmedian = 0
    t = []
    b = []
    for j in range(0,station.nh):
        if station.h[j] > median:
            t.append(station.h[j])
        else:
            b.append(station.h[j])
    tmed = x_hat(t)
    bmed = x_hat(b)
    for j in range(0,station.nh):
        if station.h[j] > median:
            station.h[j] = tmed
        else:
            station.h[j] = bmed
# ___________________________________________________________________

def filter_peaks(station):
    for j in range(1,station.nh-1):
        if abs(station.h[j-1] - station.h[j])>abs(station.h[j-1] - station.h[j+1]):
            if abs(station.h[j+1] - station.h[j])>abs(station.h[j-1] - station.h[j+1]):
                station.h[j] = (station.h[j-1] + station.h[j+1]) / 2

# ___________________________________________________________________
#                             EXTRACT PROFILE VALUES
def get_profile_old(dempath, c1, c2):
    latpart = '0'+str(abs(int(c1.lat))+1)
    if abs(c1.lat) >= 10:
        latpart = str(abs(int(c1.lat))+1)
    lonpart = '00'+str(abs(int(c1.lon))+1)
    if abs(c1.lon) >= 10:
        lonpart = '0'+str(abs(int(c1.lon))+1)
    if abs(c1.lon) >= 100:
        lonpart = str(abs(int(c1.lon))+1)
    if c1.lat < 0:
        latpart = 's'+latpart
    else:
        latpart = 'n'+latpart
    if c1.lon < 0:
        lonpart = 'w'+lonpart
    else:
        lonpart = 'e'+lonpart
    demname = dempath+'/'+latpart+'_'+lonpart+'*.hdr'
##    print demname
# ********************************************************

    dem = glob.glob(demname)
    print demname
    imh = Image_Header()
    imh.read(dem[0])
##    print imh.ncols, imh.nrows, imh.nbands, imh.nbits, imh.ulx, imh.uly, imh.xdim, imh.ydim, imh.pixtype
    if c1.lat > c2.lat:
        ul = Point(int((c1.lon-imh.ulx)/imh.xdim), int((imh.uly-c1.lat)/imh.ydim))
        lr = Point(int((c2.lon-imh.ulx)/imh.xdim), int((imh.uly-c2.lat)/imh.ydim))
    else:
        lr = Point(int((c1.lon-imh.ulx)/imh.xdim), int((imh.uly-c1.lat)/imh.ydim))
        ul = Point(int((c2.lon-imh.ulx)/imh.xdim), int((imh.uly-c2.lat)/imh.ydim))
##    print ul.x,ul.y,lr.x,lr.y

    dembin = dem[0].replace('.hdr','.bil')
    demdata = Imagem_Bil(dembin,imh).read_bloc(imh,ul,lr)
    [rows,cols] = shape(demdata)
    m = (ul.y - lr.y) / float(ul.x - lr.x)
    b = ul.y - (m * ul.x)
##    print m,b
    profile = []
    for i in range(0,rows-1):
        j = int(i/m)
        profile.append(demdata[i,j])
    return profile

# ___________________________________________________________________

def cross_point(ll_11, ll_12, ll_21, ll_22):
    ll_3 = Lat_Lon(-999,-999)
    
    if (ll_12.lon - ll_11.lon) == 0 and (ll_22.lon - ll_21.lon) == 0:
        ll_3.lat = 999
        ll_3.lon = 999
        return ll_3

    if (ll_12.lon - ll_11.lon) == 0 and (ll_22.lon - ll_21.lon) != 0:
        m2 = (ll_22.lat - ll_21.lat) / (ll_22.lon - ll_21.lon)
        b2 = ll_21.lat - (m2 * ll_21.lon)
        ll_3.lon = ll_11.lon
        ll_3.lat = (m2 * ll_3.lon) + b2
        return ll_3

    if (ll_12.lon - ll_11.lon) != 0 and (ll_22.lon - ll_21.lon) == 0:
        m1 = (ll_12.lat - ll_11.lat) / (ll_12.lon - ll_11.lon)
        b1 = ll_11.lat - (m1 * ll_11.lon)
        ll_3.lon = ll_21.lon
        ll_3.lat = (m1 * ll_3.lon) + b1
        return ll_3

    m1 = (ll_12.lat - ll_11.lat) / (ll_12.lon - ll_11.lon)
    m2 = (ll_22.lat - ll_21.lat) / (ll_22.lon - ll_21.lon)
    b1 = ll_11.lat - (m1 * ll_11.lon)
    b2 = ll_21.lat - (m2 * ll_21.lon)

    if m1 == m2:
        ll_3.lat = 999
        ll_3.lon = 999
        return ll_3
    
    elif m1 == 0 and m2 != 0:
        ll_3.lat = ll_11.lat
        ll_3.lon = (ll_3.lat - b2) / m2
        return ll_3
    
    elif m1 != 0 and m2 == 0:
        ll_3.lat = ll_21.lat
        ll_3.lon = (ll_3.lat - b1) / m1
        return ll_3

    else:
        ll_3.lon = ((b2-b1)/(m1-m2))
        ll_3.lat = (m1 * ll_3.lon) + b1
    return ll_3

# ___________________________________________________________________
        
def point_on_line(p, l_11, l_12, l_21, l_22):
    flag = 0
    if p.lat >= l_11.lat and p.lat <= l_12.lat:
        if p.lon >= l_11.lon and p.lon <= l_12.lon:
            flag = 1
        elif p.lon <= l_11.lon and p.lon >= l_12.lon:
            flag = 1
        else:
            flag = 0
    elif p.lat <= l_11.lat and p.lat >= l_12.lat:
        if p.lon >= l_11.lon and p.lon <= l_12.lon:
            flag = 1
        elif p.lon <= l_11.lon and p.lon >= l_12.lon:
            flag = 1
        else:
            flag = 0
    if flag == 0:
        return 0

    if p.lat >= l_21.lat and p.lat <= l_22.lat:
        if p.lon >= l_21.lon and p.lon <= l_22.lon:
            return 1
        elif p.lon <= l_21.lon and p.lon >= l_22.lon:
            return 1
        else:
            return 0
    elif p.lat <= l_21.lat and p.lat >= l_22.lat:
        if p.lon >= l_21.lon and p.lon <= l_22.lon:
            return 1
        elif p.lon <= l_21.lon and p.lon >= l_22.lon:
            return 1
        else:
            return 0
    else:
        return 0

# __________________________________________________________________  

def bbox_intersect(ul1, br1, ul2, br2):
    if point_between(ul1, ul2, br2):
        return 1
    if point_between(br1, ul2, br2):
        return 1
    if point_between(ul2, ul1, br1):
        return 1
    if point_between(br2, ul1, br1):
        return 1
    return 0

# __________________________________________________________________  

def point_between(p, ul, br):
    if p.lat < ul.lat and p.lat > br.lat and p.lon > ul.lon and p.lon < br.lon:
        return 1
    return 0
   
# __________________________________________________________________  

def idw_average(dist,value,exp):
    wval = 0
    w = 0
    for i in range(len(value)):
        wval+=value[i]*(1/(abs(dist[i]/1000)**exp))
        w+= 1/(abs(dist[i]/1000)**exp)
    return wval/w
    
# __________________________________________________________________  

def autocor(mat1, mat2):
    if mat1.shape != mat2.shape:
        return 0.0
    else:
        s = mat1.shape
        if len(s) == 2:
            n = s[0]*s[1]
        else:
            n = s[0]
        matminusav1 = mat1-(float(sum(sum(mat1)))/n)
        matminusav2 = mat2-(float(sum(sum(mat2)))/n)
        return sum(sum((matminusav1)*(matminusav2)))/(((sum(sum(matminusav1*matminusav1))*sum(sum(matminusav2*matminusav2)))**0.5)+0.00001)

# __________________________________________________________________  

def vect_autocor(vec1, vec2):
    if vec1.shape != vec2.shape:
        return 0.0
    else:
        n = len(vec1)
        matminusav1 = vec1-(float(sum(vec1))/n)
        matminusav2 = vec2-(float(sum(vec2))/n)
        return sum((matminusav1)*(matminusav2))/(((sum(matminusav1*matminusav1)*sum(matminusav2*matminusav2))**0.5)+0.00001)

# __________________________________________________________________  


def poli2deg(x,y):
    a = np.array([0.0, 0.0, 0.0])
    if len(x) < 6:
        return a
    else:
        sx = sum(x)
        sx2 = sum(x*x)
        sx3 = sum(x*x*x)
        sx4 = sum(x*x*x*x)
        sy = sum(y)
        sxy = sum(x*y)
        sx2y = sum(x*x*y)
        A = np.array([ [len(x), sx, sx2], [sx, sx2, sx3], [sx2, sx3, sx4] ])
        B = np.array([sy, sxy, sx2y])
        return np.linalg.solve(A,B)
        
# __________________________________________________________________  

def poli1deg(x,y):
    a = np.array([0.0, 0.0])
    if len(x) < 4:
        return a
    else:
        sx = sum(x)
        sx2 = sum(x*x)
        sy = sum(y)
        sxy = sum(x*y)
        A = np.array([ [len(x), sx], [sx, sx2] ])
        B = np.array([sy, sxy])
        return np.linalg.solve(A,B)
# __________________________________________________________________  
      
def intepol(za, zb, dab, dc):
    return (((zb-za)/dab)*dc)+za

# __________________________________________________________________  
      
def sumofsquares2(x,y,a):
    n = len(x)
    ssq = 0
    for i in range(0,n):
        sq = y[i] - (a[0] + (a[1]*x[i]) + (a[2]*x[i]*x[i]))
        sq = sq * sq
        ssq = ssq + sq
    return ssq/n
    
# __________________________________________________________________  

def bestpointsubset(x,y):
    b = [0,1.0,0.000001,0,1.0]
    n = len(x)-6
    if n == 0:
        return b
    minindex = 0
    x1=np.zeros(len(x)+4)
    y1=np.zeros(len(x)+4)
    
    for i in range(0,n):
        if abs(x[0])>abs(x[len(x)-1]):
            x = x[ ::-1]
            y = y[ ::-1]
        for j in range(0,4):
            x1[j]=x[0]
            y1[j]=y[0]
        for j in range(4,len(x1)):
            x1[j]=x[j-4]
            y1[j]=y[j-4]
#        print y1[0:len(x1)-i]
        a = poli2deg(x1[0:len(x1)-i],y1[0:len(x1)-i])
        aa = poli1deg(x1[0:len(x1)-i],y1[0:len(x1)-i])
        err = sumofsquares2(x1,y1,a)
        if i == 0:
            minerr = err
            b = [a[0],a[1],a[2],aa[0],aa[1]]
        else:
            if err < minerr:
                minerr = err
                minindex = i
                b = [a[0],a[1],a[2],aa[0],aa[1]]
#        print a, err, n, len(x)
#    print minindex
    return b
        
# __________________________________________________________________  
        
def min_dist_classifier_left(v):
    cat = []
    cat.append(Class_Vector('Bump',[-2990, -0.3890, -118, 7913]))
    cat.append(Class_Vector('Flat',[-248, -0.0125, -156, 11406]))
    cat.append(Class_Vector('Hole',[483, 0.0838, -111, 6145]))
    cat.append(Class_Vector('Hook',[-2073, -0.3984, 917, 5052]))
    cat.append(Class_Vector('Up',[-30, -0.0850, -678, 42766]))

    if len(v) != 4:
        return 'None'
    dmin = 1000000
    for i in range(0,4):
        d = 0
        for j in range(0,3):
            d = d + ((v[j] - cat[i].variables[j]) * (v[j] - cat[i].variables[j]))
        if i == 0:
            dmin = d
            name = cat[i].name
        else:
            if d < dmin:
                dmin = d
                name = cat[i].name
    return name

# __________________________________________________________________  
        
def min_dist_classifier_right(v):
    cat = []
    cat.append(Class_Vector('Bump',[843, -0.0814, 223, -10440]))
    cat.append(Class_Vector('Flat',[342, -0.0282, 137, -3395]))
    cat.append(Class_Vector('Hole',[-2243, 0.2997, -82, -8875]))
    cat.append(Class_Vector('Hook',[1510, -0.437, -1565, -2852]))
    cat.append(Class_Vector('Up',[-1532, -0.398, 1212, 8669]))

    if len(v) != 4:
        return 'None'
    dmin = 1000000
    for i in range(0,4):
        d = 0
        for j in range(0,3):
            d = d + ((v[j] - cat[i].variables[j]) * (v[j] - cat[i].variables[j]))
        if i == 0:
            dmin = d
            name = cat[i].name
        else:
            if d < dmin:
                dmin = d
                name = cat[i].name
    return name

# __________________________________________________________________  
        
def rule_classifier_left(v):
    if abs(v[1]) < 0.02:
        if v[2] > 100:
            return 'Down'
        elif v[2] < -100:
            return 'Up'
        else:
            return 'Flat'
    else:
        if v[2] > 100:
            return 'Hook'
        elif v[2] < -100:
            return 'Hump'
        else:
            if v[1] >= 0.02:
                return 'Hole'
            else:
                return 'Bump'

# __________________________________________________________________  
        
def rule_classifier_right(v):
    if abs(v[1]) < 0.02:
        if v[2] > 100:
            return 'Up'
        elif v[2] < -100:
            return 'Down'
        else:
            return 'Flat'
    else:
        if v[2] > 100:
            return 'Hump'
        elif v[2] < -100:
            return 'Hook'
        else:
            if v[1] >= 0.02:
                return 'Hole'
            else:
                return 'Bump'
        
# __________________________________________________________________  
        
def determine_exponent(name):
    if name == 'Up':
        return 3.0
    elif name == 'Down':
        return 3.0
    elif name == 'Flat':
        return 1.5
    elif name == 'Bump':
        return 2.5
    elif name == 'Hump':
        return 3.0
    elif name == 'Hook':
        return 3.0
    elif name == 'Hole':
        return 2.0
    else:
        return 1.5
# __________________________________________________________________  

def average_level(d_name,start_year,end_year):
    try:
        f2 = open(d_name,'rt')
    except IOError:
        return
    t = ""
    valvalue = []
    while t[0:15] != "//EstacaoCodigo":
        t = f2.readline()
    t2 = t.split(';')
    ult = len(t2)
    for j in range(0,ult):
        if t2[j]=="Data":
            j_date = j
        elif t2[j]=="Hora":
            j_time = j
        elif t2[j]=="Cota01":
            j_day1 = j-1
    surday = dt.date(1,1,1)
    average_level=[]
    n_level=np.zeros(366)
    for k in range(0,366):
        average_level.append(0.0)
    t=f2.readline()
    t2 = t.split(';')
    d1, m1, y1 = (int(x) for x in t2[j_date].split('/'))
    m2 = 0
    while ((t != '') and (int(y1) <= end_year)):
        if ((int(y1) >= start_year) and (m1 != m2)):
            m2 = m1
            last_month_day = calendar.monthrange(y1,m1)
            for i in range(1,last_month_day[1]+1):
                surday =  dt.date(y1, m1, i)
                val = (t2[j_day1+i])
                try:
                    val2 = float(int(val))
                except:
                    try:
                        val2 = float(val)
                    except:
                        val2 = 0.0
                index = date_to_julian_day(surday)-1
                if val2 != 0.0:
                    average_level[index] = average_level[index] + float(val2)
                    n_level[index]+=1
##                print surday, date_to_julian_day(surday), val
        t=f2.readline()
        t2 = t.split(';')
        d1, m1, y1 = (int(x) for x in t2[j_date].split('/'))
    for k in range(0,366):
        average_level[k] = average_level[k] / (n_level[k]*100)
##        print  "%d %.2f" % (k, average_level[k])
    f2.close()
    return average_level
# ___________________________________________________________________

def date_to_julian_day(my_date):
    first_day = dt.date.toordinal(dt.date(my_date.year,1,1))
    return (dt.date.toordinal(my_date) - first_day)
# ___________________________________________________________________
                
def simulate_hooking(alt_sat,alt_ter,vsta,sf,footprint_radius,rw,midx,midy):
    r = []
    shapes = sf.shapes()
    npline = len(shapes)
    sfx1 = []
    sfy1 = []
    for kk in range(0,npline):
        npoints = len(shapes[kk].points)
        for i in range(0,npoints):
            sfxy = shapes[kk].points[i]
            if sfxy[0]>midx-0.2:
                if sfxy[0]<midx+0.2:
                    if sfxy[1]>midy-0.2:
                        if sfxy[1]<midy+0.2:
                            sfx1.append(sfxy[0])
                            sfy1.append(sfxy[1])
    for i in range(0,vsta.nh):
        dmin = footprint_radius
        r.append(0)
        for j in range(0,len(sfx1)):
            d = dist_ll(sfy1[j], sfx1[j], vsta.lat[i], vsta.lon[i])
            if d < dmin and d >= rw:
                r[i] = alt_ter + (alt_sat - ((alt_sat**2 + d**2)**0.5))
                dmin = d
            elif d < rw:
                r[i] = alt_ter
    return np.array(r)

# ___________________________________________________________________
                
def simulate_hooking_inverse(alt_sat,hk,vsta,sf,footprint_radius,rw,midx,midy):
    r = []
    shapes = sf.shapes()
    npline = len(shapes)
    sfx1 = []
    sfy1 = []
    for kk in range(0,npline):
        npoints = len(shapes[kk].points)
        for i in range(0,npoints):
            sfxy = shapes[kk].points[i]
            if sfxy[0]>midx-0.2:
                if sfxy[0]<midx+0.2:
                    if sfxy[1]>midy-0.2:
                        if sfxy[1]<midy+0.2:
                            sfx1.append(sfxy[0])
                            sfy1.append(sfxy[1])
    for i in range(0,vsta.nh):
        r.append(0)
        if hk[i] != -999:
            dmin = footprint_radius
            alt_ter = hk[i]
            for j in range(0,len(sfx1)):
                d = dist_ll(sfy1[j], sfx1[j], vsta.lat[i], vsta.lon[i])
                if d < dmin and d >= rw:
                    r[i] = alt_ter - (alt_sat - ((alt_sat**2 + d**2)**0.5))
                    dmin = d
                elif d < rw:
                    r[i] = alt_ter
    return np.array(r)

# ___________________________________________________________________
                
def fit_hook(a,b):
    if (len(a) != len(b)):
        return 0
    dif = np.array(b) - np.array(a)
    for i in range(0,len(a)):
        a[i]+=min(dif)
    return np.array(a)

# ___________________________________________________________________
                
def fit_hook_idw(moving,fixed,dist):
    if (len(moving) != len(fixed)):
        return 0
    dif = 0.0
    diviser = 0.1
    for i in range(0,len(moving)):
        if moving[i] > 0:
            idw = (1.0/abs(dist[i]/1000))
            idw = idw * idw
            dif += (fixed[i] - moving[i]) * (fixed[i] - moving[i]) * idw
            diviser += idw
    dif = dif / diviser
    dif = sqrt(dif)
    for i in range(0,len(moving)):
        if moving[i] > 0:
            moving[i] += dif
    return moving

# ___________________________________________________________________
                
def sort_north(ll):
    for i in range(0,len(ll)-1):
        for j in range(i+1,len(ll)):
            if ll[j].lat > ll[i].lat:
                templat = ll[i].lat
                ll[i].lat = ll[j].lat
                ll[j].lat = templat
                templon = ll[i].lon
                ll[i].lon = ll[j].lon
                ll[j].lon = templon
    return ll

# ___________________________________________________________________
                
def sort_point_north(p):
    for i in range(0,len(p)-1):
        for j in range(i+1,len(p)):
            if p[j].y > p[i].y:
                temp = p[i].y
                p[i].y = p[j].y
                p[j].y = temp
                temp = p[i].x
                p[i].x = p[j].x
                p[j].x = temp
    return p
# ___________________________________________________________________
                
def xing_point(sf,ll_11,ll_12):

    shapes = sf.shapes()
    npline = len(shapes)

    midy = (ll_11.lat + ll_12.lat) / 2.0
    midx = (ll_11.lon + ll_12.lon) / 2.0

    nxing = 0
    midpoints = []
    for kk in range(0,npline):
        npoints = len(shapes[kk].points)
        latxing = []
        lonxing = [] 
        for i in range(0,len(shapes[kk].parts)):
            sfx = []
            sfy = []
            ini = shapes[kk].parts[i]
            if i == len(shapes[kk].parts)-1:
                fin = npoints
            else:
                fin = shapes[kk].parts[i+1]
#            if fin-ini > 1000:
#                print kk, i, fin-ini
            for j in range(ini,fin):
                sfxy = shapes[kk].points[j]
                sfx.append(sfxy[0])
                sfy.append(sfxy[1])
            for jj in range(1, len(sfx)):
                ll_21 = Lat_Lon(sfy[jj-1],sfx[jj-1])
                ll_22 = Lat_Lon(sfy[jj],sfx[jj])
                pol = cross_point(ll_11, ll_12, ll_21, ll_22)
                if point_on_line(pol, ll_11, ll_12, ll_21, ll_22) == 1:
                    midpoints.append(pol)
                    nxing+=1
            
    midpoints = sort_north(midpoints)
    midpointx = []
    midpointy = []
    for i in range(0,nxing-1,2):
        midpointx.append((midpoints[i].lon+midpoints[i+1].lon)/2.0)
        midpointy.append((midpoints[i].lat+midpoints[i+1].lat)/2.0)
#    print midpointx, midpointy
    dist = 10000000
    index = 0
    for i in range(0,len(midpointx)):
        if dist_ll(midpointy[i], midpointx[i], midy, midx) < dist:
            index = i
            dist = dist_ll(midpointy[i], midpointx[i], midy, midx)
    if len(midpointx) != 0:
        return Lat_Lon(midpointy[index], midpointx[index])
    else:
        return Lat_Lon(-999, -999)

# ____________________________________________ Find Nearest _______________________________________

def find_nearest(arr, val):
    return (np.abs(arr-val)).argmin()

# _________________________________________ Polar to Cartesian ____________________________________

def polar2cartesian(theta, phi, d):
    cart = [0.0,0.0,0.0,1.0]
    theta = theta * pi / 180
    phi = (phi-90) * pi / 180
    cart[0] = d * sin(theta) * cos(phi)
    cart[1] = d * sin(theta) * sin(phi)
    cart[2] = d * cos(theta)
    return cart

# _________________________________________ Polar to Cartesian ____________________________________

def gen_point_shape(name, lon, lat, label, data):
    
    if '.shp' in name:
        shpname = name
    else:
        shpname = name + '.shp'
    prjname = name + '.prj'
    w2 = shapefile.Writer(shapeType=1)
    w2.autoBalance = 1
    w2.field('Label','C','20')
    w2.field('Date','C', '20')
    for i in range(0,len(lon)):
        w2.point(lon[i],lat[i])
        w2.record(label[i],data[i])
    w2.save(shpname)
    w2 = None

    prj = open(prjname, "w")
    epsg = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    prj.write(epsg)
    prj.close()

                
# _____________________________________ Create line shapefile ____________________________________

def gen_line_shape(name, chain, field1, state):
    
    if '.shp' in name:
        shpname = name
    else:
        shpname = name + '.shp'
    if state == 1:
        r = shapefile.Reader(shpname)
        w = shapefile.Writer(r.shapeType)
        w.fields = list(r.fields)
        w.records.extend(r.records())
        w._shapes.extend(r.shapes())
    else:
        w = shapefile.Writer(shapefile.POLYLINE)
        w.field('Cycle','C','4')
        w.field('Track','C','4')
        w.field('Date','C', '20')
        w.field('h','N',8,3)
        w.autoBalance = 1
    w.line(parts=chain)
    w.record(field1,field2,field3,field4)
    w.save(shpname)
    w = None

#  Read the shape file of the satellite track
# _________________________________________________________________________________________________
def read_tracks(nome):
    track_sf = shapefile.Reader(nome)
    trackline = track_sf.shapes()
    trackfields = track_sf.fields
    ntline = len(trackline)

    pol = []
    for kk in range(0,ntline):
        recs = track_sf.record(kk)
        tt = recs[0]
        vert = []
        npoints = len(trackline[kk].points)
        for i in range(0,len(trackline[kk].parts)):
            ini = trackline[kk].parts[i]
            if i == len(trackline[kk].parts)-1:
                fin = npoints
            else:
                fin = trackline[kk].parts[i+1]
            tx = []
            ty = []
            for j in range(ini,fin):
                txy = trackline[kk].points[j]
                tx.append(txy[0])
                ty.append(txy[1])
            for j in range(0,len(tx)-1):
                vert.append(Vertice(tx[j], ty[j], tx[j+1], ty[j+1], tt))
        pol.append(Polig(vert))
    return pol
# ________________________________________________________________________________________________

#  Read the shape file of the river
# _________________________________________________________________________________________________
def read_waterbody(nome):

    sf = shapefile.Reader(nome)
    shapes = sf.shapes()
    npline = len(shapes)
    pol = []
    for kk in range(0,npline):
        recl = sf.record(kk)
        lake_name = recl[1]
#        print lake_name
        npoints = len(shapes[kk].points)
        for i in range(0,len(shapes[kk].parts)):
            ini = shapes[kk].parts[i]
            if i == len(shapes[kk].parts)-1:
                fin = npoints
            else:
                fin = shapes[kk].parts[i+1]
##            print kk, i, npline, npoints, ini, fin
            sfx = []
            sfy = []
            for j in range(ini,fin):
                sfxy = shapes[kk].points[j]
                sfx.append(sfxy[0])
                sfy.append(sfxy[1])
            vert = []
            for j in range(0,len(sfx)-1):
                vert.append(Vertice(sfx[j], sfy[j], sfx[j+1], sfy[j+1], lake_name))
            vert.append(Vertice(sfx[len(sfx)-1], sfy[len(sfx)-1], sfx[0], sfy[0], lake_name))
            pol.append(Polig(vert))
    return pol
# ________________________________________________________________________________________________
def cross_point_vector(v1, v2):# essa funcao determina o ponto de cruzamento de dois vertices
    p1 = Point(-99999.99999, -99999.99999)# como a funcao tem que retornar um valor, se nao existe ponto de encontro
                                          # a funcao ira retornar esse valor
    if (v1.x1 - v1.x2) == 0 and (v2.x1 - v2.x2) == 0:# caso os 2 vertices sao verticais (inclinacao infinita)
        return p1
    if (v1.x1 - v1.x2) == 0 and (v2.x1 - v2.x2) != 0:# caso o primeiro vertice e vertical basta determinar o y
        m2 = (v2.y2 - v2.y1) / (v2.x2 - v2.x1)
        b2 = v2.y1 - (m2 * v2.x1)
        p1.x = v1.x1
        p1.y = (m2 * p1.x) + b2
        return p1
    if (v1.x1 - v1.x2) != 0 and (v2.x1 - v2.x2) == 0:# caso o segundo vertice e vertical basta determinar o y
        m1 = (v1.y2 - v1.y1) / (v1.x2 - v1.x1)
        b1 = v1.y1 - (m1 * v1.x1)
        p1.x = v2.x1
        p1.y = (m1 * p1.x) + b1
        return p1
    m1 = (v1.y2 - v1.y1) / (v1.x2 - v1.x1)
    m2 = (v2.y2 - v2.y1) / (v2.x2 - v2.x1)
    b1 = v1.y1 - (m1 * v1.x1)
    b2 = v2.y1 - (m2 * v2.x1)
    if m1 == m2:# caso as duas inclinacoes sao iguais -> os vertices sao paralelos
        return p1
    elif m1 == 0 and m2 != 0:# caso o primeiro vertice e horizontal basta determinar o x
        p1.y = v1.y1
        p1.x = (p1.y - b2) / m2
        return p1
    elif m1 != 0 and m2 == 0:# caso o segundo vertice e horizontal basta determinar o x
        p1.y = v2.y1
        p1.x = (p1.y - b1) / m1
        return p1
    else:# para todos os outros casos, temos de determinar o ponto de encontro fazendo o calculo completo
        p1.x = ((b2-b1)/(m1-m2))
        p1.y = (m1 * p1.x) + b1
    return p1
# ___________________________________________________________________

def ponto_na_linha(p2,v3):   # ja sabemos que o ponto pertence ao vertice, mas nao sabemos se ele cai no intervalo    
    if p2.y >= min(v3.y1,v3.y2) and p2.y <= max(v3.y1,v3.y2) and p2.x >= min(v3.x1,v3.x2) and p2.x <= max(v3.x1,v3.x2):
        return 1
    else:
        return 0
# ___________________________________________________________________

def ponto_em_poligono(pp,pol): # essa funcao determina se om ponto encontra-se dentro de um poligono
# no caso desse exercicio, nenhum dos vertices das linhas comeca ou termina dentro de um poligono, mas
# como poderia acontecer devemos considerar o caso e guardar esse ponto
    n_cruz = 0
    vtest = Vertice(pp.x,pp.y,pp.x,0,'0')# criamos um vertica partindo da linha ate a origem em y (0)
    for j in range(0,len(pol.v)):
        px = cross_point_vector(pol.v[j], vtest)
        if ponto_na_linha(px,vtest) and ponto_na_linha(px,pol.v[j]): # se o ponto de encontro pertance aos 2 vertices
            n_cruz+=1 # toda vez que o vertice cruza um vertice do poligono acrescentamos 1
    if n_cruz%2:# se o resto da divisao do numero de cruzamentos por dois = 1 (numero e impar)
        return 1
    else:
        return 0
# ___________________________________________________________________

def sort_vertice_north(x,y):
    for i in range(0,len(x)-1):
        for j in range(i,len(x)):
            if y[i] > y[j]:
                ty = y[i]
                y[i] = y[j]
                y[j] = ty
                tx = x[i]
                x[i] = x[j]
                x[j] = tx
# ___________________________________________________________________

    

