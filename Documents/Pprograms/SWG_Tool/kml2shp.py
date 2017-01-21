import SWG_Altisat as PyAsat
import SWG_PyPM as PyPM

##nome = '/home/philippe/Documentos/Jason/track_jason3.shp'
##nome_out = nome.replace('.shp', '_sm.shp')
##print nome_out
##tracks = PyPM.read_tracks(nome)
##
##state = 0
##d_ref = 1000000.0
##for i in range(0,len(tracks)):
##    ch = []
##    ch.append([tracks[i].v[0].x1,tracks[i].v[0].y1])
##    xref = tracks[i].v[0].x1
##    yref = tracks[i].v[0].y1
##    for j in range(0,len(tracks[i].v)):
##        xnew = tracks[i].v[j].x2
##        ynew = tracks[i].v[j].y2
##        d = PyPM.dist_ll(yref,xref,ynew,xnew)
####        print d
##        if d >= d_ref:
##            ch.append([xnew,ynew])
##            xref = xnew
##            yref = ynew
####    print len(tracks[i].v), len(ch)
##    ch = [ch]
##    PyAsat.gen_line_shape(nome_out, ch, i+1, 0, 0, 0, state)
##    state = 1

kmlfile = '/home/philippe/Documentos/Cryosat/Visu_C2_Tracks_HiRes.kml'
shpfile = kmlfile.replace('.kml', '.shp')
try:
    f = open(kmlfile,'rt')
except IOError:
    sys.exit()

state = 0
ntracks = 0
t = f.readline()
while t != '' and ntracks < 500000:
    while t[0:15] != '<styleUrl>#LINE':
        t = f.readline()
    ch = []
    t = f.readline()
    t1 = t.split()
    t2 = t1[len(t1)-1].split('<')
    track = int(t2[0])
    while t[0:13] != '<coordinates>':
        t = f.readline()
    t = f.readline()
    count = 0
    while t[0:14] != '</coordinates>':
        count += 1
        if count == 5:
            c = t.split(',')
            ch.append([float(c[0]),float(c[1])])
            count = 0
        t = f.readline()
    if ntracks%100 == 0:
        print 'track', track, len(ch)
    ch = [ch]
    PyAsat.gen_line_shape(shpfile, ch, track, 0, 0, 0, state)
    ntracks+=1
    state = 1
f.close()

    



