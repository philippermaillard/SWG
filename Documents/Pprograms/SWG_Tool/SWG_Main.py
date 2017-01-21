import numpy
import sys
from math import cos, sin, acos
from pylab import *
import datetime as dt
import copy
import struct
import glob
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
import matplotlib.image as mpimg
import shapefile
import SWG_PyPM as PyPM

def rmsd(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def VHS(path,tab_file,txt_file,dem_path,s_file,year,stabase,geoid,dmax,threshold,style,tt,relief,sfr,wtype,alltab):
    tabs = []
    if alltab:
        tabs = glob.glob(path+'/*.tab')
        tabs.sort()
        try:
            fout = open(path+'/all_out.txt','wt')
        except IOError:
          print "There was an error opening file ", path+'/all_out.txt'
          sys.exit()        
    else:
        tabs.append(tab_file)
        foutname = tab_file.replace('.tab','out.txt')
        try:
            fout = open(foutname,'wt')
        except IOError:
          print "There was an error opening file ", foutname
          sys.exit()        
    for tab_file in tabs:
        print tab_file
    #  Get or define parameters
    # _________________________________________________________________________________________________

        threshold = float(threshold)
        whatyear = int(year)
        base = float(stabase)
        geoid_corr = float(geoid)
        s_year = 1990
        e_year = 2010#dt.datetime.now().year
        dist_max = float(dmax)
        if dist_max < 5000 and style == 'w':
            dist_max = 5000
    #  Read the satellite tab file
    # _________________________________________________________________________________________________

        virsta = []

        virsta = PyPM.read_tab(tab_file)
        ncycles = len(virsta)
        if len(virsta) > 0:
            sat_alt = np.mean(virsta[0].alt)
            e_year = virsta[ncycles-1].hdate.year
        # _________________________________________ mid coordinates of track points________________________
            midy = 0.0
            midx = 0.0
            for i in range(0,ncycles):
                midy+= np.mean(virsta[i].lat)
                midx+= np.mean(virsta[i].lon)
            midx = midx / ncycles
            midy = midy / ncycles

        #  Read the shape file of the river
        # _________________________________________________________________________________________________

            sf = shapefile.Reader(str(s_file))
            s_file = s_file.replace('.shp','')

        #  Read the CPRM files (if present)
        # _________________________________________________________________________________________________

            PyPM.read_cprm(txt_file,virsta)

        # _________________________________________________________________________________________________
                        
            waterbody = PyPM.read_waterbody(s_file)
            first_lat = 0.
            first_lon = 0.
            last_lat = 0.
            last_lon = 0.
            n_plotcycle = 0
        else:
            print 'File', tab_file, 'contains no data; skipped'
        for i0 in range(0,ncycles):
##            print 'points:', virsta[i0].nh
            if virsta[i0].cycle%10==0:
                print 'processing cycle', virsta[i0].cycle
            last = virsta[i0].nh-1
            track_section = PyPM.Vertice(virsta[i0].lon[0],virsta[i0].lat[0], virsta[i0].lon[last],virsta[i0].lat[last], str(virsta[i0].cycle))
##            print track_section.x1, track_section.y1,track_section.x2,track_section.y2
            px = []
            for j0 in range(0,len(waterbody)):
                for m0 in range(0,virsta[i0].nh):
                    if PyPM.ponto_em_poligono(PyPM.Point(virsta[i0].lon[m0],virsta[i0].lat[m0]), waterbody[j0]):
                        virsta[i0].d2w[m0] = 0
                for k0 in range(0,len(waterbody[j0].v)):# para cada vertice de cada poligono
                    p = PyPM.cross_point_vector(track_section, waterbody[j0].v[k0])# determinas o ponto de cruzamento entre o vertice da
                    if p.x != -99999.99999 and p.y != -99999.99999:# verificar se existe um ponto de encontro
                        a = PyPM.ponto_na_linha(p,track_section)# verificar se o ponto de encontro pertence ao vertice da linha
                        b = PyPM.ponto_na_linha(p,waterbody[j0].v[k0])# verificar se o ponto de encontro pertence ao vertice do poligono
                        if a and b:# caso o ponto de encontro pertence aos dois vertice
                            px.append(p)
            if len(px) < 2:
                virsta[i0].nh = 0
                print 'Cycle ', virsta[i0].cycle, 'has been skipped'
            else:
                PyPM.sort_point_north(px)
                additional_d = PyPM.dist_ll(px[0].y, px[0].x, px[len(px)-1].y, px[len(px)-1].x)/2.
            for m0 in range(0,virsta[i0].nh):
                if virsta[i0].d2w[m0] == -1:
                    dref = 100000.0
                    mean_x = 0.
                    mean_y = 0.
                    for p in px:
                        d = PyPM.dist_ll(virsta[i0].lat[m0], virsta[i0].lon[m0], p.y, p.x)
                        mean_y += p.y
                        mean_x += p.x
                        if d < dref:
                            dref = d
                    virsta[i0].d2w[m0] = dref
                    virsta[i0].m_lat = mean_y/len(px)
                    virsta[i0].m_lon = mean_x/len(px)
            if relief and int(virsta[i0].hdate.year) == whatyear:
                n_plotcycle+=1
                first_lat += virsta[i0].lat[0]
                first_lon += virsta[i0].lon[0]
                last_lat += virsta[i0].lat[last]
                last_lon += virsta[i0].lon[last]
                    
        totwh = []
        totcal = []
        totdate = []

    #  Get Profile data from DEM
    # _________________________________________________________________________________________________
        if relief:
            coor2 = PyPM.Lat_Lon(first_lat/n_plotcycle,first_lon/n_plotcycle)
            coor1 = PyPM.Lat_Lon(last_lat/n_plotcycle,last_lon/n_plotcycle)
            print coor1.lat, coor1.lon, '\n', coor2.lat, coor2.lon
            if coor2.lon < coor1.lon: 
                t_profile = PyPM.split_profile(coor1, coor2, dem_path)
            else:
                t_profile = PyPM.split_profile(coor2, coor1, dem_path)
    ##        profile = PyPM.get_profile(dem_path, coor1, coor2)
    ##        print coor1.lat, coor1.lon, coor2.lat, coor2.lon

    # VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
        cml = PyPM.lut()
        count = 0
        lons = []
        lats = []
        lonsb = []
        latsb = []

        for i in range(0,ncycles):
            lat0 = virsta[i].m_lat
                        
    #  Process elevation data and determine distance from the river cossing point        
            d = []
            alt = []
            d1 = []
            h1 = []
            d2 = []
            h2 = []

            if lat0 != -999:
                PyPM.filter_peaks(virsta[i])
                for j in range(0,virsta[i].nh):
                    if virsta[i].lat[j] > virsta[i].m_lat:
                        sign = (-1)
                    else:
                        sign = 1
                    d.append(virsta[i].d2w[j] * sign)
                    if virsta[i].d2w[j] <= dist_max + additional_d:
                        if virsta[i].lat[j] > virsta[i].m_lat:
                            h2.append(virsta[i].h[j])
                            d2.append(virsta[i].d2w[j] + additional_d)
                        else:
                            h1.append(virsta[i].h[j])
                            d1.append(virsta[i].d2w[j] + additional_d)
                d1 = np.array(d1)
                h1 = np.array(h1)
                d2 = np.array(d2)
                d2*=(-1)
                h2 = np.array(h2)
                scale = 1000000

    # ---------------------------------------------- pattern recognition -----------------------------------
                if style == 'w':
                    a = PyPM.bestpointsubset(d1,h1)
                    fname_r = PyPM.rule_classifier_right([float(a[1]*scale), float(a[2]*scale), float(a[4]*scale), float(a[1]/a[2])])
                    expo_r = PyPM.determine_exponent(fname_r)
                    for gg in range(0,len(d1)):
                        h1[gg] = a[0]+(a[1]*d1[gg])+(a[2]*d1[gg]*d1[gg])
                    a = PyPM.bestpointsubset(d2,h2)
                    fname_l = PyPM.rule_classifier_left([float(a[1]*scale), float(a[2]*scale), float(a[4]*scale), float(a[1]/a[2])])
                    expo_l = PyPM.determine_exponent(fname_l)
                    for gg in range(0,len(d2)):
                        h2[gg] = a[0]+(a[1]*d2[gg])+(a[2]*d2[gg]*d2[gg])

    # ---------------------------------------------- river width --------------------------------------
                elif style == 'a':
                    expo_r = 1
                    expo_l = 1
                    fname_l = '_'
                    fname_r = '_'

    # ---------------------------------------------- hooking fitting -----------------------------------
                elif style == 'h':
                    hk = PyPM.simulate_hooking(sat_alt,min(virsta[i].h),virsta[i],sf,sfr,dist_max,midx,midy)
                    hk = PyPM.fit_hook_idw(hk,virsta[i].h,d)
                    hks = PyPM.simulate_hooking_inverse(sat_alt,hk,virsta[i],sf,sfr,dist_max,midx,midy)
                    expo_r = 1
                    expo_l = 1
                    fname_l = '_'
                    fname_r = '_'
    # --------------------------------------------------------------------------------------------------
                if len(d1) > 0:
                    whr = PyPM.idw_average(d1,h1,expo_r)
                if len(d2) > 0:
                    whl = PyPM.idw_average(d2,h2,expo_l)
                if len(d1) > 0 and len(d2) > 0:
                    wh = (whr+whl)/2
                elif len(d1) == 0 and len(d2) > 0:
                    wh = whl
                elif len(d2) == 0 and len(d1) > 0:
                    wh = whr
                else:
                    wh = 0
                if style == 'h':
                    wh = np.mean(hks[np.nonzero(hks)])
            virsta[i].wh = wh
            totwh.append(wh)
            totcal.append(virsta[i].cal)
            totdate.append(virsta[i].hdate)
            s = '%s %.5f %.5f %.3f\n' % (str(virsta[i].hdate), virsta[i].m_lat, virsta[i].m_lon, virsta[i].wh)
            fout.write(s)
                
                
#                                           Plot selected year        
# _________________________________________________________________________________________________

            
            if int(virsta[i].hdate.year) == whatyear or whatyear < 0:
                print virsta[i].hdate, wh

            if int(virsta[i].hdate.year) == whatyear:
                plt.figure('Altimetric Profile')
                count+=1
                plt.plot(d1,h1,'k-',lw=2)
                plt.plot(d2,h2,'k-',lw=2)
                plt.plot(d,virsta[i].h,cml[count],lw=1)
                
                if style == 'h':
                    sim = []
                    sim_c = []
                    dd = []
                    for k in range(0, len(hk)):
                        if hk[k] > 0:
                            sim.append(hk[k])
                            sim_c.append(hks[k])
                            dd.append(d[k])
                    plt.plot(dd,sim,'r.',dd,sim_c,'g.',lw=2)
                
                plt.xlabel("Distance (m)\n", fontsize=18)
                plt.ylabel("Altitude (m)", fontsize=18)
                plt.xlim(-3000,3000)
                tick_params(axis='both',labelsize=18)
                minh = min(virsta[i].h)
                maxh = max(virsta[i].h)
                maxalt = maxh
                plt.plot([0,0],[minh,maxh], 'k-')
                t = tab_file.split('/')
                t = t[len(t)-1].split('.')
                titlestring = t[len(t)-2] + ' (' + str(virsta[i].hdate.year) + ')'

# ________________________________________ Plot relief ________________________________________________
                if relief and count == 1:
                    ini = d[0]
                    fin = d[len(d)-1]
                    step = (fin-ini)/float(len(t_profile))
                    dprof = np.arange(ini,fin,step)
##                    print ini,fin,step,len(t_profile), len(dprof)
##                    plt.figure('Terrain Profile')
                    plt.fill_between(dprof,t_profile,color='r',facecolor='y', alpha=0.4)
##                    plt.plot(dprof,t_profile,'k-')
                    plt.xlim(-3000,3000)
                    plt.ylim(minh,max(t_profile))

                loz = []
                laz = []
                for j in range(0,virsta[i].nh):
                    loz.append(virsta[i].lon[j])
                    laz.append(virsta[i].lat[j])
                lons.append(loz)
                lats.append(laz)
                lonsb.append(virsta[i].m_lon)
                latsb.append(virsta[i].m_lat)
                

                totwha = np.array(totwh)
                totcala = np.array(totcal)
                if tt:
                    
                    totwhsorted = np.sort(totwh)
                    top3rd = totwhsorted[int(round(len(totwh)*.666))-1]
                    totwh_tt = []
                    totcal_tt = []
                    for j in range(0, len(totwh)):
                        if totwh[j] <= top3rd:
                            totwh_tt.append(totwha[j])
                            totcal_tt.append(totcala[j])
                    totwh_tt = np.array(totwh_tt)
                    totcal_tt = np.array(totcal_tt)
                    totcala+= rmsd(totwh_tt, totcal_tt)
                    print 'RMSE:', rmsd(totwha, totcala)
                else:
                    totcala+= rmsd(totwha, totcala)
                    print 'RMSE:', rmsd(totwha, totcala)
                ref_curve = PyPM.average_level(txt_file, s_year, e_year)
                fig = plt.figure(3)
                fig.suptitle('Times Water Level Series')
                tplot = plt.subplot(2,1,1)
                tplot.set_title('Absolute water level elevation')
                tplot.plot(totdate, totwha, 'k-')
                
                if txt_file != '-':
                    tplot.plot(totdate, totcala, 'b--')
                    bplot = plt.subplot(2,1,2)
                    bplot.set_title('Water level difference')
                    bplot.plot(totdate, totwha-totcala, 'k-')
                

            # **********************************************   BASE MAP    *****************************************
            # ____________________________________________ Plot general view _______________________________________
            if int(virsta[i].hdate.year) == whatyear:
                mg = 0.3
                llx = sf.bbox[0]-mg
                lly = sf.bbox[1]
                urx = sf.bbox[2]+mg
                ury = sf.bbox[3]
                cx = (sf.bbox[0] + sf.bbox[2])/2
                cy = (sf.bbox[1] + sf.bbox[3])/2

                fig = plt.figure('Overview')
                ax = fig.add_subplot(111)
                map = Basemap(llcrnrlon=llx,llcrnrlat=lly,urcrnrlon=urx,urcrnrlat=ury,projection='tmerc', lat_0=cy, lon_0=cy)

                map.drawmapboundary(fill_color='aqua')
                map.fillcontinents(color='#d7e5ae',lake_color='aqua')
                map.drawcoastlines()
                map.readshapefile(s_file, 'rsf')
                patches   = []

                for info, shape in zip(map.rsf_info, map.rsf):
                    patches.append( Polygon(np.array(shape), True) )
                ax.add_collection(PatchCollection(patches, facecolor= '#bfe1e5', edgecolor='k', linewidths=0.1, zorder=2))
                map.drawparallels(np.arange(0.,-81.,-1.), labels=[0,1,0,0], fontsize=10)
                map.drawmeridians(np.arange(-180.,181.,1.), labels=[0,0,0,1], fontsize=10)
                for i in range(0,len(lons)):
                    mx, my = map(lons[i], lats[i])
                    s = cml[i]
                    co = s[0]
                    mk = s[1]
                    map.plot(mx, my, marker=mk,color=co)
                mx, my = map(lonsb, latsb)
                map.plot(mx, my, marker='D',color='K',ls='None',ms=10)

            # ____________________________________________ Plot detailed view ______________________________________________

                mg = 0.2
                llx = min(lons[0])-mg
                lly = min(lats[0])
                urx = max(lons[0])+mg
                ury = max(lats[0])
                cx = (llx + urx)/2
                cy = (lly + ury)/2

                fig = plt.figure('Zoom view')
                ax = fig.add_subplot(111)
                map = Basemap(llcrnrlon=llx,llcrnrlat=lly,urcrnrlon=urx,urcrnrlat=ury,projection='tmerc', lat_0=cy, lon_0=cy)
                map.fillcontinents(color='#d7e5ae')

                map.readshapefile(s_file, 'rsf')
                patches   = []

                for info, shape in zip(map.rsf_info, map.rsf):
                    patches.append( Polygon(np.array(shape), True) )
                ax.add_collection(PatchCollection(patches, facecolor= '#bfe1e5', edgecolor='k', linewidths=0.1, zorder=2))
                map.drawparallels(np.arange(0.,-81.,-0.1), labels=[0,1,0,0], fontsize=10)
                map.drawmeridians(np.arange(-180.,181.,0.1), labels=[0,0,0,1], fontsize=10)
                
                for i in range(0,len(lons)):
                    mx, my = map(lons[i], lats[i])
                    s = cml[i]
                    co = s[0]
                    mk = s[1]
                    map.plot(mx, my, marker=mk,color=co)
                mx, my = map(lonsb, latsb)
                map.plot(mx, my, marker='D',color='K',ls='None',ms=10)
    fout.close()
    plt.show()
# ______________________________________________________________

