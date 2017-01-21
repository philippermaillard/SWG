import numpy as np
import sys
from math import cos, sin, acos, log, sqrt
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pylab import *
import datetime as dt
import shapefile
from netCDF4 import Dataset, MFDataset
import SWG_PyPM as PyPM
import os
import glob
os.putenv('CODA_DEFINITION', '/usr/local/share/coda/definitions/')
import coda

class SatAlt:
    def __init__(self,alt,lat,lon,ayear,aday,trk,ocean,ice1,ice2,ion,dry,wet,stide,ptide,track,cycle,wf,geoid):
        self.alt = alt
        self.lat = lat
        self.lon = lon
        self.ayear = ayear
        self.aday = aday
        self.trk = trk
        self.ocean = ocean
        self.ice1 = ice1
        self.ice2 = ice2
        self.ion = ion
        self.dry = dry
        self.wet = wet
        self.stide = stide
        self.ptide = ptide
        self.track = track
        self.cycle = cycle
        self.wf = wf
        self.geoid = geoid

#*************************** READ RA-2 FILES (CODA) ***************************    


def read_ra2_wf(dname,track,coord,d,cycle):
    c = 299792458.0
    B = 0.0
    sc = 0.001

    geoid = 0.0

# **************************** Find coda files *******************************    
    scycle = str(cycle)
    if cycle < 10:
        scycle = '0'+str(cycle)
    
    orbit = int((track/2.0)+0.5)
    sorbit = str(orbit)
    if orbit < 10:
        sorbit = '0000'+str(orbit)
    elif orbit < 100:
        sorbit = '000'+str(orbit)
    elif orbit < 1000:
        sorbit = '00'+str(orbit)
    else:
        sorbit = '0'+str(orbit)
        
    N1name = dname+'/RA2*A0'+scycle+'_'+sorbit+'*.N1'
   
    coda_name = glob.glob(N1name)
    passnumber = 0
    if (len(coda_name)!=0):
        for name in coda_name:
#            print name
            if passnumber == 0:
                pf = coda.open(name)
                passnumber = coda.fetch(pf, 'sph', 'pass_number')
##                print 'Found track',passnumber
                if passnumber != track:
                    coda.close(pf)
                    passnumber = 0
# ****************************************************************************    
    rec = []
    if passnumber != track: 
        return rec          
    try:    
        description = coda.get_description(pf)
    except IOError:
        return rec
    var = coda.fetch(pf, 'mph')
    n_param = coda.get_field_count(pf)
    names = coda.get_field_names(pf)
    n = coda.get_size(pf, 'avg_waveforms_mds')
#    print var, n, 'records', names
    s = coda.get_field_names(pf, 'ra2_mds', 0)
#    print s

# 'mph', 'sph', 'dsd', 'ra2_mds', 'mwr_mds', 'avg_waveforms_mds', 'burst_waveforms_mds'

    instr_mode = coda.fetch(pf, 'ra2_mds', -1, 'instr_mode_id_flags')
    alt0 =  coda.fetch(pf, 'ra2_mds', -1, 'alt_cog_ellip')
    altdif =  coda.fetch(pf, 'ra2_mds', -1, 'hz18_diff_1hz_alt')
    lat0 =   coda.fetch(pf, 'ra2_mds', -1, 'lat')
    lon0 =   coda.fetch(pf, 'ra2_mds', -1, 'lon')
    ocean0 =  coda.fetch(pf, 'ra2_mds', -1, 'ku_band_ocean_range')
    wet0 =   coda.fetch(pf, 'ra2_mds', -1, 'mod_wet_tropo_corr')
    dry0 =   coda.fetch(pf, 'ra2_mds', -1, 'mod_dry_tropo_corr')
    ion0 =   coda.fetch(pf, 'ra2_mds', -1, 'ion_corr_doris_ku')
    stide0 = coda.fetch(pf, 'ra2_mds', -1, 'solid_earth_tide_ht')
    ptide0 =  coda.fetch(pf, 'ra2_mds', -1, 'geocen_pole_tide_ht')
    latdif0 =  coda.fetch(pf, 'ra2_mds', -1, 'hz18_diff_1hz_lat')
    londif0 =  coda.fetch(pf, 'ra2_mds', -1, 'hz18_diff_1hz_lon')
    ice10 =   coda.fetch(pf, 'ra2_mds', -1, 'hz18_ku_ice1')
    ice20 =   coda.fetch(pf, 'ra2_mds', -1, 'hz18_ku_ice2')
    trk0 = coda.fetch(pf, 'ra2_mds', -1, 'hz18_ku_trk_cog')
    second0 = coda.fetch(pf, 'ra2_mds', -1, 'dsr_time')
    geoid = coda.fetch(pf, 'ra2_mds', -1, 'geoid_ht')
    geoid = geoid /1000.0
    
    latdif = np.ndarray((latdif0.size,latdif0[0].size))
    londif = np.ndarray((londif0.size,londif0[0].size))

    m = 20
    n = int(n[0])
    
    second = np.zeros((n,m))
    lat = np.zeros((n,m))
    lon = np.zeros((n,m))
    alt = np.zeros((n,m))
    altd = np.zeros((n,m))
    trk = np.zeros((n,m))
    ocean = np.zeros((n,m))
    ice1 = np.zeros((n,m))
    ice2 = np.zeros((n,m))
    day = np.zeros((n,m))
    year = np.zeros((n,m))
    jday = np.zeros((n,m))
    flag = np.ones((n,m))

    lag = 1    
    baseyear = dt.datetime(2000, 1, 1)
    for i in range(0,n):
        latdif[i,:] = np.asarray(latdif0[i])
        londif[i,:] = np.asarray(londif0[i])
        ice1[i,:] = np.asarray(ice10[i])
        ice2[i,:] = np.asarray(ice20[i])
        second[i,:] = np.asarray(second0[i])
        ocean[i,:] = np.asarray(ocean0[i])
        alt[i,:] = np.asarray(alt0[i])
        altd[i,:] = np.asarray(altdif[i])
        for j in range(0,m):
            alt[i,j] = alt[i,j] + altd[i,j]
            meas = baseyear + dt.timedelta(seconds=second[i,0])
            year[i,j] = meas.year
            jday[i,j] = meas.timetuple().tm_yday
        trk[i,:] = np.asarray(trk0[i])
        lat[i,:] = latdif[i,:] + lat0[i]
        lon[i,:] = londif[i,:] + lon0[i]# - 360

    dry = np.zeros((n,m))
    ion = np.zeros((n,m))
    wet = np.zeros((n,m))
    stide = np.zeros((n,m))
    ptide = np.zeros((n,m))
    wf = np.ndarray(shape=(n,m,128), dtype = int)

#    print 'First coordinate', lat[0,0],lon[0,0]
#    print 'Last  coordinate', lat[n-1,m-1],lon[n-1,m-1]
    for i in range(0,n):
        for j in range(0,m):
            dist = abs(lat[i,j]-coord.lat)*111000
            if dist <= d:
                if B == 0.0:
                    B = instr_mode[i] * 10000000
                    sr = c/(2*B)

#                    print 'instrument mode:', B
# ______________________________ Interpolate ___________________________________
                dab = PyPM.dist_ll(lat[i,0],lon[i,0],lat[i,m-1],lon[i,m-1])
                dab = dab * lag
                dc = PyPM.dist_ll(lat[i,j],lon[i,j],lat[i,m-1],lon[i,m-1])
                if j <= m/2:
                    dc = dc * -1
# ______________________________ Interpolate dry tropo __________________________
                za = dry0[i]
                zb = dry0[i+lag]
                dry[i,j] = PyPM.intepol(za, zb, dab, dc) * sc
# ______________________________ Interpolate ion ________________________________
                za = ion0[i]
                zb = ion0[i+lag]
                ion[i,j] = PyPM.intepol(za, zb, dab, dc) * sc
# ______________________________ Interpolate solid earth ________________________
                za = stide0[i]
                zb = stide0[i+lag]
                stide[i,j] = PyPM.intepol(za, zb, dab, dc) * sc
# ______________________________ Interpolate polar tide __________________________
                za = ptide0[i]
                zb = ptide0[i+lag]
                ptide[i,j] = PyPM.intepol(za, zb, dab, dc) * sc
# ______________________________ Interpolate wet tropo __________________________
                za = wet0[i]
                zb = wet0[i+lag]
                wet[i,j] = PyPM.intepol(za, zb, dab, dc) * sc

                swf =  coda.fetch(pf, 'avg_waveforms_mds',i,'data_blk_info',j, 'ave_ku_wvforms_if')
                wf[i,j,:] = swf[:]
                wf.astype(int)

                rec.append(SatAlt(alt[i,j]*sc,lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j]*sc,ocean[i,j]*sc,ice1[i,j]*sc,ice2[i,j]*sc,ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j], track,cycle,wf[i,j,:],geoid[i]))
#                print alt[i,j]*sc,lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j]*sc,ocean[i,j]*sc,\
#                    ice1[i,j]*sc,ice2[i,j]*sc,ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j]
    coda.close(pf)
    return rec

#************************** READ ALTIKA FILES (NETCDF) **************************    


def read_altika_wf(dname,track,coord,d,cycle):

    c = 299792458.0
    B = 480000000.0
    sr = c/(2*B)
    sc = 1.0

# **************************** Find netcdf files *******************************    
    scycle = str(cycle)
    if cycle < 10:
        scycle = '0'+str(cycle)
    
    track = int(track)
    strack = str(track)
    if track < 10:
        strack = '000'+str(track)
    elif track < 100:
        strack = '00'+str(track)
    elif track < 1000:
        strack = '0'+str(track)
    else:
        strack = '0'+str(track)
        
    N1name = dname+'/SRL_*'+scycle+'_'+strack+'*.CNES.nc'
   
    nc_name = glob.glob(N1name)
    if (len(nc_name)==0):
        rec = []
        return rec
    for name in nc_name:
#        print name
        nc = Dataset(name)
    varlist = nc.variables

    geoid_nc = nc.variables['geoid']
    geoid_nc = geoid_nc[:]
    alt0 = nc.variables['alt_40hz']#                  ok interpolated
    latvar = nc.variables['lat_40hz']#                  ok interpolated
    lonvar = nc.variables['lon_40hz']#                  ok interpolated
    lat = latvar[:]
    lon = lonvar[:]-360
    ocean0 = nc.variables['range_40hz']#                ok interpolated
    ice10 = nc.variables['ice1_range_40hz']#            ok interpolated
    ice20 = nc.variables['ice2_range_40hz']#            ok interpolated
    wet0 = nc.variables['model_wet_tropo_corr']#        ok interpol
    dry0 = nc.variables['model_dry_tropo_corr']#        ok interpol
    ion0 = nc.variables['iono_corr_gim']#               ok interpol
    stide0 = nc.variables['solid_earth_tide']#          ok interpol
    ptide0 = nc.variables['pole_tide']#                 ok interpol
    trk0 = nc.variables['tracker_40hz']#                ok interpolated
    second0 = nc.variables['time_40hz']#                ok interpolated
    wf0 = nc.variables['waveforms_40hz']
    wf = np.array(wf0)

    m = 40
    n = shape(alt0)
    n = int(n[0])
#        print 'total number of records:', n
    second = np.zeros((n,m))
    alt = np.zeros((n,m))
    trk = np.zeros((n,m))
    ocean = np.zeros((n,m))
    ice1 = np.zeros((n,m))
    ice2 = np.zeros((n,m))
    day = np.zeros((n,m))
    year = np.zeros((n,m))
    jday = np.zeros((n,m))
    flag = np.ones((n,m))

    lag = 1    
    baseyear = dt.datetime(2000, 1, 1)
    for i in range(0,n):
        ice1[i,:] = np.asarray(ice10[i])
        ice2[i,:] = np.asarray(ice20[i])
        second[i,:] = np.asarray(second0[i])
        ocean[i,:] = np.asarray(ocean0[i])
        alt[i,:] = np.asarray(alt0[i])
        trk[i,:] = np.asarray(trk0[i])
        for j in range(0,m):
            meas = baseyear + dt.timedelta(seconds=second[i,0])
            year[i,j] = meas.year
            jday[i,j] = meas.timetuple().tm_yday

    dry = np.zeros((n,m))
    ion = np.zeros((n,m))
    wet = np.zeros((n,m))
    stide = np.zeros((n,m))
    ptide = np.zeros((n,m))
    rec = []
    lag = 1
#    print 'First coordinate', lat[0,0],lon[0,0]
#    print 'Last  coordinate', lat[n-1,0],lon[n-1,0]
    for i in range(0,n):
        for j in range(0,m):
            dist = abs(lat[i,j]-coord.lat)*111000
            if dist <= d:
#                print dist
# ______________________________ Interpolate ___________________________________
                dab = PyPM.dist_ll(lat[i,0],lon[i,0],lat[i,m-1],lon[i,m-1])
                dab = (dab * lag) + 0.00001
                dc = PyPM.dist_ll(lat[i,j],lon[i,j],lat[i,m-1],lon[i,m-1])
                if j <= m/2:
                    dc = dc * -1
# ______________________________ Interpolate dry tropo __________________________
                za = dry0[i]
                zb = dry0[i+lag]
                dry[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate ion ________________________________
                za = ion0[i]
                zb = ion0[i+lag]
                ion[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate solid earth ________________________
                za = stide0[i]
                zb = stide0[i+lag]
                stide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate polar tide __________________________
                za = ptide0[i]
                zb = ptide0[i+lag]
                ptide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate wet tropo __________________________
                za = wet0[i]
                zb = wet0[i+lag]
                wet[i,j] = PyPM.intepol(za, zb, dab, dc)

                rec.append(SatAlt(alt[i,j],lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j],ocean[i,j],ice1[i,j],ice2[i,j],ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j],track,cycle,wf[i,j,:],geoid_nc[i]))
#                print alt[i,j]*sc,lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j]*sc,ocean[i,j]*sc,\
#                    ice1[i,j]*sc,ice2[i,j]*sc,ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j]
    nc.close()

    return rec

#************************ READ SENTINEL-3 FILES (NETCDF) ************************    


def read_sral_wf(dname,track,coord,d,cycle):

    c = 299792458.0
    B = 350000000.0
    sr = c/(2*B)
    sc = 1.0

# **************************** Find netcdf files *******************************    
    scycle = str(cycle)
    dcycle = str(cycle)
    if cycle < 10:
        scycle = '00'+str(cycle)
    elif cycle < 100:
        scycle = '0'+str(cycle)
    elif cycle < 1000:
        scycle = str(cycle)
    
    track = int(track)
    strack = str(track)
    if track < 10:
        strack = '00'+str(track)
    elif track < 100:
        strack = '0'+str(track)
    elif track < 1000:
        strack = str(track)
    else:
        strack = str(track)
        
    N1name = dname+'/S3A_SR_2_LAN____*'+'_'+strack+'_C'+scycle+'*.nc'
    N2name = dname+'/S3A_SR_2_LAN____*'+'_'+scycle+'_'+strack+'______*.SEN3/enhanced_measurement.nc'
##    print N1name
##    print N2name
   
    nc_name = glob.glob(N1name)
    nc_name += glob.glob(N2name)
##    print nc_name
    if (len(nc_name)==0):
        rec = []
        return rec
    for name in nc_name:
        print name
        nc = Dataset(name)
##    print nc
    varlist = nc.variables
##    for v in varlist:
##        print v

    geoid_nc = nc.variables['geoid_01']
    geoid_nc = geoid_nc[:]
    altvar = nc.variables['alt_20_ku']#                         ok
    alt_20hz = altvar[:] 
    latvar = nc.variables['lat_20_ku']#                         ok
    lonvar = nc.variables['lon_20_ku']#                         ok
    latx = latvar[:]
    lonx = lonvar[:]-360
    lat01 = nc.variables['lat_01']#                         ok
    lon01 = nc.variables['lon_01']#                         ok
    lat01 = lat01[:]
    lon01 = lon01[:]-360
    oceanx = nc.variables['range_ocean_20_ku']#                 ok
    ice1x = nc.variables['range_ocog_20_ku']#                   ok
    ice2x = nc.variables['range_ice_20_ku']#                    ok
    wetx = nc.variables['mod_wet_tropo_cor_meas_altitude_01']#  interpolate
    dryx = nc.variables['mod_dry_tropo_cor_meas_altitude_01']#  interpolate
    ionx = nc.variables['iono_cor_alt_20_ku']#                  ok
    stidex = nc.variables['solid_earth_tide_01']#               interpolate
    ptidex = nc.variables['pole_tide_01']#                      interpolate
    trkx = nc.variables['tracker_range_20_ku']#                 ok
    secondx = nc.variables['time_20_ku']#                       ok
    wfx = nc.variables['waveform_20_ku']

##     20 hz:
    nm = shape(alt_20hz)
    m = 20
    if len(shape(alt_20hz)) == 1:
        m = 20
        tot = int(nm[0]/m)*m
        n = tot/m
    else:
        tot = nm[0] * nm[1]
        n = nm[0]
    ice1 = np.asarray(ice1x[0:tot])
    ice2 = np.asarray(ice2x[0:tot])
    second = np.asarray(secondx[0:tot])
    ocean = np.asarray(oceanx[0:tot])
    ion = np.asarray(ionx[0:tot])
    alt = np.asarray(alt_20hz[0:tot])
    trk = np.asarray(trkx[0:tot])
    lat = np.asarray(latx[0:tot])
    lon = np.asarray(lonx[0:tot])
    wf = np.array(wfx[0:tot])

    if len(shape(alt_20hz)) == 1:
        ice1 = ice1.reshape((tot/m,m))
        ice2 = ice2.reshape((tot/m,m))
        second = second.reshape((tot/m,m))
        ocean = ocean.reshape((tot/m,m))
        ion = ion.reshape((tot/m,m))
        alt = alt.reshape((tot/m,m))
        trk = trk.reshape((tot/m,m))
        lat = lat.reshape((tot/m,m))
        lon = lon.reshape((tot/m,m))
        wf = wf.reshape((tot/m,m,128))
##    print 'wf', shape(wf)
        
##    1 hz:
    dryx = np.asarray(dryx)
    wetx = np.asarray(wetx)
    ptidex = np.asarray(ptidex)
    stidex = np.asarray(stidex)

    print 'total number of records:',nm
    print 'First coordinate', lat[0,0],lon[0,0]
    print 'Last  coordinate', lat[n-1,0],lon[n-1,0]

    year = np.zeros((n,m))
    jday = np.zeros((n,m))
    dry = np.zeros((n,m))
    wet = np.zeros((n,m))
    stide = np.zeros((n,m))
    ptide = np.zeros((n,m))
    lag = 1    
    baseyear = dt.datetime(2000, 1, 1)
    for i in range(0,n):
        for j in range(0,m):
            if second[i,j] > 10000000000:
                second[i,j] = second[i-1,j]
            meas = baseyear + dt.timedelta(seconds=second[i,j])
            year[i,j] = meas.year
            jday[i,j] = meas.timetuple().tm_yday

    rec = []
    lag = 1

    for i in range(0,n):
        for j in range(0,m):
            dist = abs(lat[i,j]-coord.lat)*111000
            if dist <= d:
#                print dist
# ______________________________ Interpolate ___________________________________
                dab = PyPM.dist_ll(lat[i,0],lon[i,0],lat[i,m-1],lon[i,m-1])
                dab = (dab * lag) + 0.00001
                dc = PyPM.dist_ll(lat[i,j],lon[i,j],lat[i,m-1],lon[i,m-1])
                if j <= m/2:
                    dc = dc * -1
# ______________________________ Interpolate dry tropo __________________________
                za = dryx[i]
                zb = dryx[i+lag]
                dry[i,j]= PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate solid earth ________________________
                za = stidex[i]
                zb = stidex[i+lag]
                stide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate polar tide __________________________
                za = ptidex[i]
                zb = ptidex[i+lag]
                ptide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate wet tropo __________________________
                za = wetx[i]
                zb = wetx[i+lag]
                wet[i,j] = PyPM.intepol(za, zb, dab, dc)

                rec.append(SatAlt(alt[i,j],lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j],ocean[i,j],ice1[i,j],ice2[i,j],ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j],track,cycle,wf[i,j,:],geoid_nc[i]))
#                print alt[i,j]*sc,lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j]*sc,ocean[i,j]*sc,ice1[i,j]*sc,ice2[i,j]*sc,ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j]
    nc.close()

    return rec

#************************ READ CRYOSAT-2 SAR FILES (NETCDF) ************************    

def read_cryosat_sar(dname,track,coord,d,cycle):

# **************************** Find netcdf files *******************************    
    scycle = str(cycle)
    if cycle < 10:
        scycle = '00'+str(cycle)
    elif cycle < 100:
        scycle = '0'+str(cycle)
    elif cycle < 1000:
        scycle = ''+str(cycle)
    
    track = int(track)
    strack = str(track)
    if track < 10:
        strack = '00'+str(track)
    elif track < 100:
        strack = '0'+str(track)
    elif track < 1000:
        strack = ''+str(track)
    else:
        strack = ''+str(track)
    print scycle, strack
        
    N1name = dname+'/*CS_*_*_2*_'+'*'+'_'+scycle+'_'+strack+'*.nc'
    print N1name
   
    nc_name = glob.glob(N1name)
    if (len(nc_name)==0):
        rec = []
        return rec
    for name in nc_name:
        print name
        nc = Dataset(name)
    varlist = nc.variables
    for vn in nc.variables:
        print vn
        if vn == 'surf_height_20hz':
            sh_flag = 1
        elif vn == 'surf_height_trkr_1_20hz':
            sh_flag = 2
    print sh_flag
    lon = nc.variables['lon_20hz']
    lon = lon[:]
    lon-=360.0
    lat = nc.variables['lat_20hz']
    lat = lat[:]
    geoid_nc = nc.variables['geoid_eigen6c4']
    geoid_nc = geoid_nc[:]
    secondx = nc.variables['time_20hz']
    if sh_flag == 1:
        alt_20hz = nc.variables['surf_height_20hz']
        alt_20hz = alt_20hz[:]/1000.0
    elif sh_flag == 2:
        alt_20hz = nc.variables['surf_height_trkr_1_20hz']
        alt_20hz = alt_20hz[:]
    for i in range(0, len(alt_20hz)):
        for j in range(0,len(alt_20hz[i])):
            a = alt_20hz[i,j]
            if a<0.0 or a > 7000.0:
                alt_20hz[i,j] = -9999.999

    nm = shape(alt_20hz)
    n = nm[0]
    m = nm[1]
    second = np.zeros((n,m))
    alt = np.zeros((n,m))
    day = np.zeros((n,m))
    year = np.zeros((n,m))
    jday = np.zeros((n,m))
    ice1 = np.zeros((n,m))
    ice2 = np.zeros((n,m))
    ocean = np.zeros((n,m))
    ion = np.zeros((n,m))
    dry = np.zeros((n,m))
    wet = np.zeros((n,m))
    stide = np.zeros((n,m))
    ptide = np.zeros((n,m))
    trk = np.zeros((n,m))
    wf = np.zeros((n,m,1))
    rec = []

    baseyear = dt.datetime(2000, 1, 1)
    for i in range(0,n):
        alt[i,:] = np.asarray(alt_20hz[i])
        second[i,:] = np.asarray(secondx[i])
        for j in range(0,m):
            meas = baseyear + dt.timedelta(seconds=second[i,0])
            year[i,j] = meas.year
            jday[i,j] = meas.timetuple().tm_yday
        rec.append(SatAlt(alt[i,j],lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j],ocean[i,j],ice1[i,j],ice2[i,j],ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j],track,cycle,wf[i,j,:],geoid_nc[i]))
    nc.close()
    return rec

#************************ READ JASON FILES (NETCDF with wf) ************************    

def read_jason(dname,track,coord,d,cycle):
    track = int(track)
    c = 299792458.0
    B = 480000000.0
    sr = c/(2*B)
    sc = 1.0

# **************************** Find netcdf files *******************************    
    scycle = str(cycle)
    if cycle < 10:
        scycle = '00'+str(cycle)
    elif cycle < 100:
        scycle = '0'+str(cycle)
    elif cycle < 1000:
        scycle = str(cycle)
    
    strack = str(track)
    if track < 10:
        strack = '00'+str(track)
    elif track < 100:
        strack = '0'+str(track)
    elif track < 1000:
        strack = str(track)
    else:
        strack = str(track)
        
    N1name = dname+'/JA*'+scycle+'_*'+strack+'*.nc'
    print N1name
   
    nc_name = glob.glob(N1name)
    if (len(nc_name)==0):
        rec = []
        return rec
    for name in nc_name:
##        print name
        nc = Dataset(name)
##    print nc
    varlist = nc.variables
##    for v in varlist:
##        print v

    geoid_nc = nc.variables['geoid']
    geoid_nc = geoid_nc[:]
    alt0 = nc.variables['alt_20hz']#                  ok interpolated
    latvar = nc.variables['lat_20hz']#                  ok interpolated
    lonvar = nc.variables['lon_20hz']#                  ok interpolated
    lat = latvar[:]
    lon = lonvar[:]
    ocean0 = nc.variables['range_20hz_ku']#                ok interpolated
    ice10 = nc.variables['ice_range_20hz_ku']#            ok interpolated
    wet0 = nc.variables['model_wet_tropo_corr']#        ok interpol
    dry0 = nc.variables['model_dry_tropo_corr']#        ok interpol
    ion0 = nc.variables['iono_corr_gim_ku']#               ok interpol
    stide0 = nc.variables['solid_earth_tide']#          ok interpol
    ptide0 = nc.variables['pole_tide']#                 ok interpol
    trk0 = nc.variables['tracker_20hz_ku']#                ok interpolated
    second0 = nc.variables['time_20hz']#                ok interpolated
    wf0 = nc.variables['waveforms_20hz_ku']
    wf = np.array(wf0)
    [n,m] = shape(alt0)
##    print 'shape',n,m


    second = np.zeros((n,m))
    alt = np.zeros((n,m))
    trk = np.zeros((n,m))
    ocean = np.zeros((n,m))
    ice1 = np.zeros((n,m))
    ice2 = np.zeros((n,m))
    day = np.zeros((n,m))
    year = np.zeros((n,m))
    jday = np.zeros((n,m))
    flag = np.ones((n,m))

    baseyear = dt.datetime(2000, 1, 1)
    for i in range(0,n):
        ice1[i,:] = np.asarray(ice10[i])
        second[i,:] = np.asarray(second0[i])
        ocean[i,:] = np.asarray(ocean0[i])
        alt[i,:] = np.asarray(alt0[i])
        trk[i,:] = np.asarray(trk0[i])
        for j in range(0,m):
            meas = baseyear + dt.timedelta(seconds=second[i,0])
            year[i,j] = meas.year
            jday[i,j] = meas.timetuple().tm_yday

    dry = np.zeros((n,m))
    ion = np.zeros((n,m))
    wet = np.zeros((n,m))
    stide = np.zeros((n,m))
    ptide = np.zeros((n,m))
    rec = []
    lag = 1
##    print 'First coordinate', lat[0,0],lon[0,0]
##    print 'Last  coordinate', lat[n-1,0],lon[n-1,0]
    for i in range(0,n):
        for j in range(0,m):
            lon[i,j] = 360.0-lon[i,j]
            dist = abs(lat[i,j]-coord.lat)*111000
            if dist <= d:
##                print dist, alt[i,j]
# ______________________________ Interpolate ___________________________________
                dab = PyPM.dist_ll(lat[i,0],lon[i,0],lat[i,m-1],lon[i,m-1])
                dab = (dab * lag) + 0.00001
                dc = PyPM.dist_ll(lat[i,j],lon[i,j],lat[i,m-1],lon[i,m-1])
                if j <= m/2:
                    dc = dc * -1
# ______________________________ Interpolate dry tropo __________________________
                za = dry0[i]
                zb = dry0[i+lag]
                dry[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate ion ________________________________
                za = ion0[i]
                zb = ion0[i+lag]
                ion[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate solid earth ________________________
                za = stide0[i]
                zb = stide0[i+lag]
                stide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate polar tide __________________________
                za = ptide0[i]
                zb = ptide0[i+lag]
                ptide[i,j] = PyPM.intepol(za, zb, dab, dc)
# ______________________________ Interpolate wet tropo __________________________
                za = wet0[i]
                zb = wet0[i+lag]
                wet[i,j] = PyPM.intepol(za, zb, dab, dc)

                rec.append(SatAlt(alt[i,j],lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j],ocean[i,j],ice1[i,j],ice1[i,j],ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j],track,cycle,wf[i,j,:],geoid_nc[i]))
#                print alt[i,j]*sc,lat[i,j],lon[i,j],year[i,j],jday[i,j],trk[i,j]*sc,ocean[i,j]*sc,\
#                    ice1[i,j]*sc,ice2[i,j]*sc,ion[i,j],dry[i,j],wet[i,j],stide[i,j],ptide[i,j]
    nc.close()

    return rec

# _____________________________________ Create alti point shapefile ____________________________________

def gen_point_shape_alti(name, lon, lat, field1, field2, field3, field4, field5, state):
    
    shpname = name + '.shp'
    if state == 1:
        r = shapefile.Reader(shpname)
        w = shapefile.Writer(r.shapeType)
        w.fields = list(r.fields)
        w.records.extend(r.records())
        w._shapes.extend(r.shapes())
    else:
        w = shapefile.Writer(shapeType=1)
        w.autoBalance = 1
        w.field('Number','N', 20,0)
        w.field('CYCLE','C', 7,0)
        w.field('TRACK','N', 7,0)
        w.field('Date','C', 11)
        w.field('ICE1','N', 20,3)
        w.field('LAKE1','N', 20,3)
    for i in range(0,len(lon)):
        w.point(lon[i],lat[i])
        w.record(i+1,field1, field2, field3[i], field4[i], field5[i])
    w.save(shpname)
    w = None
    
    epsg = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    prjname = name + '.prj'
    prj = open(prjname, "w")
    prj.write(epsg)
    prj.close()

# _____________________________________ Create line shapefile ____________________________________

def gen_line_shape(name, chain, field1, field2, field3, field4, state):
    
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
# ________________________________________ Retracker Lake1 ____________________________________________

def lake1(wf,trk,cgate,B):

    c = 299792458.0
    sr = c/(2*B)

    scale = 10

    wf1 = np.zeros(128)
    count_wf = 0

    count = 0
    count_peaks = 0
    wfo = wf
    minamp = max(wfo)*0.1
    gate = 0
    for j in range(1,126):
        if wfo[j] > wfo[j-1] and wfo[j] > wfo[j+1] and wfo[j] >= minamp:
            count_peaks += 1
        p1 = PyPM.XYZ((j-1),wfo[j-1]/scale,0)
        p2 = PyPM.XYZ((j+1),wfo[j+1]/scale,0)
        pc = PyPM.XYZ((j),wfo[j]/scale,0)
        ang = PyPM.find_angle_2d(p1,p2,pc)
        if (ang < 45 or ang > 315):# and wfo[j] >= minamp):
            count += 1
            wf1[j] = wfo[j]
            peak = count_peaks
            gate = j
        else:
            wf1[j] = 0
    if count == 1:
        count_wf += 1
        if peak <= 3:
 #           print gate, trk + ((cgate-gate)*sr)
            return float(trk + ((cgate-gate)*sr))
        else:
            return -1.0
    else:
        return -1.0

# ________________________________________ Retracker Lake2 ____________________________________________

def lake2(wf,trk,cgate,f):

    c = 299792458.0
    sr = c/(2*f)
    wff = np.zeros(len(wf))
    wfff = np.zeros(len(wf))

    count_peaks = 0
    for j in range(1,len(wf)-1):
        wff[j] = (2 * wf[j]) - (wf[j-1]+wf[j+1])
    for j in range(1,128):
        if wff[j-1] < 0 and wff[j]>0 and wff[j]>(max(wff)/5):
            wfff[j] = wff[j]
        else:
            wfff[j] = 0

    indices = np.nonzero(wfff)
    count_peaks = indices[0]
#    print shape(indices), count_peaks, indices[0]
#    plt.plot(wff,'b-')

    if len(count_peaks) <= 3 and len(count_peaks) > 0:
        gate = count_peaks[0]
        if wf[gate] > 250:
            return float(trk + ((cgate-gate)*sr))
    else:
        return -1.0

# ________________________________________ Simplify waveform ____________________________________________

def simplify_wf(wf, show):
    wfx = []
    wfy = []
    wfy.append(wf[0])
    wfx.append(0)
    minarea = (3000 * 1/max(wf))**2
    j1 = 0
    j2 = 1
    j3 = 2
    while j3 < 127:
        area = ((j1-j2)*((wf[j1]-wf[j2])/2))+((j2-j3)*((wf[j2]-wf[j3])/2))+((j3-j1)*((wf[j3]-wf[j1])/2))
        if abs(area) < minarea:
            j2+=1
            j3+=1
        else:
            wfy.append(wf[j2])
            wfx.append(j2)
            j1=j2
            j2=j3
            j3+=1
    wfy.append(wf[127])
    wfx.append(127)
    wfy2 = []
    for i in range(0,len(wfx)-1):
        wfy2.append(wfy[i])
        for j in range(1,wfx[i+1]-wfx[i]):
            val = wfy[i] + (((wfy[i+1]-wfy[i]) / (wfx[i+1]-(wfx[i])))*j)
            wfy2.append(val)
#            print wfx[i],j, val
    wfy2.append(wf[127])
    fig = 1
    if show == 1:
        plt.figure(fig,figsize=(16,12), dpi=80)
        plt.subplot(1,2,1)
        plt.plot(wf,'r-')
        plt.subplot(1,2,2)
        plt.plot(wfy2,'g-')
        plt.plot(wfy2,'go')
        plt.show()
    return wfy2

# ________________________________________ Waveform Sorted Peaks _______________________________________

def wf_sorted_peaks(wf,wfh):
    wfp = []
    wfhp = []
    w = []
    wfm = float(max(wf))
    lim = wfm/5.0
    n = float(len(wf))
    for i in range(1,len(wf)-1):
        if wf[i] > wf[i-1] and wf[i] > wf[i+1] and wf[i] > lim:
#            wfp.append(wf[i])
            temp = ((float(wf[i])) * (((n-float(i))/n)**4.0))
            w.append(temp)
            wfp.append(float(wf[i]))
            wfhp.append(wfh[i])

    for i in range(0,len(wfp)):
        for j in range(i, len(wfp)):
            if w[i] < w[j]:
                temp = w[i]
                w[i] = w[j]
                w[j] = temp
                temp = wfp[i]
                wfp[i] = wfp[j]
                wfp[j] = temp
                temp = wfhp[i]
                wfhp[i] = wfhp[j]
                wfhp[j] = temp
                
##    cml = PyPM.lut2()
##    plt.plot(wf,'k-')
##    for i in range(0,len(wfp)):
##        plt.plot(10, wfp[i],cml[i],ms=12-i)
##    plt.show()
##    print wfp, wfhp
    return wfhp

    
    



