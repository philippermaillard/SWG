import sys
import datetime as dt
import time
import os
import SWG_Main as SWG_Cycle
import Tkinter as tk
from Tkinter import *
import tkFileDialog, Tkconstants
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import SWG_Altisat as PyAltisat
import SWG_PyPM as PyPM

class Sapp_tk(tk.Tk):
    def __init__(self,parent,path,tabname,txtname,bilpath,shapename):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.path = path
        self.tabname = tabname
        self.txtname = txtname
        self.bilpath = bilpath
        self.shapename = shapename
        self.file_opt = options = {}
        options['initialdir'] = path
        options['parent'] = parent
        options['title'] = 'Pick you file'

        self.initialize()
    
    def initialize(self):
        self.grid()
        self.year = -9999
        self.geoide = 0.0
##        self.base = -9999.
        self.tthird = 0
        self.relief = 0
        self.distmax = 1000
        self.tolerance = 10.0
        self.style = "h"
        self.sfr = 4000.0
        self.type = "r"

# ___________________________________________ WIGETS _________________________________________
        lblue = "#ddddddfff"
        bluegrey = "#aaaaaafff"
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry("500x300"))
        
        background_image = PhotoImage(file = "water.gif")
        background_label = tk.Label(self, image=background_image)
        background_label.photo = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

#   GET PATH
        self.label_Path = tk.StringVar()
        label = tk.Label(self,textvariable=self.label_Path,anchor="w",bg=lblue)
        label.grid(column=0,row=0,columnspan=1,sticky='EW')
        self.label_Path.set(u"General File Path: ")
        self._Path_var = tk.StringVar()
        label = tk.Label(self,textvariable=self._Path_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        label.grid(column=1,row=0,columnspan=1,sticky='W',padx=1)
        self._Path_var.set(self.path)

        button0 = tk.Button(self,text=u"Change Path",command=self.OnButtonClick_Path)
        button0.grid(column=2,row=0)

#   GET SATELLITE FILE
        self._Tab_label = Label(self, text = "Satellite TAB File (leave empty for all)",anchor="w",bg=lblue)
        self._Tab_label.grid(column=0,row=1,columnspan=1,sticky='EW')
        self._Tab_var = StringVar()
        self._Tab_var_label = Label(self,textvariable=self._Tab_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self._Tab_var_label.grid(column=1,row=1,columnspan=1,sticky='W',padx=1)
        self._Tab_var.set(self.tabname)

        button1 = tk.Button(self,text=u"Change  File",command=self.OnButtonClick_Tab)
        button1.grid(column=2,row=1)

#   GET CALIBRATION FILE
        self._Caltxt_label = Label(self, text = "Calibration TXT File",anchor="w",bg=lblue)
        self._Caltxt_label.grid(column=0,row=2,columnspan=1,sticky='EW')
        self._Caltxt_var = StringVar()
        self._Caltxt_var_label = Label(self,textvariable=self._Caltxt_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self._Caltxt_var_label.grid(column=1,row=2,columnspan=1,sticky='W',padx=1)
        self._Caltxt_var.set(self.txtname)

        button2 = tk.Button(self,text=u"Change File",command=self.OnButtonClick_Txt)
        button2.grid(column=2,row=2)

#   GET DEM FILE
        self._DEM_label = Label(self, text = "DEM File Path",anchor="w",bg=lblue)
        self._DEM_label.grid(column=0,row=3,columnspan=1,sticky='EW')
        self._DEM_var = StringVar()
        self._DEM_var_label = Label(self,textvariable=self._DEM_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self._DEM_var_label.grid(column=1,row=3,columnspan=1,sticky='W',padx=1)
        self._DEM_var.set(self.bilpath)

        button3 = tk.Button(self,text=u"Change Path",command=self.OnButtonClick_Hdr)
        button3.grid(column=2,row=3)

#   GET SHAPE FILE
        self._Shape_label = Label(self, text = "Shape File",anchor="w",bg=lblue)
        self._Shape_label.grid(column=0,row=4,columnspan=1,sticky='EW')
        self._Shape_var = StringVar()
        self._Shape_var_label = Label(self,textvariable=self._Shape_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self._Shape_var_label.grid(column=1,row=4,columnspan=1,sticky='W',padx=1)
        self._Shape_var.set(self.shapename)

        button3 = tk.Button(self,text=u"Change File",command=self.OnButtonClick_Shp)
        button3.grid(column=2,row=4)

#   GET YEAR
        self._Year_label = Label(self, text = "Year to Plot (leave empty if none)",anchor="w",bg=lblue)
        self._Year_label.grid(column=0,row=5,columnspan=1,sticky='EW')
        self._Year_var = IntVar()
        self._Year_var.set(2002)
        self._Year_entry = Entry(self,textvariable=self._Year_var,width=10)
        self._Year_entry.grid(column=1,row=5,sticky='W',padx=1)

#   GET GEOIDE CORRECTION
        self._Geoid_label = Label(self, text = "Geoide correction factor",anchor="w",bg=lblue)
        self._Geoid_label.grid(column=0,row=6,columnspan=1,sticky='eW',padx=1)
        self._Geoid_var = DoubleVar()
        self._Geoid_entry = Entry(self,textvariable=self._Geoid_var,width=10)
        self._Geoid_entry.grid(column=1,row=6,sticky='W',padx=1)

#   GET BASE LEVEL CORRECTION
        self._Baselevel_label = Label(self, text = "Base level of station in m (negative for auto)",anchor="w",bg=lblue)
        self._Baselevel_label.grid(column=0,row=7,columnspan=1,sticky='EW',padx=1)
        self._Baselevel_var = DoubleVar()
        self._Baselevel_var.set(-9999.)
        self._Baselevel_entry = Entry(self,textvariable=self._Baselevel_var,width=10)
        self._Baselevel_entry.grid(column=1,row=7,sticky='W',padx=1)

#   GET MAXIMUM DISTANCE
        self._Maxdist_label = Label(self, text = "Maximum distance from river centerline (1000)",anchor="w",bg=lblue)
        self._Maxdist_label.grid(column=0,row=8,columnspan=1,sticky='EW')
        self._Maxdist_var = DoubleVar()
        self._Maxdist_var.set(1000.0)
        self._Maxdist_entry = Entry(self,textvariable=self._Maxdist_var,width=10)
        self._Maxdist_entry.grid(column=1,row=8,sticky='W',padx=1)

#   GET MAXIMUM TOLERANCE
        self._Tolmax_label = Label(self, text = "Maximum outlier tolerance (10.0)",anchor="w",bg=lblue)
        self._Tolmax_label.grid(column=0,row=9,columnspan=1,sticky='EW')
        self._Tolmax_var = DoubleVar()
        self._Tolmax_var.set(10.0)
        self._Tolmax_entry = Entry(self,textvariable=self._Tolmax_var,width=10)
        self._Tolmax_entry.grid(column=1,row=9,sticky='W',padx=1)

#   GET SATELLITE FOOTPRINT
        self._Footprint_label = Label(self, text = "Saterllite footprint radius (4000)",anchor="w",bg=lblue)
        self._Footprint_label.grid(column=0,row=10,columnspan=1,sticky='EW')
        self._Footprint_var = IntVar()
        self._Footprint_var.set(4000)
        self._Footprint_entry = Entry(self,textvariable=self._Footprint_var,width=10)
        self._Footprint_entry.grid(column=1,row=10,sticky='W',padx=1)

#   OPTIONS
        self._Option_label = Label(self, text = "Options: ",anchor="w",fg="black",bg=bluegrey)
        self._Option_label.grid(column=0,row=11,columnspan=1,sticky='E')

#   CHECKBUTTON FOR TOP THIRD CALIBRATION
        self.tthird = IntVar()
        check1 = Checkbutton(self,text="High waters calibration (top third)",variable=self.tthird,bg=bluegrey,fg="black",width=28)
        check1.grid(column=1,row=11)

#   CHECKBUTTON FOR RELIEF
        self.relief = IntVar()
        check2 = Checkbutton(self,text="Show relief",variable=self.relief,bg=bluegrey,fg="black",width=10)
        check2.grid(column=2,row=11)

#   CHECKBUTTON FOR PROCESSING ALL TAB FILES
        self.alltab = IntVar()
        check3 = Checkbutton(self,text="All Tabs",variable=self.alltab,bg=bluegrey,fg="black",width=10, command=self.OncheckAllTabs)
        check3.grid(column=2,row=5)        

#   RADIO BUTTON FOR STYLE
        self.style = StringVar(value="w")
        Radiobutton(self,text="Pattern Recognition Weighted",variable=self.style, value="w",bg=bluegrey,fg="black",width=33).grid(column=0,row=12)
        Radiobutton(self,text="River Width",variable=self.style, value="a",bg=bluegrey,fg="black",width=10).grid(column=2,row=12)
        Radiobutton(self,text="Hooking Simulation",variable=self.style, value="h",bg=bluegrey,fg="black",width=28).grid(column=1,row=12)

#   RADIO BUTTON FOR TYPE
        self.type = StringVar(value="r")
        Radiobutton(self,text="River",variable=self.type, value="r",width=10,bg=lblue).grid(column=2,row=9)
        Radiobutton(self,text= "Lake",variable=self.type, value="l",width=10,bg=lblue).grid(column=2,row=10)

#   GO
        Go_button = Button(self,text=u"EXECUTE!",height=3,width=21,fg="white",bg="green",font="-weight bold", command=self.OnButtonClick_Go)
        Go_button.grid(column=1,row=13)

#   QUIT
        Quit_button = Button(self,text=u"QUIT!",height=3,width=7,fg="yellow",bg="red",font="-weight bold",command=self.OnButtonClick_Quit)
        Quit_button.grid(column=2,row=13)

# SAGIS Menu
        self.sagismenu = Menu(self)
        self.config(menu=self.sagismenu)
        self.subMenu = Menu(self.sagismenu)
        self.sagismenu.add_cascade(label="VHS",menu=self.subMenu)
        self.subMenu.add_command(label="Create Virtual Hydrological Station", command = self._VHS_child_1)
        self.subMenu.add_command(label="Create Multiple Virtual Hydrological Station", command = self._VHS_child_2)

# Status Bar
        self.status_txt = Label(self, text = "Processing file # ", bd=2,width=35, relief=SUNKEN, anchor=E, bg=bluegrey)
        self.status_txt.grid(column=0,row=14,columnspan=5,sticky='W')
        self.status_var = StringVar()
        self.status_var.set("cycle")
        self.status = Label(self, textvariable = self.status_var, bd=2,width=80, relief=SUNKEN, anchor=W, bg=bluegrey)
        self.status.grid(column=1,row=14,columnspan=5,sticky='W')

# Display Altimetry Principle
        self._figura1 = PhotoImage(file = "Altimetry.gif")
        self._rotulo_figura = Label(self, image = self._figura1)
        self._rotulo_figura.grid(row = 2, column = 4,rowspan = 12)

# Display UFMG_GEO
        self._figura2 = PhotoImage(file = "UFMG_GEO.gif")
        self._rotulo_figura = Label(self, image = self._figura2)
        self._rotulo_figura.grid(row = 0, column = 4,rowspan = 2)

# ______________________________________ SAGIS EVENTS ____________________________________

# VHS child 1 window _____________________________________________________________________
    def _VHS_child_1(self):
        self.top1 = Toplevel()
        self.top1.title("Producing Single VHS based on a Coordinate")
        self.top1.grid()
        
        self.top1._sagispath_label = Label(self.top1, text = "Satellite File Path")
        self.top1._sagispath_label.grid(row = 1,column = 0)
        self.top1._sagispath_var = StringVar()
        self.top1._sagispath_var_label = Label(self.top1,textvariable=self.top1._sagispath_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=25)
        self.top1._sagispath_var_label.grid(row = 1, column = 1, columnspan=2, sticky='W', padx=1)
        self.top1._sagispath_var.set("")
        
        button_sagispath = tk.Button(self.top1,text=u"Change Path",command= self.OnButtonClick_SAGISPath_1)
        button_sagispath.grid(column=3,row=1)

        self.top1.status_txt = Label(self.top1, text = "Processing cycle ", bd=2,width=20, relief=SUNKEN, anchor=E)
        self.top1.status_txt.grid(column=0,row=6,columnspan=1,sticky='W')
        self.top1.status_var = IntVar()
        self.top1.status_var.set(0)
        self.top1.status = Label(self.top1, textvariable = self.top1.status_var, bd=2,width=10, relief=SUNKEN, anchor=W)
        self.top1.status.grid(column=1,row=6,columnspan=1,sticky='W')

#   RADIO BUTTON FOR SATELLITE
        self.top1.satellite = tk.StringVar(value="envisat")
        tk.Radiobutton(self.top1,text="Envisat",variable=self.top1.satellite, value="envisat", width=10).grid(column=0,row=0)
        tk.Radiobutton(self.top1,text="Saral",variable=self.top1.satellite, value="saral", width=10).grid(column=1,row=0)
        tk.Radiobutton(self.top1,text="CryoSat-2(sar)",variable=self.top1.satellite, value="cryosat2sar", width=10).grid(column=2,row=0)
        tk.Radiobutton(self.top1,text="Sentinel-3",variable=self.top1.satellite, value="sentinel3", width=10).grid(column=3,row=0)
        tk.Radiobutton(self.top1,text="Jason",variable=self.top1.satellite, value="jason", width=10).grid(column=4,row=0)
        
        
#   GET Lat Lon
        self.top1._lat_label = Label(self.top1, text = "Lat-Lon(decimal)")
        self.top1._lat_label.grid(row = 2,column = 0)
        self.top1._lat_var = DoubleVar()
        self.top1._lat_var.set(-15.664)
        self.top1._lat_entry = Entry(self.top1, textvariable = self.top1._lat_var, width=10)
        self.top1._lat_entry.grid(row = 2, column = 1,sticky='W',padx=1)
        self.top1._lon_var = DoubleVar()
        self.top1._lon_var.set(-44.59)
        self.top1._lon_entry = Entry(self.top1, textvariable = self.top1._lon_var, width=10)
        self.top1._lon_entry.grid(row = 2, column = 2,sticky='W',padx=1)

#   GET Track and Cycle
        self.top1._track_label = Label(self.top1, text = "Satellite track")
        self.top1._track_label.grid(row = 3,column = 0)
        self.top1._track_var = IntVar()
        self.top1._track_var.set(377)
        self.top1._track_entry = Entry(self.top1, textvariable = self.top1._track_var, width=10)
        self.top1._track_entry.grid(row = 3, column = 1,sticky='W',padx=1)
        self.top1._cycle_label = Label(self.top1, text = "Cycle(s) (first-last)")
        self.top1._cycle_label.grid(row = 3,column = 2)
        self.top1._cycle_var = StringVar()
        self.top1._cycle_var.set("10-35")
        self.top1._cycle_entry = Entry(self.top1, textvariable = self.top1._cycle_var, width=10)
        self.top1._cycle_entry.grid(row = 3, column = 3,sticky='W',padx=1)

#   GET Distance from coordinate
        self.top1._dist_label = Label(self.top1, text = "Distance from center")
        self.top1._dist_label.grid(row = 4,column = 0)
        self.top1._dist_var = DoubleVar()
        self.top1._dist_var.set(5000.0)
        self.top1._dist_entry = Entry(self.top1, textvariable = self.top1._dist_var, width=10)
        self.top1._dist_entry.grid(row = 4, column = 1, sticky='W',padx=1)

#   CHECKBUTTON FOR GEOID
        self.top1._satgeoid_var = IntVar()
        self.top1.check_satgeoid = Checkbutton(self.top1,text="Use Satellite Geoid",variable=self.top1._satgeoid_var,width=21, anchor=W)
        self.top1.check_satgeoid.grid(column=4,row=4, sticky='W')
        self.top1._satgeoid_var.set(1)

#   GET GEOID correction
        self.top1._geoid_label = Label(self.top1, text = "GEOID additional correction")
        self.top1._geoid_label.grid(row = 4,column = 2)
        self.top1._geoid_var = DoubleVar()
        self.top1._geoid_var.set(0.0)
        self.top1._geoid_entry = Entry(self.top1, textvariable = self.top1._geoid_var, width=10)
        self.top1._geoid_entry.grid(row = 4, column = 3, sticky='W',padx=1)

#   GET name for files
        self.top1._fname_label = Label(self.top1, text = "Name for files")
        self.top1._fname_label.grid(row = 5,column = 0)
        self.top1._fname_var = StringVar()
        self.top1._fname_var.set("AltiSat")
        self.top1._fname_entry = Entry(self.top1, textvariable = self.top1._fname_var, width=10)
        self.top1._fname_entry.grid(row = 5, column = 1,sticky='W',padx=1)

#   CHECKBUTTONS for Shapefiles
        self.top1._ptshp_var = IntVar()
        self.top1.check_ptshp = Checkbutton(self.top1,text="Point shapefile",variable=self.top1._ptshp_var,width=21, anchor=W)
        self.top1.check_ptshp.grid(column=4,row=1, sticky='W')
        self.top1._lnshp_var = IntVar()
        self.top1.check_ptshp = Checkbutton(self.top1,text="Line shapefile",variable=self.top1._lnshp_var,width=21, anchor=W)
        self.top1.check_ptshp.grid(column=4,row=2, sticky='W')

#   CHECKBUTTONS for Wavforms graphs
        self.top1._wfg_var = IntVar()
        self.top1.check_wfg = Checkbutton(self.top1,text="Waveforms (one cycle only)",variable=self.top1._wfg_var,width=21, anchor=W)
        self.top1.check_wfg.grid(column=4,row=3, sticky='W')

#   Process SAGIS Button
        self.top1.button_sagis = tk.Button(self.top1,text=u"Process",font="-weight bold",command= self.OnButtonClick_VHS_1)
        self.top1.button_sagis.grid(column=4,row=5,rowspan=2)

# _______________________________________________________________________________________

# VHS child 2 window _____________________________________________________________________
    def _VHS_child_2(self):
        self.top2 = Toplevel()
        self.top2.title("Producing Multiple VHS based on a Shapefile")
        self.top2.grid()
        
#   GET WATER SHAPE FILE
        self.top2._WShape_label = Label(self.top2, text = "Shape File for Water Bodies",anchor="w")
        self.top2._WShape_label.grid(column=0,row=1,columnspan=1,sticky='EW')
        self.top2._WShape_var = StringVar()
        self.top2._WShape_var_label = Label(self.top2,textvariable=self.top2._WShape_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self.top2._WShape_var_label.grid(column=1,row=1,columnspan=2,sticky='W',padx=1)
        self.top2._WShape_var.set("")

        self.top2.button_Wshp = tk.Button(self.top2,text=u"Change  File",command=self.OnButtonClick_Water_Shp)
        self.top2.button_Wshp.grid(column=3,row=1)

#   GET TRACKS SHAPE FILE
        self.top2._TShape_label = Label(self.top2, text = "Shape File for Satellite Tracks",anchor="w")
        self.top2._TShape_label.grid(column=0,row=2,columnspan=1,sticky='EW')
        self.top2._TShape_var = StringVar()
        self.top2._TShape_var_label = Label(self.top2,textvariable=self.top2._TShape_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self.top2._TShape_var_label.grid(column=1,row=2,columnspan=2,sticky='W',padx=1)
        self.top2._TShape_var.set("")

        self.top2.button_Tshp = tk.Button(self.top2,text=u"Change  File",command=self.OnButtonClick_Tracks_Shp)
        self.top2.button_Tshp.grid(column=3,row=2)

#   GET PATH FOR OUTPUT FILES
        self.top2._sagispath_label = Label(self.top2, text = "Path for Input and Output Files")
        self.top2._sagispath_label.grid(row = 3,column = 0)
        self.top2._sagispath_var = StringVar()
        self.top2._sagispath_var_label = Label(self.top2,textvariable=self.top2._sagispath_var,anchor="e",fg="black",bg="white",relief=SUNKEN,width=30)
        self.top2._sagispath_var_label.grid(row = 3, column = 1, columnspan=2, sticky='W', padx=1)
        self.top2._sagispath_var.set("")
        
        button_sagispath = tk.Button(self.top2,text=u"Change Path",command= self.OnButtonClick_SAGISPath_2)
        button_sagispath.grid(column=3,row=3)

#   STATUS BAR FOR CYCLES
        self.top2.status_txt = Label(self.top2, text = "Processing cycle ", bd=2,width=20, relief=SUNKEN, anchor=E)
        self.top2.status_txt.grid(column=0,row=6,columnspan=1,sticky='W')
        self.top2.status_cycle_var = IntVar()
        self.top2.status_cycle_var.set(0)
        self.top2.status = Label(self.top2, textvariable = self.top2.status_cycle_var, bd=2,width=10, relief=SUNKEN, anchor=W)
        self.top2.status.grid(column=1,row=6,columnspan=1,sticky='W')

#   STATUS BAR FOR TRACKS
        self.top2.status_txt = Label(self.top2, text = "Processing track ", bd=2,width=20, relief=SUNKEN, anchor=E)
        self.top2.status_txt.grid(column=2,row=6,columnspan=1,sticky='W')
        self.top2.status_track_var = IntVar()
        self.top2.status_track_var.set(0)
        self.top2.status = Label(self.top2, textvariable = self.top2.status_track_var, bd=2,width=10, relief=SUNKEN, anchor=W)
        self.top2.status.grid(column=3,row=6,columnspan=1,sticky='W')

#   RADIO BUTTON FOR SATELLITE
        self.top2.satellite = tk.StringVar(value="envisat")
        tk.Radiobutton(self.top2,text="Envisat",variable=self.top2.satellite, value="envisat", width=10).grid(column=0,row=0)
        tk.Radiobutton(self.top2,text="Saral",variable=self.top2.satellite, value="saral", width=10).grid(column=1,row=0)
        tk.Radiobutton(self.top2,text="CryoSat-2(sar)",variable=self.top2.satellite, value="cryosat2sar", width=10).grid(column=2,row=0)
        tk.Radiobutton(self.top2,text="Sentinel-3",variable=self.top2.satellite, value="sentinel3", width=10).grid(column=3,row=0)
        tk.Radiobutton(self.top2,text="Jason",variable=self.top2.satellite, value="jason", width=10).grid(column=4,row=0)
        
#   GET Cycles
        self.top2._cycle_label = Label(self.top2, text = "Cycle(s) (first-last)")
        self.top2._cycle_label.grid(row = 4,column = 2)
        self.top2._cycle_var = StringVar()
        self.top2._cycle_var.set("10-35")
        self.top2._cycle_entry = Entry(self.top2, textvariable = self.top2._cycle_var, width=10)
        self.top2._cycle_entry.grid(row = 4, column = 3,sticky='W',padx=1)

#   GET Distance from coordinate
        self.top2._dist_label = Label(self.top2, text = "Distance from river banks")
        self.top2._dist_label.grid(row = 4,column = 0)
        self.top2._dist_var = DoubleVar()
        self.top2._dist_var.set(5000.0)
        self.top2._dist_entry = Entry(self.top2, textvariable = self.top2._dist_var, width=10)
        self.top2._dist_entry.grid(row = 4, column = 1, sticky='W',padx=1)

#   GET GEOID correction
        self.top2._geoid_label = Label(self.top2, text = "GEOID additional correction")
        self.top2._geoid_label.grid(row = 5,column = 2)
        self.top2._geoid_var = DoubleVar()
        self.top2._geoid_var.set(0.0)
        self.top2._geoid_entry = Entry(self.top2, textvariable = self.top2._geoid_var, width=10)
        self.top2._geoid_entry.grid(row = 5, column = 3, sticky='W',padx=1)

#   GET name for files
        self.top2._fname_label = Label(self.top2, text = "Name for files")
        self.top2._fname_label.grid(row = 5,column = 0)
        self.top2._fname_var = StringVar()
        self.top2._fname_var.set("AltiSat")
        self.top2._fname_entry = Entry(self.top2, textvariable = self.top2._fname_var, width=10)
        self.top2._fname_entry.grid(row = 5, column = 1,sticky='W',padx=1)

#   CHECKBUTTONS for Shapefiles
        self.top2._ptshp_var = IntVar()
        self.top2.check_ptshp = Checkbutton(self.top2,text="Point shapefile",variable=self.top2._ptshp_var,width=11)
        self.top2.check_ptshp.grid(column=4,row=1, sticky='W')
        self.top2._lnshp_var = IntVar()
        self.top2.check_ptshp = Checkbutton(self.top2,text="Line  shapefile",variable=self.top2._lnshp_var,width=11)
        self.top2.check_ptshp.grid(column=4,row=2, sticky='W')

#   CHECKBUTTON FOR GEOID
        self.top2._satgeoid_var = IntVar()
        self.top2.check_satgeoid = Checkbutton(self.top2,text="Use Satellite Geoid",variable=self.top2._satgeoid_var,width=20, anchor=W)
        self.top2.check_satgeoid.grid(column=4,row=3, sticky='W')
        self.top2._satgeoid_var.set(1)

#   Process SAGIS Button
        self.top2.button_sagis = tk.Button(self.top2,text=u"Process",font="-weight bold",command= self.OnButtonClick_VHS_2)
        self.top2.button_sagis.grid(column=4,row=5,rowspan=2)
# _______________________________________________________________________________________

    def OnButtonClick_VHS_1(self):
        sg_tracklist = []
        sg_latlonlist = []
        sg_d_list = []
        sg_path = self.top1._sagispath_var.get()
        sg_name = self.top1._fname_var.get()
        sg_latlonlist.append(str(self.top1._lat_var.get())+','+str(self.top1._lon_var.get()))
        sg_tracklist.append(self.top1._track_var.get())
        sg_cycle = self.top1._cycle_var.get()
        sg_d_list.append(self.top1._dist_var.get())
        sg_geoid = self.top1._geoid_var.get()
        sg_sat = self.top1.satellite.get()
        wf = self.top1._wfg_var.get()
        cyclelist = sg_cycle.split('-')
        fcycle = int(cyclelist[0])
        lcycle = int(cyclelist[len(cyclelist)-1])+1
        if lcycle-fcycle > 1:
            self.top1._wfg_var.set(0)

        make_tab_file(self, sg_path, sg_name, sg_latlonlist, sg_tracklist, sg_cycle, sg_d_list, sg_sat, wf)

    def OnButtonClick_VHS_2(self):
        water_shp_name = self.top2._WShape_var.get()
        track_shp_name = self.top2._TShape_var.get()
        vhs_path = sg_path = self.top2._sagispath_var.get()
        sg_name = self.top2._fname_var.get()
        sg_cycle = self.top2._cycle_var.get()
        sg_d = self.top2._dist_var.get()
        sg_geoid = self.top2._geoid_var.get()
        sg_sat = self.top2.satellite.get()
        make_multiple_vhs(self, vhs_path, water_shp_name, track_shp_name, sg_name, sg_cycle, sg_d, sg_sat, 0)

    def OnButtonClick_SAGISPath_1(self):
        self.top1._sagispath = self.askdir()
        self.top1._sagispath_var.set(self.top1._sagispath)
        self.initname = " "

    def OnButtonClick_SAGISPath_2(self):
        self.top2._sagispath = self.askdir()
        self.top2._sagispath_var.set(self.top2._sagispath)
        self.initname = " "
        
    def OnButtonClick_VHS_Shp(self):
        self.top2.file_opt = options = {}
        self.top2.file_opt['filetypes'] = [('shape files','.shp')]
        self.top2.shapename = self.askopenfname()
        self.top2._Shape_var.set(self.top2.shapename)

    def OnButtonClick_Water_Shp(self):
        self.file_opt = options = {}
        self.file_opt['filetypes'] = [('shape files','.shp')]
        self.top2.shapename = self.askopenfname()
        self.top2._WShape_var.set(self.top2.shapename)

    def OnButtonClick_Tracks_Shp(self):
        self.file_opt = options = {}
        self.file_opt['filetypes'] = [('shape files','.shp')]
        self.top2.tracks = self.askopenfname()
        self.top2._TShape_var.set(self.top2.tracks)
# ________________________________________ SWG EVENTS ____________________________________
    def askdir(self):
        return tkFileDialog.askdirectory(initialdir=self.path)

    def OnButtonClick_Path(self):
        self.path = self.askdir()
        self._Tab_var.set("-")
        self._Caltxt_var.set("-",)
#        self._DEM_var.set("-")
#        self._Shape_var.set("-")
        self._Path_var.set(self.path)
        self.initname = ''

    def askopenfname(self):
        return tkFileDialog.askopenfilename(**self.file_opt)
        
    def OnButtonClick_Tab(self):
        self.file_opt['initialdir'] = self.path
        self.file_opt['filetypes'] = [('tab files','.tab'),('tab files','.TAB')]
        self.tabname = self.askopenfname()
        self._Tab_var.set(self.tabname)

    def OnButtonClick_Txt(self):
        self.file_opt['initialdir'] = self.path
        self.file_opt['filetypes'] = [('text files','.txt'),('text files','.TXT')]
        self.txtname = self.askopenfname()
        self._Caltxt_var.set(self.txtname)

    def OnButtonClick_Hdr(self):
        self.bilpath = self.askdir()
        self._DEM_var.set(self.bilpath)

    def OnButtonClick_Shp(self):
        self.file_opt['filetypes'] = [('shape files','.shp')]
        self.shapename = self.askopenfname()
        self._Shape_var.set(self.shapename)

    def OncheckAllTabs(self):
        self._Year_var.set(-1)
        self._DEM_var.set('-')
        self._Caltxt_var.set('-')
        self._Tab_var.set('')
        self._Geoid_var.set(0.0)
        self._Baselevel_var.set(0.0)

    def OnButtonClick_Go(self):
        self.tabname = self._Tab_var.get()
        self.txtname = self._Caltxt_var.get()
##        self.bilname
##        self.shapename
        self.year = self._Year_var.get()
        self.geoide = self._Geoid_var.get()
        self.base = self._Baselevel_var.get()
        self.distmax = self._Maxdist_var.get()
        self.tolerance = self._Tolmax_var.get()
        self.sfr = self._Footprint_var.get()
        print self.year, self.geoide, self.base, self.distmax, self.tolerance, self.sfr
        self.str1 = 0
        if float(self.geoide) < 100 and float(self.geoide) > -100:
            SWG_Cycle.VHS(self._Path_var.get(), self.tabname,self.txtname,self.bilpath,self.shapename,self.year,self.base,self.geoide,self.distmax, self.tolerance,self.style.get(),self.tthird.get(),self.relief.get(),self.sfr,self.type.get(),self.alltab.get())
        elif float(self.geoide) < 100 and float(self.geoide) > -100:
           self.labelVariable21.set(" Value is outside range (-100 to 100) ") 
        
    def OnButtonClick_Quit(self):
            self.destroy()
# ____________________________________ SWG MAKE TAB FILES _________________________________

def make_tab_file(self, sg_path, sg_name, sg_latlon, sg_tracklist, sg_cycle, sg_d_list, sg_sat, flag_wf):
    plot = 0
    if not os.path.exists(sg_path+'/VHS/'):
        os.makedirs(sg_path+'/VHS/')

    cyclelist = sg_cycle.split('-')
    fcycle = int(cyclelist[0])
    lcycle = int(cyclelist[len(cyclelist)-1])+1

    for t in range(0,len(sg_tracklist)):
        state = 0
        sg_track = sg_tracklist[t]
        if t != 0 and sg_tracklist[t] == sg_tracklist[t-1]:
            state = 1
        [la,lo] = sg_latlon[t].split(',')
        coord = PyPM.Lat_Lon(float(la),float(lo))
        sg_d = sg_d_list[t]
        try:
            self.top2.status_track_var.set(sg_track)
            self.top2.update_idletasks()
        except:
            pass
#        fout1 = open(sg_path+'/VHS/'+sg_sat+'_'+sg_name+'_'+str(sg_track)+'_'+sg_cycle+'_'+str(t)+'.txt','wt')
        fout_i1 = open(sg_path+'/VHS/'+sg_sat+'_'+sg_name+'_'+str(sg_track)+'_'+sg_cycle+'_'+str(t)+'_ice1.tab','wt')
##        fout_l1 = open(sg_path+'/VHS/'+sg_sat+'_'+sg_name+'_'+str(sg_track)+'_'+sg_cycle+'_'+str(t)+'_lake1.tab','wt')
        s = '*999*cycle day year longitude latitude H-&&& altitude .\n'
        fout_i1.write(s)
        s = '*999*cycle day year longitude latitude H-&&& altitude .\n'
##        fout_l1.write(s)
        for cycle in range(fcycle,lcycle):
            try:
                self.top2.status_cycle_var.set(cycle)
                self.top2.update_idletasks()
                self.top2.status_track_var.set(sg_track)
                self.top2.update_idletasks()
            except:
                self.top1.status_var.set(cycle)
                self.top1.update_idletasks()
    #        print 'Cycle', cycle
            if sg_sat == 'envisat':
                cgate = 46
                freq = 320000000
                alti = PyAltisat.read_ra2_wf(sg_path,sg_track,coord,sg_d,cycle)
            elif sg_sat == 'saral':
                cgate = 51
                freq = 500000000
                alti = PyAltisat.read_altika_wf(sg_path,sg_track,coord,sg_d,cycle)
            elif sg_sat == 'sentinel3':
                cgate = 51
                freq = 350000000
                alti = PyAltisat.read_sral_wf(sg_path,sg_track,coord,sg_d,cycle)
            elif sg_sat == 'cryosat2sar':
                cgate = 51
                freq = 350000000
                alti = PyAltisat.read_cryosat_sar(sg_path,sg_track,coord,sg_d,cycle)
            elif sg_sat == 'jason':
                cgate = 32
                freq = 320000000
                alti = PyAltisat.read_jason(sg_path,sg_track,coord,sg_d,cycle)
            if len(alti) > 0:
    #            print len(alti), 'records retained'
                hice1 = []
                hlake1 = []
                dref = 100000.0
                dindex = 0
                for i in range(0,len(alti)):
                    cor = alti[i].ion + alti[i].dry + alti[i].wet + alti[i].ptide + alti[i].stide + alti[i].geoid
                    hice1.append(alti[i].alt - (alti[i].ice1 + cor))
##                    if PyAltisat.lake2(alti[i].wf, alti[i].trk, cgate, freq) > 0:
##                        hlake1.append(alti[i].alt - (PyAltisat.lake2(alti[i].wf, alti[i].trk, cgate, freq) + cor))
##                    else:
##                        hlake1.append(alti[i].alt - (alti[i].ice1 + cor))
                    if PyPM.dist_ll(alti[i].lat, alti[i].lon, coord.lat, coord.lon) < dref:
                        dindex = i
                        dref = PyPM.dist_ll(alti[i].lat, alti[i].lon, coord.lat, coord.lon)
##                        print dref, dindex

                d_plot = []
##                print len(alti), dindex
                for i in range(0,len(alti)):
                    d = PyPM.dist_ll(alti[i].lat, alti[i].lon, alti[dindex].lat, alti[dindex].lon)
                    if alti[i].lat < alti[dindex].lat:
                        d = d * -1.0
                    d_plot.append(d)                       

                plt.figure('Ice1')
                plt.plot(d_plot, hice1, 'k-o')
                plt.ylim(hice1[dindex]-50, hice1[dindex]+50)
                plt.xlim(-sg_d, sg_d)
                plt.xlabel("Distance from center (m)", fontsize=18)
                plt.ylabel("Altitude (m)", fontsize=18)

                flon = []
                flat = []
                fayear = []
                faday = []
                falt = []
                cdate = []
                for j in range(0,len(alti)):
                    flon.append(alti[j].lon)
                    flat.append(alti[j].lat)
                    fayear.append(int(alti[j].ayear))
                    faday.append(int(alti[j].aday))
                    falt.append(alti[j].alt)
                    ndate = dt.date.toordinal(dt.date(int(alti[j].ayear),1,1))
                    ndate = dt.date.fromordinal(ndate+int(alti[j].aday))
                    cdate.append(str(ndate))

                    s = str(cycle)+' '+str(faday[j])+' '+str(fayear[j])+' '+str(flon[j])+' '+str(flat[j])+' '+str(hice1[j])+' '+str(falt[j])+'\n'
                    fout_i1.write(s)
##                    if hlake1[j] != -999:
##                        s = str(cycle)+' '+str(faday[j])+' '+str(fayear[j])+' '+str(flon[j])+' '+str(flat[j])+' '+str(hlake1[j])+' '+str(falt[j])+'\n'
##                        fout_l1.write(s)
                    if flag_wf and (lcycle-fcycle)==1:
                        plt.figure(j)
                        plt.plot(alti[j].wf, 'k-')
                        plt.xlabel("Bins", fontsize=18)
                        plt.ylabel("Amplitude", fontsize=18)

                try:
                    pshpflag = self.top1._ptshp_var.get()
                except:
                    pshpflag = self.top2._ptshp_var.get()
                if pshpflag:
                    ptshpname = sg_path+'/VHS/'+sg_sat+'_'+sg_name+'_'+str(sg_track)+'_'+sg_cycle+'_p'
                    PyAltisat.gen_point_shape_alti(ptshpname, flon, flat, str(cycle), sg_track, cdate, hice1, hice1, state)
                try:
                    lshpflag = self.top1._lnshp_var.get()
                except:
                    lshpflag = self.top2._lnshp_var.get()
                if lshpflag:
                    ch=[]
                    ch.append([alti[0].lon,alti[0].lat])
                    ch.append([alti[len(alti)-1].lon,alti[len(alti)-1].lat])
                    ch = [ch]
                    shpname = sg_path+'/VHS/'+sg_sat+'_'+sg_name+'_'+str(sg_track)+'_'+sg_cycle+'_l'
                    PyAltisat.gen_line_shape(shpname, ch, cycle, sg_track, cdate[0], 0, state)
                state = 1
                

        fout_i1.close()
##        fout_l1.close()
    plt.show()


# _________________________________ SWG MAKE MULTIPLE TAB FILES ______________________________

def make_multiple_vhs(self, vhs_path, water_shp_name, track_shp_name, sg_name, sg_cycle, sg_d, sg_sat, none):

##    plt.figure(0)
    linhas = PyPM.read_tracks(track_shp_name)
    lagos = PyPM.read_waterbody(water_shp_name)

    xvert = []
    for i in range(0,len(linhas)):# para cada linha (temos que considerar as linhas antes dos poligonos para manter
                                  # a ordem dos pontos, pois sao as linhas que a gente vai recortar
        xx = []# a lista de x das linas recortadas
        yy = []# a lista de y das linas recortadas
        st = linhas[i].v[0].tag
        for j in range(0,len(linhas[i].v)):# para cada vertice de cada linha
            for k in range(0,len(lagos)):
                p1 = PyPM.Point(linhas[i].v[j].x1+0.000001,linhas[i].v[j].y1)
                p2 = PyPM.Point(linhas[i].v[j].x2+0.000001,linhas[i].v[j].y2)
                if PyPM.ponto_em_poligono(p1,lagos[k]) and PyPM.ponto_em_poligono(p2,lagos[k]):# caso o vertice e todo dentro de um lago
                    xx.append(p1.x)# acrescentar esse ponto
                    yy.append(p1.y)
                    xx.append(p2.x)# acrescentar esse ponto
                    yy.append(p2.y)
                for l in range(0,len(lagos[k].v)):# para cada vertice de cada poligono
                    p = PyPM.cross_point_vector(linhas[i].v[j], lagos[k].v[l])# determinas o ponto de cruzamento entre o vertice da
                    sp = "%.2f, %.2f" % (p.x,p.y)# formatacao do ponto como "string" mantendo apenas 2 digitos apos o ponto
                                                                  # linha e o vertice do poligino
                    if p.x != -99999.99999 and p.y != -99999.99999:# verificar se existe um ponto de encontro
                        a = PyPM.ponto_na_linha(p,linhas[i].v[j])# verificar se o ponto de encontro pertence ao vertice da linha
                        b = PyPM.ponto_na_linha(p,lagos[k].v[l])# verificar se o ponto de encontro pertence ao vertice do poligono
                        if a and b:# caso o ponto de encontro pertence aos dois vertice
                            if PyPM.ponto_em_poligono(p1,lagos[k]): # caso o ponto 1 do vertice fica dentro de um lago
                                xx.append(p1.x)# acrescentar esse ponto
                                yy.append(p1.y)
                            if PyPM.ponto_em_poligono(p2,lagos[k]): # caso o ponto 2 do vertice fica dentro de um lago
                                xx.append(p2.x)# acrescentar esse ponto
                                yy.append(p2.y)
                        # para os outros casos, usamos apenas o ponto de encontro dos vertices
                            xx.append(p.x)
                            yy.append(p.y)
    #                        print 'O ponto ',sp,' => encontro do poligono', i+1, 'com a linha', k+1

        if len(xx) > 0:
            PyPM.sort_vertice_north(xx,yy)
            for j in range(0,len(xx),2):
                if PyPM.dist_ll(yy[j],xx[j],yy[j+1],xx[j+1]) > 300:
                    xvert.append(PyPM.Vertice(xx[j],yy[j],xx[j+1],yy[j+1],st))
##                    print st
    vhs_latlon = []
    vhs_tracklist = []
    vhs_d = []
    plt.figure('Water_x_Tracks')
    for vert in xvert:
        plt.plot([vert.x1, vert.x2],[vert.y1, vert.y2],'bo-')
        plt.plot((vert.x1+vert.x2)/2.,(vert.y1+vert.y2)/2., 'kd', lw=3)
        vhs_latlon.append(str((vert.y1+vert.y2)/2.)+','+str((vert.x1+vert.x2)/2.))
        vhs_d.append(sg_d + (PyPM.dist_ll(vert.y1, vert.x1, vert.y2, vert.x2)/2.0))
        vhs_tracklist.append(vert.tag)
        sg_path = '/home/philippe/Documents/Alti'
    make_tab_file(self, vhs_path, sg_name, vhs_latlon, vhs_tracklist, sg_cycle, vhs_d, sg_sat, 0)
    for track in linhas:
        tx = []
        ty = []
        for i in range(0,len(track.v)):
            tx.append(track.v[i].x1)
            ty.append(track.v[i].y1)
            tx.append(track.v[i].x2)
            ty.append(track.v[i].y2)
        plt.plot(tx,ty)

    for body in lagos:
        sfx = []
        sfy = []
        for i in range(0,len(body.v)):
            sfx.append(body.v[i].x1)
            sfy.append(body.v[i].y1)
        plt.figure('Water_x_Tracks')
        plt.plot(sfx,sfy)
    plt.show()

