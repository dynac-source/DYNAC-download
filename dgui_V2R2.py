#!/bin/usr/python3
######################################################
# Import libraries                                   #
######################################################
import sys
import platform
import subprocess
import contextlib
import os
import datetime
import pandas as pd
import numpy as np
from numpy import exp, pi, sqrt
from lmfit import Model

import pyqtgraph as pg

from PyQt5 import QtWidgets, QtCore, QtGui, QtPrintSupport
from PyQt5.QtCore    import QSize, Qt, QRect, QPoint
from PyQt5.QtGui     import (QColor, QTextCursor, QTextBlock, QRegion,
        QIcon, QKeySequence, QPen, QImage, QScreen, QGraphicsScene,
        QImageWriter, QPalette)
from PyQt5.QtGui import QPainter
        
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGroupBox,
        QMenu, QPushButton, QRadioButton, QHBoxLayout, QWidget,
        QLabel, QSlider, QGraphicsView, QFileDialog, QMessageBox,
        QAction, qApp, QShortcut, QToolBar, QMainWindow, QDialog,
        QVBoxLayout, QGridLayout)
from matplotlib import cm
import matplotlib.pyplot as plt
import colorcet as cc

from scipy import interpolate
from scipy import stats
from scipy.stats import moment
#from functools import partial
#from sys import argv
import argparse
import math

import tkinter as tk
from tkinter import ttk

######################################################
# set the DGUI version and its date                  #
######################################################
dguiv = "DGUI V2R2"
dguid = "1-May-2020"
dgui_v = dguiv + " " + dguid

######################################################
# set the default dynac version                      #
######################################################
global dynacv, systembin
dynacv = "dynacv7"

######################################################
# Initialize some parameters                         #
######################################################
global inter_selected, KDE_selected, acr_selected, evi_selected, n_of_KDE_bins, pro_raw, pro_fit
global rangex, rangexp, rangey, rangeyp, rangez, rangezp
global xvals, xpvals, yvals, ypvals, zvals, zpvals, GRS, fit_amp, plot_ellipse
global emivals_selected, emivals_bottom, ABS_selected, COG_selected, NRMS
global lut, colormap_name, last_dfpath, last_ifpath
# Unix, Windows and old Macintosh end-of-line
newlinechars = ['\n', '\r\n', '\r']
ifpath=""
ifname=""
dfname=""
# dfpath is distribution file path, ifpath is input file path
default_dfpath=""
last_dfpath=""
last_ifpath=""
# next line sets default color map to be used by dynac gui for density plots
colormap_name = "default"
SV1=0
inter_selected = True
KDE_selected = False
acr_selected = True
evi_selected = False
emivals_selected = False
emivals_bottom = False
n_of_KDE_bins = 50
fit_amp = 16./3.
GRS = "Auto"
ABS_selected = True
COG_selected = False
pro_raw = True
pro_fit = False
rangex = False
rangexp = False
rangey = False
rangeyp = False
rangez = False
rangezp = False
plot_ellipse = False
# mass units (in MeV)
xmat_p    = 938.27231
xmat_hmin = 939.301404
xmat_hi   = 931.4940954
xmat_e    =   0.510998928
amu = 1
ener = 0.
xmat = xmat_p 
NRMS = 6.

######################################################
# Define command line options                        #
######################################################
dgparser = argparse.ArgumentParser(description=dgui_v)
dgparser.add_argument('-v', help="show DGUI version number and exit", action='store_const', const=dguiv)
dgparser.add_argument('--version', help="show DGUI version number and exit", action='version', version=dguiv)
dgparser.add_argument('-p',help='here P is the path to the location of dgui.py; no space between -p and the path! -pP is mandatory if none of the other optional arguments is used', action='store', nargs=1)

######################################################
# Get command line options and check dgui.ini        #
######################################################
args = dgparser.parse_args()
if (args.v != None):
    print(args.v)
    dgparser.exit(status=0, message=None)
if (args.p == None):
    print('No -p argument given')
    print("DGUI requires an argument; for help type:")
    if (platform.system() == 'Windows') :
        print("python dgui.py -h")
    else:
        print("python3 dgui.py -h")
    dgparser.exit(status=0, message=None)
dynpath=args.p[0]
xvals=np.zeros(2)
xpvals=np.zeros(2)
yvals=np.zeros(2)
ypvals=np.zeros(2)
zvals=np.zeros(2)
zpvals=np.zeros(2)
rangex  = True
rangexp = True
rangey  = True
rangeyp = True
rangez  = True
rangezp = True
xvals[0]=-2.
xvals[1]=2.
xpvals[0]=-200.
xpvals[1]=200.
yvals[0]=-2.
yvals[1]=2.
ypvals[0]=-200.
ypvals[1]=200.
zvals[0]=-180.
zvals[1]=180.
zpvals[0]=0.
zpvals[1]=20.
try:
    with open(dynpath + os.sep + "dgui.ini") as fp:  
        line = fp.readline()
        dynpathff=line
        cnt = 1
        while line:
            sline=line.strip()
            if "COLORMAP" in sline:
                colormap_name=sline[9:len(sline)]
            if "DYNACVERSION" in sline:
                dynacv=sline[13:len(sline)]
#                print('DEBUG ',dynacv)
            if "PDFVIEWER" in sline:
                if "evince" in sline:
                    acr_selected = False
                    evi_selected = True
#                    print("evince selected as PDF viewer")
#                else:    
#                    print("Acrobat Reader selected as PDF viewer")
#            print("Line {}: {}".format(cnt, sline))
            if "PROFILES" in sline:
                if "fit" in sline:
                    pro_fit = True
                    pro_raw = False
            if "RANGES" in sline:
                if " X " in sline:
                    fline=""
                    fline = sline[3+sline.find(" X "):]
                    xvals = [float(x) for x in fline.split()]
#                    print("X  limits",xvals[0],xvals[1])
                    rangex = True
                if " XP " in sline:
                    fline=""
                    fline = sline[3+sline.find(" XP "):]
                    xpvals = [float(x) for x in fline.split()]
#                    print("XP limits",xpvals[0],xpvals[1])
                    rangexp = True
                if " Y " in sline:
                    fline=""
                    fline = sline[3+sline.find(" Y "):]
                    yvals = [float(x) for x in fline.split()]
#                    print("Y  limits",yvals[0],yvals[1])
                    rangey = True
                if " YP " in sline:
                    fline=""
                    fline = sline[3+sline.find(" YP "):]
                    ypvals = [float(x) for x in fline.split()]
#                    print("YP limits",ypvals[0],ypvals[1])
                    rangeyp = True
                if " Z " in sline:
                    fline=""
                    fline = sline[3+sline.find(" Z "):]
                    zvals = [float(x) for x in fline.split()]
#                    print("Z  limits",zvals[0],zvals[1])
                    rangez = True
                if " ZP " in sline:
                    fline=""
                    fline = sline[3+sline.find(" ZP "):]
                    zpvals = [float(x) for x in fline.split()]
#                    print("ZP limits",zpvals[0],zpvals[1])
                    rangezp = True
            line = fp.readline()
            cnt += 1
except OSError as e:
    erno = e.errno 
    if(erno == 2):
#        emtxt = dynpath + os.sep + "dgui.ini"
#        emsg1 = QMessageBox()
#        emsg1.setIcon(QMessageBox.Critical)
#        emsg1.setText("File not found:\n'%s'" % emtxt)
#        emsg1.setWindowTitle("Error Message")                                 
        print("ERROR: " + dynpath + os.sep + "dgui.ini : file not found")
    else:
        print('ERROR ', erno,' on opening dgui.ini')
        
    
if (platform.system() == 'Windows') :
    dynpath=dynpath[:-4] + "bin"
    default_dfpath=dynpath[:-3] + "datafiles"
    last_dfpath=default_dfpath
    last_ifpath=default_dfpath
    default_ugpath=dynpath[:-3] + "help"
    dynpath=dynpathff    
else:
    dynpath=dynpath[:-4] + "bin"
    default_dfpath=dynpath[:-3] + "datafiles"
    last_dfpath=default_dfpath
    last_ifpath=default_dfpath
    default_ugpath=dynpath[:-3] + "help"
myplatform=platform.system()
systembin="Running on " + platform.system() + " with DYNAC binary in " + dynpath

######################################################
# Gaussian for fitting purposes                      #
######################################################
def gaussian(x, amp, cen, wid, lof):
    """1-d gaussian: gaussian(x, amp, cen, wid, lof)"""
    return lof + amp * exp(-(x-cen)**2 / (2*wid**2))
    
######################################################
# Define LUT for selected colormap                   #
######################################################
def cm_lut(cmn,show_thr):
    """lut for color map: cm_lut(cmn,show_thr)"""
# cmn is the color map name    
    global lut
    # Get the colormap
    if(cmn == "default"): 
    # Get bottom part of colormap
        cmapbot = cm.get_cmap("RdPu")  
        cmapbot._init()
        lutbot = (cmapbot._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
        # Get central part of colormap
        colormap = cm.get_cmap("nipy_spectral") 
        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
        # Get top part of colormap
        cmaptst = cm.get_cmap("Reds")  
        cmaptst._init()
        luttop = (cmaptst._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
        #overwrite bottom part of lut
        indx=1
        lim=15
        while indx < lim+1:
            lut[lim-indx,0]=lutbot[228-10*indx,0]
            lut[lim-indx,1]=lutbot[228-10*indx,1]
            lut[lim-indx,2]=lutbot[228-10*indx,2]
            lut[lim-indx,3]=lutbot[228-10*indx,3]
            indx = indx + 1
        #overwrite top part of lut
        indx=240
        delta=50
        lim=255
        step=0
        while indx < lim+1:
            lut[indx,0]=luttop[indx-delta+step*3,0]
            lut[indx,1]=luttop[indx-delta+step*3,1]
            lut[indx,2]=luttop[indx-delta+step*3,2]
            lut[indx,3]=luttop[indx-delta+step*3,3]
            indx = indx + 1
            step=step+1
        #make sure level zero = white
        lut[0,0]=255.
        lut[0,1]=255.
        lut[0,2]=255.
        lut[0,3]=255.
    else: 
        cmtype=0
        if((cmn == "nipy_spectral") or (cmn == "viridis") or (cmn == "gist_stern") or 
           (cmn == "jet") or (cmn == "jet_white")):
            cmtype=1
            if(cmn=="jet_white"):
                colormap = cm.get_cmap("jet")
            else:
                colormap = cm.get_cmap(cmn)
            colormap._init()
            lut =  (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
            olut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
            indx=1
            lim=255
            while indx < lim+1:
                lut[indx,0]=olut[lim+1-indx,0]
                lut[indx,1]=olut[lim+1-indx,1]
                lut[indx,2]=olut[lim+1-indx,2]
                lut[indx,3]=olut[lim+1-indx,3]
                indx = indx + 1
        if((cmn == "gnuplot2_r") or (cmn == "gist_earth_r")): 
            cmtype=1
            colormap = cm.get_cmap(cmn)
            colormap._init()
            lut =  (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
        if (cmtype == 0): 
            if((cmn == "linear_worb_100_25_c53") or (cmn == "linear_wcmr_100_45_c42")): 
               colormap = cc.cm[cmn]
               colormap._init()
               lut =  (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
            else: 
               colormap = cc.cm[cmn]
               colormap._init()
               lut =  (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
               olut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0-255 for Qt
               indx=1
               lim=255
               while indx < lim+1:
                   lut[indx,0]=olut[lim+1-indx,0]
                   lut[indx,1]=olut[lim+1-indx,1]
                   lut[indx,2]=olut[lim+1-indx,2]
                   lut[indx,3]=olut[lim+1-indx,3]
                   indx = indx + 1
    if(cmn == "jet"): 
        colors_i = np.concatenate((np.linspace(0, 1., 255), (0., 0., 0., 0.)))
        cmap = cm.jet
        colors_rgba = cmap(colors_i)
        lut = colors_rgba * 255
    if(cmn == "jet_white"): 
        colors_i = np.concatenate((np.linspace(0, 1., 255), (0., 0., 0., 0.)))
        cmap = cm.jet
        colors_rgba = cmap(colors_i)
        lut = colors_rgba * 255
    if(show_thr == 1):                                            
#   zero out below threshold (but not for colormap "jet")
#   do this only for the color bar in the main graph window
# do not do this for the color bar in the options box                
        indx=0
        thresh=int(258*SV1/100)
        if(cmn != "jet"): 
            if(thresh == 0):
                thresh=1
        while indx < thresh:
            lut[indx,0]=0.
            lut[indx,1]=0.
            lut[indx,2]=0.
            lut[indx,3]=0.
            indx=indx + 1
#        indx=0
#        if(cmn == "jet"): 
#            lut[indx,0]=100.
#            lut[indx,1]=100.
#            lut[indx,2]=100.
#            lut[indx,3]=100.
#   make sure no white spots show up at peak (peak should be black)
    indx=255
    while indx < 259:
        lut[indx,0]=0.
        lut[indx,1]=0.
        lut[indx,2]=0.
        lut[indx,3]=255.
        indx=indx + 1
    
######################################################
# OPTIONS LAYOUT class                               #
######################################################
class OptionsLayout(QWidget):
    def __init__(self, parent=None):
        global colormap_name, topvpos, vdel 
        super().__init__(parent)
## Create a ParameterTree widget
        self.top_line = QtWidgets.QLabel(self)
        self.top_line.setText("DGUI PREFERENCES AND OPTIONS SELECTION")
        self.top_line.resize(375,25)
        topvpos=10
        vdel=30
        boxesvoff = 0
        self.top_line.move(20, topvpos)        

# Display name of dynac binary, read from dgui.ini
        self.label_binary = QtWidgets.QLabel(self)
        self.label_binary.setText("Name of DYNAC binary:")
        self.label_binary.resize(375,25)
        self.label_binary.move(20, topvpos+vdel)        
        self.text_binary = QtWidgets.QTextEdit(self)
        self.text_binary.resize(140,29)
        self.text_binary.move(200, topvpos+vdel-1)        
        self.text_binary.setText(dynacv)
        self.BinBtn = QtWidgets.QPushButton('Change', self)
        self.BinBtn.resize(80,32)
        self.BinBtn.move(350, topvpos+vdel-2)        
        # Add BinBtn call back
        self.BinBtn.clicked.connect(self.change_bin)
        self.BinBtn.setToolTip('Change the dynac executable to be used')  

#       create "Density plot method" options box (box 1)
        self.OptBox1 = QGroupBox(self)
        self.OptBox1.setGeometry(QtCore.QRect(10, topvpos+2*vdel, 220, 50))
        self.OptBox1.setTitle("Density plot method")
        # Add L radio button (coordinates within groupBox)
        self.Optradio1 = QRadioButton(self.OptBox1)
        self.Optradio1.setGeometry(QtCore.QRect(10, 20, 120, 25))
        self.Optradio1.setText("Interpolation")
        self.Optradio1.setChecked(True)
        # Add R radio button (coordinates within groupBox)
        self.Optradio2 = QRadioButton(self.OptBox1)
        self.Optradio2.setGeometry(QtCore.QRect(150, 20, 60, 25))
        self.Optradio2.setText("KDE")
        # Add radio button 1 call back
        self.Optradio1.clicked.connect(self.get_or1)
        self.Optradio1.setToolTip('If selected, use interpolation between histogrammed data points')  
        # Add radio button 2 call back
        self.Optradio2.clicked.connect(self.get_or2)
        self.Optradio2.setToolTip('If selected, use KDE method')  

#       create "Number of bins for KDE plots" options box (box 3)
        self.OptBox3 = QGroupBox(self)
        self.OptBox3.setGeometry(QtCore.QRect(235, topvpos+2*vdel, 210, 50))
        self.OptBox3.setTitle("# of bins for KDE plots")
        # Add L radio button (coordinates within groupBox)
        self.OptradKDE1 = QRadioButton(self.OptBox3)
        self.OptradKDE1.setGeometry(QtCore.QRect(10, 20, 100, 25))
        self.OptradKDE1.setText("50")
        self.OptradKDE1.setChecked(True)
        # Add M radio button (coordinates within groupBox)
        self.OptradKDE2 = QRadioButton(self.OptBox3)
        self.OptradKDE2.setGeometry(QtCore.QRect(65, 20, 50, 25))
        self.OptradKDE2.setText("75")
        # Add R radio button (coordinates within groupBox)
        self.OptradKDE3 = QRadioButton(self.OptBox3)
        self.OptradKDE3.setGeometry(QtCore.QRect(120, 20, 60, 25))
        self.OptradKDE3.setText("100")
        # Add KDE radio button 1 call back
        self.OptradKDE1.clicked.connect(self.get_orKDE1)
        self.OptradKDE1.setToolTip('If selected, use 50 bins (fast)')  
        # Add KDE radio button 2 call back
        self.OptradKDE2.clicked.connect(self.get_orKDE2)
        self.OptradKDE2.setToolTip('If selected, use 75 bins (slow)')  
        # Add KDE radio button 3 call back
        self.OptradKDE3.clicked.connect(self.get_orKDE3)
        self.OptradKDE3.setToolTip('If selected, use 100 bins (very slow)')  

#       create "colormap" options box 
        self.label_cmn = QtWidgets.QLabel(self)
        self.label_cmn.setText("Color map:")
        self.label_cmn.resize(275,25)
        self.comboBox = QtGui.QComboBox(self)
        self.comboItems = {1: "default", 2: "gnuplot2_r", 3: "gist_earth_r", 4: "gist_stern",
            5: "viridis", 6: "nipy_spectral", 7: "jet", 8: "jet_white", 9: "diverging_rainbow_bgymr_45_85_c67",
            10: "rainbow_bgyr_35_85_c72", 11: "linear_tritanopic_krjcw_5_98_c46",
            12: "linear_worb_100_25_c53", 13: "linear_wcmr_100_45_c42",
            14: "linear_kryw_5_100_c67", 15:"linear_kryw_0_100_c71"}
#        self.comboBox.addItems(self.comboItems)
#       set preferred colormap as first (this way it will show at the top of the selection box)
        self.comboBox.addItem(colormap_name)
        indx=1
        while indx < 16:
            if(colormap_name != self.comboItems.get(indx)):
                self.comboBox.addItem(self.comboItems.get(indx))
            indx=indx + 1
        if (platform.system() == 'Windows') :
            self.label_cmn.move(125, topvpos+4*vdel-2)        
            self.comboBox.move(198, topvpos+4*vdel)        
        if (platform.system() == 'Linux') :
            self.label_cmn.move(125, topvpos+4*vdel-6)        
            self.comboBox.move(198, topvpos+4*vdel-4)        
        if (platform.system() == 'Darwin') :  
            self.label_cmn.move(115, topvpos+4*vdel-2)        
            self.comboBox.move(180, topvpos+4*vdel-4)        
        self.comboBox.activated[str].connect(self.cm_choice)
        self.comboBox.setToolTip('Select the colormap to be used for density plots')  
                
#       create "Threshold for density plot" options box (box 2)
        self.OptBox2 = QGroupBox(self)
        self.OptBox2.setGeometry(QtCore.QRect(10, topvpos+5*vdel, 220, 50))
        self.OptBox2.setTitle("Threshold for density plot")
        # Add slider 
        self.Optsld1 = QSlider(Qt.Horizontal, self.OptBox2)
        self.Optsld1.setFocusPolicy(Qt.NoFocus)
        self.Optsld1.setGeometry(20, 22, 100, 25)
        self.Optsld1.setValue(SV1)
        self.Optsld1.valueChanged[int].connect(self.changeSV1)
        self.Optsld1.setToolTip('Change the threshold for the density plots')  
        # Add slider labels        
        self.OptSL1a = QLabel(self.OptBox2)
        self.OptSL1a.setText("0")
        self.OptSL1a.setGeometry( 10, 22, 20, 20)
        self.OptSL1b = QLabel(self.OptBox2)
        self.OptSL1b.setText("99")
        self.OptSL1b.setGeometry(125, 22, 20, 20)
        self.OptSL1c = QLabel(self.OptBox2)
        self.OptSL1c.setText(str(SV1))
        self.OptSL1c.setGeometry( 150, 22, 20, 20)

#       create colorbar based on selected colormap 
# Get the LUT corresponding to the selected colormap
        cm_lut(colormap_name,0)
        #Static plot widget is used here to create a colorbar
        self.staticPlt = pg.PlotWidget(self)
        #Set background of colorbar to white:
        self.staticPlt.setBackground((252,252,245, 255))
        xmin=0.
        xmax=99.
        ymin=0.
        ymax=0.2
        x = np.empty((256, 2)) 
        y = np.empty((256, 2)) 
        indx=0
        lut[indx,0]=255.
        lut[indx,1]=255.
        lut[indx,2]=255.
        while indx < 100:
            indice = int(indx * 255. / 99.)
            x[indx,0]= indx
            x[indx,1]= indx
            y[indx,0]=ymin
            y[indx,1]=ymax
            self.staticPlt.plot(x[indx,],y[indx,], pen=QPen(QColor(int(lut[indice,0]), int(lut[indice,1]), int(lut[indice,2]))))
            indx=indx + 1
#        staticPlt.setTitle(title='Colorbar')
        self.staticPlt.showAxis('left', show=False)
#        staticPlt.move(215,94)
        self.staticPlt.move(235,topvpos+4*vdel)
#        staticPlt.resize(175,55)
        self.staticPlt.resize(210,55)
        if (platform.system() == 'Windows') :
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(210,55)
        if (platform.system() == 'Linux') :
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(200,55)
        if (platform.system() == 'Darwin') :  
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(200,55)
        self.staticPlt.setToolTip('This is the colormap used for density plots')  
        
#       create "Data in profiles are" options box (box 5)
        self.OptBox5 = QGroupBox(self)
        self.OptBox5.setGeometry(QtCore.QRect(10, topvpos+7*vdel, 220, 50))
        self.OptBox5.setTitle("Data in profiles are to be")
        # Add profiles check box (coordinates within groupBox)        
        self.checkBox6 = QCheckBox(self.OptBox5)
        self.checkBox6.setGeometry(QtCore.QRect(10, 22, 60, 25))
        self.checkBox6.setText("Raw")
        if(pro_raw != 0):
            self.checkBox6.setChecked(True)
        self.checkBox6.clicked.connect(self.get_cb6)
        # Add R check box (coordinates within groupBox)        
        self.checkBox7 = QCheckBox(self.OptBox5)
        self.checkBox7.setGeometry(QtCore.QRect(100, 22, 70, 25))
        self.checkBox7.setText("Fitted")
        if(pro_fit != 0):
            self.checkBox7.setChecked(True)
        self.checkBox7.clicked.connect(self.get_cb7)
        # Add Raw check tool tip
        self.checkBox6.setToolTip('If selected, profiles will be based on raw data')  
        # Add Fit check tool tip
        self.checkBox7.setToolTip('If selected, profiles will be based on a Gaussian fit')  

#       create "Amplitude of fits (a.u.)" options box (box 8)
        self.OptBox8 = QGroupBox(self)
        self.OptBox8.setGeometry(QtCore.QRect(235, topvpos+7*vdel, 210, 50))
        self.OptBox8.setTitle("Amplitude of profiles (a.u.)")
        # Add L radio button (coordinates within groupBox)
        self.OptradAF1 = QRadioButton(self.OptBox8)
        self.OptradAF1.setGeometry(QtCore.QRect(10, 20, 100, 25))
        self.OptradAF1.setText("1")
        # Add ML radio button (coordinates within groupBox)
        self.OptradAF2 = QRadioButton(self.OptBox8)
        self.OptradAF2.setGeometry(QtCore.QRect(60, 20, 50, 25))
        self.OptradAF2.setText("2")
        # Add MR radio button (coordinates within groupBox)
        self.OptradAF3 = QRadioButton(self.OptBox8)
        self.OptradAF3.setGeometry(QtCore.QRect(110, 20, 50, 25))
        self.OptradAF3.setChecked(True)
        self.OptradAF3.setText("3")
        # Add R radio button (coordinates within groupBox)
        self.OptradAF4 = QRadioButton(self.OptBox8)
        self.OptradAF4.setGeometry(QtCore.QRect(160, 20, 50, 25))
        self.OptradAF4.setText("4")
        # Add AF radio button 1 call back
        self.OptradAF1.clicked.connect(self.get_orAF1)
        self.OptradAF1.setToolTip('Small amplitude for fits and raw data')  
        # Add AF radio button 2 call back
        self.OptradAF2.clicked.connect(self.get_orAF2)
        self.OptradAF2.setToolTip('Small to medium amplitude for fits and raw data')  
        # Add AF radio button 3 call back
        self.OptradAF3.clicked.connect(self.get_orAF3)
        self.OptradAF3.setToolTip('Medium to large amplitude for fits and raw data')  
        # Add AF radio button 4 call back
        self.OptradAF4.clicked.connect(self.get_orAF4)
        self.OptradAF4.setToolTip('Large amplitude for fits and raw data')  

#       create "Graph limits based on" options box (box 7)
        self.OptBox7 = QGroupBox(self)
        self.OptBox7.setGeometry(QtCore.QRect(10, topvpos+9*vdel, 220, 50))
        self.OptBox7.setTitle("Graph limits based on")
        # Add L radio button (coordinates within groupBox)
        self.OptradGL1 = QRadioButton(self.OptBox7)
        self.OptradGL1.setGeometry(QtCore.QRect(10, 20, 100, 25))
        self.OptradGL1.setText("Auto")
        self.OptradGL1.setChecked(True)
        # Add R radio button (coordinates within groupBox)
        self.OptradGL2 = QRadioButton(self.OptBox7)
        self.OptradGL2.setGeometry(QtCore.QRect(100, 20, 60, 25))
        self.OptradGL2.setText("User")
        # Add GL radio button 1 call back
        self.OptradGL1.clicked.connect(self.get_orGL1)
        self.OptradGL1.setToolTip('If selected, auto range will be used')  
        # Add GL radio button 2 call back
        self.OptradGL2.clicked.connect(self.get_orGL2)
        self.OptradGL2.setToolTip('If selected, user defined settings will be used')  

# Create top right options box, plot centering (box 14)
        self.OptBox14 = QGroupBox(self)
        self.OptBox14.setGeometry(QtCore.QRect(235, topvpos+9*vdel, 210, 50))
        self.OptBox14.setTitle("Plot center options")
#       create top upper options box buttons (within box 14)        
        # Add L radio button (coordinates within OptBox14
        self.radOptABS = QRadioButton(self.OptBox14)
        self.radOptABS.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.radOptABS.setText("Absolute")        
        self.radOptABS.setChecked(True)
        # Add L radio button call back
        self.radOptABS.clicked.connect(self.get_rOptABS)
        self.radOptABS.setToolTip("Place distributions with respect to abolute reference axis")  
        # Add R radio button (coordinates within OptBox14)
        self.radOptCOG = QRadioButton(self.OptBox14)
        self.radOptCOG.setGeometry(QtCore.QRect(110, 20, 70, 25))
        self.radOptCOG.setText("COG")
        # Add R radio button call back
        self.radOptCOG.clicked.connect(self.get_rOptCOG)
        self.radOptCOG.setToolTip("Place distributions with respect to COG")  

#       create "Ellipse options" options box (box 12)
        self.OptBox12 = QGroupBox(self)
        self.OptBox12.setGeometry(QtCore.QRect(10, topvpos+11*vdel, 150, 50))
        self.OptBox12.setTitle("Ellipse options")
        # Add profiles check box (coordinates within groupBox)        
        self.checkBox12 = QCheckBox(self.OptBox12)
        self.checkBox12.setGeometry(QtCore.QRect(10, 22, 120, 25))
        self.checkBox12.setText("Plot ellipses")
#        self.checkBox12.setChecked(True)
        self.checkBox12.clicked.connect(self.get_cb12)
        # Add "Plot ellipses" check tool tip
        self.checkBox12.setToolTip('If selected, ellipses will be plotted based on NRMS times the RMS emittance size')  
# Display NRMS, read from dpu.ini  options box (box 11)
        self.label_nrms = QtWidgets.QLabel(self)
        self.label_nrms.setText("NRMS:")
        self.label_nrms.resize(275,25)
        self.label_nrms.move(170, topvpos+11*vdel-4)        
        self.text_nrms = QtWidgets.QTextEdit(self)
        self.text_nrms.resize(50,29)
        self.text_nrms.move(170, topvpos+int(11.5*vdel)+4)
        txtnrms = str(NRMS)      
        self.text_nrms.setText(txtnrms)
        self.NRMSBtn = QtWidgets.QPushButton('Change', self)
        self.NRMSBtn.resize(75,32)
        self.NRMSBtn.move(230, topvpos+int(11.5*vdel)+3)        
        # Add NRMSBtn call back
        self.NRMSBtn.clicked.connect(self.change_nrms)
        self.NRMSBtn.setToolTip("Change the number of RMS multiples for ellipses")  

#       create "Open User Guides (pdf) with" options box (box 4)
        self.OptBox4 = QGroupBox(self)
        self.OptBox4.setGeometry(QtCore.QRect(10, topvpos+13*vdel, 220, 50))
        self.OptBox4.setTitle("Open User Guides (pdf) with")
        # Add L radio button (coordinates within groupBox)
        self.Optradio3 = QRadioButton(self.OptBox4)
        self.Optradio3.setGeometry(QtCore.QRect(10, 20, 80, 25))
        self.Optradio3.setText("Adobe")
        if evi_selected == False :
            self.Optradio3.setChecked(True)
        # Add R radio button (coordinates within groupBox)
        self.Optradio4 = QRadioButton(self.OptBox4)
        self.Optradio4.setGeometry(QtCore.QRect(100, 20, 90, 25))
        self.Optradio4.setText("Evince")
        if evi_selected == True :
            self.Optradio4.setChecked(True)
        # Add radio button 1 call back
        self.Optradio3.clicked.connect(self.get_or3)
        self.Optradio3.setToolTip('If selected, Acrobat reader will be used for opening User Guides')  
        # Add radio button 2 call back
        self.Optradio4.clicked.connect(self.get_or4)
        self.Optradio4.setToolTip('If selected, Evince will be used for opening User Guides')
          
# Display graph limits, read from dpu.ini  options box
        self.label_xmin = QtWidgets.QLabel(self)
        self.label_xmin.setText("Xmin:")
        self.label_xmin.resize(275,25)
        self.label_xmin.move(10, topvpos+15*vdel-4)        
        self.text_xmin = QtWidgets.QTextEdit(self)
        self.text_xmin.resize(50,29)
        self.text_xmin.move(10, topvpos+int(15.5*vdel)+4)
        txtminmax = str(xvals[0])      
        self.text_xmin.setText(txtminmax)
        self.label_xmax = QtWidgets.QLabel(self)
        self.label_xmax.setText("Xmax:")
        self.label_xmax.resize(275,25)
        self.label_xmax.move(10, topvpos+17*vdel-4)        
        self.text_xmax = QtWidgets.QTextEdit(self)
        self.text_xmax.resize(50,29)
        self.text_xmax.move(10, topvpos+int(17.5*vdel)+4)
        txtminmax = str(xvals[1])
        self.text_xmax.setText(txtminmax)
        #              
        self.label_xpmin = QtWidgets.QLabel(self)
        self.label_xpmin.setText("XPmin:")
        self.label_xpmin.resize(275,25)
        self.label_xpmin.move(85, topvpos+15*vdel-4)        
        self.text_xpmin = QtWidgets.QTextEdit(self)
        self.text_xpmin.resize(50,29)
        self.text_xpmin.move(85, topvpos+int(15.5*vdel)+4)
        txtminmax = str(xpvals[0])      
        self.text_xpmin.setText(txtminmax)
        self.label_xpmax = QtWidgets.QLabel(self)
        self.label_xpmax.setText("XPmax:")
        self.label_xpmax.resize(275,25)
        self.label_xpmax.move(85, topvpos+17*vdel-4)        
        self.text_xpmax = QtWidgets.QTextEdit(self)
        self.text_xpmax.resize(50,29)
        self.text_xpmax.move(85, topvpos+int(17.5*vdel)+4)
        txtminmax = str(xpvals[1])
        self.text_xpmax.setText(txtminmax)
        #              
        self.label_ymin = QtWidgets.QLabel(self)
        self.label_ymin.setText("Ymin:")
        self.label_ymin.resize(275,25)
        self.label_ymin.move(160, topvpos+15*vdel-4)        
        self.text_ymin = QtWidgets.QTextEdit(self)
        self.text_ymin.resize(50,29)
        self.text_ymin.move(160, topvpos+int(15.5*vdel)+4)
        txtminmax = str(yvals[0])      
        self.text_ymin.setText(txtminmax)
        self.label_ymax = QtWidgets.QLabel(self)
        self.label_ymax.setText("Ymax:")
        self.label_ymax.resize(275,25)
        self.label_ymax.move(160, topvpos+17*vdel-4)        
        self.text_ymax = QtWidgets.QTextEdit(self)
        self.text_ymax.resize(50,29)
        self.text_ymax.move(160, topvpos+int(17.5*vdel)+4)
        txtminmax = str(yvals[1])      
        self.text_ymax.setText(txtminmax)
        #              
        self.label_ypmin = QtWidgets.QLabel(self)
        self.label_ypmin.setText("YPmin:")
        self.label_ypmin.resize(275,25)
        self.label_ypmin.move(235, topvpos+15*vdel-4)        
        self.text_ypmin = QtWidgets.QTextEdit(self)
        self.text_ypmin.resize(50,29)
        self.text_ypmin.move(235, topvpos+int(15.5*vdel)+4)
        txtminmax = str(ypvals[0])      
        self.text_ypmin.setText(txtminmax)
        self.label_ypmax = QtWidgets.QLabel(self)
        self.label_ypmax.setText("YPmax:")
        self.label_ypmax.resize(275,25)
        self.label_ypmax.move(235, topvpos+17*vdel-4)        
        self.text_ypmax = QtWidgets.QTextEdit(self)
        self.text_ypmax.resize(50,29)
        self.text_ypmax.move(235, topvpos+int(17.5*vdel)+4)
        txtminmax = str(ypvals[1])      
        self.text_ypmax.setText(txtminmax)
        #
        self.label_zmin = QtWidgets.QLabel(self)
        self.label_zmin.setText("Zmin:")
        self.label_zmin.resize(275,25)
        self.label_zmin.move(310, topvpos+15*vdel-4)        
        self.text_zmin = QtWidgets.QTextEdit(self)
        self.text_zmin.resize(50,29)
        self.text_zmin.move(310, topvpos+int(15.5*vdel)+4)
        txtminmax = str(zvals[0])      
        self.text_zmin.setText(txtminmax)
        self.label_zmax = QtWidgets.QLabel(self)
        self.label_zmax.setText("Zmax:")
        self.label_zmax.resize(275,25)
        self.label_zmax.move(310, topvpos+17*vdel-4)        
        self.text_zmax = QtWidgets.QTextEdit(self)
        self.text_zmax.resize(50,29)
        self.text_zmax.move(310, topvpos+int(17.5*vdel)+4)
        txtminmax = str(zvals[1])      
        self.text_zmax.setText(txtminmax)
        #
        self.label_zpmin = QtWidgets.QLabel(self)
        self.label_zpmin.setText("ZPmin:")
        self.label_zpmin.resize(275,25)
        self.label_zpmin.move(385, topvpos+15*vdel-4)        
        self.text_zpmin = QtWidgets.QTextEdit(self)
        self.text_zpmin.resize(50,29)
        self.text_zpmin.move(385, topvpos+int(15.5*vdel)+4)
        txtminmax = str(zpvals[0])      
        self.text_zpmin.setText(txtminmax)
        self.label_zpmax = QtWidgets.QLabel(self)
        self.label_zpmax.setText("ZPmax:")
        self.label_zpmax.resize(275,25)
        self.label_zpmax.move(385, topvpos+17*vdel-4)        
        self.text_zpmax = QtWidgets.QTextEdit(self)
        self.text_zpmax.resize(50,29)
        self.text_zpmax.move(385, topvpos+int(17.5*vdel)+4)
        txtminmax = str(zpvals[1])      
        self.text_zpmax.setText(txtminmax)
        
        self.ChangeLimitsBtn = QtWidgets.QPushButton('Update graph limits', self)
        self.ChangeLimitsBtn.resize(425,32)
        self.ChangeLimitsBtn.move(10, topvpos+int(18.9*vdel))        
        # Add ChangeLimitsBtn call back
        self.ChangeLimitsBtn.clicked.connect(self.change_limits)
        self.ChangeLimitsBtn.setToolTip("Change the graph limits")  

#       create "Emittance values" option box 
        self.OptBox20 = QGroupBox(self)
        self.OptBox20.setGeometry(QtCore.QRect(235, topvpos+13*vdel, 220, 50))
        self.OptBox20.setTitle("Emittance values")
        # Add Display check box (coordinates within groupBox)        
        self.checkBox20 = QCheckBox(self.OptBox20)
        self.checkBox20.setGeometry(QtCore.QRect(10, 22, 70, 25))
        self.checkBox20.setText("Display") 
        self.checkBox20.clicked.connect(self.set_dev)
        self.checkBox20.setToolTip('If selected, displays RMS emittances on top 3 distribution plots')  
        # Add "at the bottom" check box (location of emittance values in plot)        
        self.checkBox21 = QCheckBox(self.OptBox20)
        self.checkBox21.setGeometry(QtCore.QRect(85, 22, 110, 25))
        self.checkBox21.setText("at the bottom") 
        self.checkBox21.clicked.connect(self.set_emi_pos)
        self.checkBox21.setToolTip('If selected, changes location of the display values to the bottom of the plots')  
        
# Display amu, optionally read from dgui.ini 
        boxesvoff = -15
        self.label1_amu = QtWidgets.QLabel(self)
        self.label1_amu.setText("Particle mass (AMU):")
        self.label1_amu.resize(285,30)
        self.label1_amu.move(150, topvpos+int(20.*vdel))        
        self.text_amu = QtWidgets.QTextEdit(self)
        self.text_amu.resize(50,26)
        self.text_amu.move(150, topvpos+int(21.5*vdel) + boxesvoff)
        txtmass = str(amu)      
        self.text_amu.setText(txtmass)
        self.AMUBtn = QtWidgets.QPushButton('Change', self)
        self.AMUBtn.resize(75,32)
        self.AMUBtn.move(205, topvpos+int(21.5*vdel) + boxesvoff - 4)        
        # Add AMUBtn call back
        self.AMUBtn.clicked.connect(self.change_amu)
        self.AMUBtn.setToolTip("Change the particle mass")  

# Display Energy, optionally read from dgui.ini
#        self.label1_energy = QtWidgets.QLabel(self)
#        self.label1_energy.setText("Beam energy (MeV/u):")
#        self.label1_energy.resize(285,25)
#        self.label1_energy.move(300, topvpos+int(20.*vdel))        
#        self.text_energy = QtWidgets.QTextEdit(self)
#        self.text_energy.resize(50,26)
#        self.text_energy.move(300, topvpos+int(21.5*vdel) + boxesvoff)
#        txtener = str(ener)      
#        self.text_energy.setText(txtener)
#        self.EnergyBtn = QtWidgets.QPushButton('Change', self)
#        self.EnergyBtn.resize(75,32)
#        self.EnergyBtn.move(355, int(topvpos+21.5*vdel) + boxesvoff - 4)        
#        # Add EnergyBtn call back
#        self.EnergyBtn.clicked.connect(self.change_energy)
#        self.EnergyBtn.setToolTip("Change the beam energy")  

        
    def set_dev(self):
        global emivals_selected
        '''Display emittance values'''               
        if(self.checkBox20.isChecked() == True ):
            emivals_selected = True 
        else:      
            emivals_selected = False         

    def set_emi_pos(self):
        global emivals_bottom
        '''Position of emittance values'''               
        if(self.checkBox21.isChecked() == True ):
            emivals_bottom = True 
        else:      
            emivals_bottom = False         

    def change_amu(self):
        global amu
        '''Change the mass (AMU)'''               
        amutxt = self.text_amu.toPlainText()
        amu = float(amutxt)
        print("Particle mass changed to ",amu)
        
#    def change_energy(self):
#        global ener
#        '''Change the beam energy (MeV/u)'''               
#        enertxt = self.text_energy.toPlainText()
#        ener = float(enertxt)
#        print("Beam energy changed to ",ener," MeV/u")                        

    def cm_choice(self,text):
        global colormap_name, topvpos, vdel, lut 
        self.staticPlt.close()
        if(text == "jet_white"):
            colormap_name = "jet"
        else:
            colormap_name = text                
# Get the LUT corresponding to the selected colormap
        cm_lut(colormap_name,0)
        if(text == "jet_white"):
            colormap_name = "jet_white"    
        self.staticPlt = pg.PlotWidget(self)
        self.staticPlt.setBackground((252,252,245, 255))
        xmin=0.
        xmax=99.
        ymin=0.
        ymax=0.2
        x = np.empty((256, 2)) 
        y = np.empty((256, 2)) 
        indx=0
        lut[indx,0]=255.
        lut[indx,1]=255.
        lut[indx,2]=255.
        while indx < 100:
            indice = int(indx * 255. / 99.)
            x[indx,0]= indx
            x[indx,1]= indx
            y[indx,0]=ymin
            y[indx,1]=ymax
            self.staticPlt.plot(x[indx,],y[indx,], pen=QPen(QColor(int(lut[indice,0]), int(lut[indice,1]), int(lut[indice,2]))))
            indx=indx + 1
        self.staticPlt.showAxis('left', show=False)
        self.staticPlt.move(235,topvpos+4*vdel)
        self.staticPlt.resize(210,55)
        if (platform.system() == 'Windows') :
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(210,55)
        if (platform.system() == 'Linux') :
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(200,55)
        if (platform.system() == 'Darwin') :  
            self.staticPlt.move(235,topvpos+4*vdel+24)
            self.staticPlt.resize(200,55)
        self.staticPlt.setToolTip('This is the colormap used for density plots')  
        self.staticPlt.show()        
                      
    def get_or1(self):
        global inter_selected, KDE_selected
        inter_selected = True
        KDE_selected = False

    def get_or2(self):
        global inter_selected, KDE_selected
        inter_selected = False
        KDE_selected = True

    def get_or3(self):
        global acr_selected, evi_selected
        acr_selected = True
        evi_selected = False

    def get_or4(self):
        global acr_selected, evi_selected
        acr_selected = False
        evi_selected = True

    def get_rOptABS(self):
        global ABS_selected, COG_selected
        ABS_selected = True
        COG_selected = False

    def get_rOptCOG(self):
        global ABS_selected, COG_selected
        COG_selected = True
        ABS_selected = False
        
    def get_orKDE1(self):
        global n_of_KDE_bins
        n_of_KDE_bins=50

    def get_orKDE2(self):
        global n_of_KDE_bins
        n_of_KDE_bins=75

    def get_orKDE3(self):
        global n_of_KDE_bins
        n_of_KDE_bins=100

    def get_orAF1(self):
        global fit_amp
        fit_amp=16./1.        

    def get_orAF2(self):
        global fit_amp
        fit_amp=16./2.        

    def get_orAF3(self):
        global fit_amp
        fit_amp=16./3.       

    def get_orAF4(self):
        global fit_amp
        fit_amp=16./4.      

    def changeSV1(self, value):
        global SV1
        self.OptSL1c.setText(str(value))
        SV1=value        

    def change_nrms(self):
        global NRMS
        '''Change the number of RMS multiples'''               
        nrmstxt = self.text_nrms.toPlainText()
        NRMS = float(nrmstxt)
        print("Number of RMS multiples changed to ",NRMS)

    def change_limits(self):
        global xvals,xpvals,yvals,ypvals,zvals,zpvals
        '''Change the graph limits'''               
        limtxt = self.text_xmin.toPlainText()
        xvals[0] = float(limtxt)
        limtxt = self.text_xmax.toPlainText()
        xvals[1] = float(limtxt)
        limtxt = self.text_xpmin.toPlainText()
        xpvals[0] = float(limtxt)
        limtxt = self.text_xpmax.toPlainText()
        xpvals[1] = float(limtxt)
        #
        limtxt = self.text_ymin.toPlainText()
        yvals[0] = float(limtxt)
        limtxt = self.text_ymax.toPlainText()
        yvals[1] = float(limtxt)
        limtxt = self.text_ypmin.toPlainText()
        ypvals[0] = float(limtxt)
        limtxt = self.text_ypmax.toPlainText()
        ypvals[1] = float(limtxt)
        #
        limtxt = self.text_zmin.toPlainText()
        zvals[0] = float(limtxt)
        limtxt = self.text_zmax.toPlainText()
        zvals[1] = float(limtxt)
        limtxt = self.text_zpmin.toPlainText()
        zpvals[0] = float(limtxt)
        limtxt = self.text_zpmax.toPlainText()
        zpvals[1] = float(limtxt)
# 2020 BUG : need to fix such that print happens to main window, not to terminal window        
#        mytext = "Graph limits updated"
#        self.inpLog.insertPlainText("\r\n")
#        self.inpLog.insertPlainText("\r\n")
#        self.inpLog.insertPlainText(mytext)
#        self.inpLog.insertPlainText("\n")                
#        self.cursor.setPosition(0,0)        
#        self.inpLog.setTextCursor(self.cursor)        
#        print("Graph limits updated")
                
    def get_cb6(self):
        global pro_raw
        if (self.checkBox6.isChecked() != 0 ):   
            pro_raw = True
#            print('CB6 Selected')
        else:    
            pro_raw = False
#            print('CB6 Not Selected')

    def get_cb7(self):
        global pro_fit
        if (self.checkBox7.isChecked() != 0 ):   
            pro_fit = True
#            print('CB7 Selected')
        else:    
            pro_fit = False
#            print('CB7 Not Selected')

    def get_cb12(self):
        global plot_ellipse
        if(self.checkBox12.isChecked() != 0 ):   
            plot_ellipse = True
        else:    
            plot_ellipse = False

    def get_orGL1(self):
        global GRS
        GRS="Auto"

    def get_orGL2(self):
        global GRS
        GRS="File"

    def change_bin(self):                            #
        global dynacv
        '''Change the dynac executable'''            #
        dynacv = self.text_binary.toPlainText()


######################################################
# OPTIONS class                                      #
######################################################
class Options(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
## Create a ParameterTree like widget
        self.setMinimumSize(QSize(455, 700))    
        self.setMaximumSize(QSize(455, 700))    
#        self.setMaximumSize(QSize(625, 875))    
        self.setWindowTitle("DYNAC GUI OPTIONS") 

        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
#        p.setColor(self.backgroundRole(), QColor(154, 0, 154))
        p.setColor(self.backgroundRole(), QColor(176,224,230))
        self.setPalette(p)

        self.main_widget = OptionsLayout(parent=self)
        self.setCentralWidget(self.main_widget)
        # filling up a menu bar
        bar = self.menuBar()
        # File menu
        file_menu = bar.addMenu('File')
        # adding actions to file menu
        open_action = QtWidgets.QAction('Open', self)
        close_action = QtWidgets.QAction('Close', self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        # Edit menu
        edit_menu = bar.addMenu('Edit')
        # adding actions to edit menu
        undo_action = QtWidgets.QAction('Undo', self)
        redo_action = QtWidgets.QAction('Redo', self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        # use `connect` method to bind signals to desired behavior
        close_action.triggered.connect(self.close)


######################################################
# MAINWINDOW class                                   #
######################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # creating widget and setting it as central
        self.setMinimumSize(QSize(1250, 700))    
#        self.setMaximumSize(QSize(1500, 840))    
        self.setMaximumSize(QSize(1250, 700))    
        self.setWindowTitle("DYNAC GUI") 

        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0, 204, 204))
        self.setPalette(p)
 
        self.createActions()

        self.main_widget = MainLayout(parent=self)
        self.setCentralWidget(self.main_widget)
        # filling up a menu bar
        bar = self.menuBar()
        bar.setNativeMenuBar(False) # Disables the global menu bar on MacOS
        
        # File menu
        file_menu = bar.addMenu('File')
        # adding actions to file menu
        openif_action = QtWidgets.QAction('Open input file', self, triggered=self.main_widget.get_inp)
        opendf_action = QtWidgets.QAction('Open dist. file', self, triggered=self.main_widget.get_dst)
        close_action  = QtWidgets.QAction('Close DGUI', self)
        file_menu.addAction(openif_action)
        file_menu.addAction(opendf_action)
        file_menu.addAction(close_action)
        # Edit menu
#        edit_menu = bar.addMenu('Edit')
#        # adding actions to edit menu
#        undo_action = QtWidgets.QAction('Undo', self)
#        redo_action = QtWidgets.QAction('Redo', self)
#        edit_menu.addAction(undo_action)
#        edit_menu.addAction(redo_action)
        # Options menu
        file_menu = bar.addMenu('Options')
        # adding actions to file menu
        prscr_action = QtWidgets.QAction('Print Screen', self, shortcut=QKeySequence.Print,
                statusTip="Print the full screen", triggered=self.printscr_)
        file_menu.addAction(prscr_action)
        # Help menu
        file_menu = bar.addMenu('Help')
        # adding actions to file menu
        helpdy_action = QtWidgets.QAction('DYNAC help', self, 
                statusTip="Help on DYNAC", triggered=self.help_dynac)
        helpdy_action.setShortcut( QKeySequence("Ctrl+M") )
        file_menu.addAction(helpdy_action)
        helpdg_action = QtWidgets.QAction('DGUI help', self, 
                statusTip="Help on DGUI", triggered=self.help_dgui)
        helpdg_action.setShortcut( QKeySequence("Ctrl+G") )
        file_menu.addAction(helpdg_action)
        # About menu
        file_menu = bar.addMenu('About')
        # adding actions to the about menu
        aboutdg_action = QtWidgets.QAction('About DGUI', self, 
                statusTip="About DGUI", triggered=self.about_dgui)
        file_menu.addAction(aboutdg_action)
        
## allow user to interrupt if DYNAC is running
#        self.interrupt_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
#        self.interrupt_shortcut.activated.connect(self.sigint_handler)
#
        # use `connect` method to bind signals to desired behavior
        close_action.triggered.connect(self.close)

#    def sigint_handler(*args):                    
#        sys.stderr.write('\r')
#        if QMessageBox.question(None, '', "Do you want to stop DYNAC execution?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
#             kill_dynac= self.ProcServer4(parent=self)
##            QApplication.quit()
##            QApplication.quit() <-- would stop DGUI
        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.printAct)
#        menu.addAction(self.cutAct)
#        menu.addAction(self.copyAct)
#        menu.addAction(self.pasteAct)
        menu.exec_(event.globalPos())
        
    def createActions(self):
        self.printAct = QAction("&Print window to file...", self, shortcut=QKeySequence.Print,
                statusTip="Print the document", triggered=self.print_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit DGUI", triggered=self.close)

    def print_(self):
# grab the window        
        if (platform.system() == 'Linux') :
            self.linuxpw = QtCore.QProcess()
            self.linuxpw.start("gnome-screenshot -i --delay=1 -w")
        else:
            self.pxmap = self.grab()
            pxmapfn, _ = QFileDialog.getSaveFileName(self, 'Save', '', filter="PNG(*.png);; JPEG(*.jpg)")
            if pxmapfn[-3:] == "png":
                self.pxmap.save(pxmapfn, "png")
            elif pxmapfn[-3:] == "jpg":
                self.pxmap.save(pxmapfn, "jpg")
            
    def printscr_(self):
# grab the whole screen
        if (platform.system() == 'Linux') :
            self.linuxps = QtCore.QProcess()
            self.linuxps.start("gnome-screenshot")
        else:
            self.pxmap = QApplication.primaryScreen().grabWindow(0)
            pxmapfn, _ = QFileDialog.getSaveFileName(self, 'Save', '', filter="PNG(*.png);; JPEG(*.jpg)")
            if pxmapfn[-3:] == "png":
                self.pxmap.save(pxmapfn, "png")
            elif pxmapfn[-3:] == "jpg":
                self.pxmap.save(pxmapfn, "jpg")

    def help_dynac(self):
# Open the DYNAC User Guide (assumes it is in ..../dynac/help directory)
        if (platform.system() == 'Windows') :
            cmd='"AcroRd32.exe" "' + default_ugpath + os.sep + "dynac_UG.pdf" + '"'
        if (platform.system() == 'Linux') :
            if (acr_selected == True) :
                cmd="acroread " + default_ugpath + os.sep + "dynac_UG.pdf"
            else:    
                cmd="evince-previewer " + default_ugpath + os.sep + "dynac_UG.pdf"
        if (platform.system() == 'Darwin') :  
            cmd="open " + default_ugpath + os.sep + "dynac_UG.pdf"
#        print("Opening DYNAC UG with: ",cmd)
        self.dynugpdf = QtCore.QProcess()
        self.dynugpdf.start(cmd)
        
    def help_dgui(self):
# Open the DGUI User Guide (assumes it is in ..../dynac/help directory)       
        if (platform.system() == 'Windows') :
            if (acr_selected == True) :
                cmd='"AcroRd32.exe" "' + default_ugpath + os.sep + "dgui_UG.pdf" + '"'        
        if (platform.system() == 'Linux') :
            if (acr_selected == True) :
                cmd="acroread " + default_ugpath + os.sep + "dgui_UG.pdf"
            else:    
                cmd="evince-previewer " + default_ugpath + os.sep + "dgui_UG.pdf"
        if (platform.system() == 'Darwin') :
            cmd="open " + default_ugpath + os.sep + "dgui_UG.pdf"
#        print("Opening DGUI UG with: ",cmd)
        self.dgugpdf = QtCore.QProcess()
        self.dgugpdf.start(cmd)

    def about_dgui(self):
# Open the DYNAC User Guide (assumes it is in ..../dynac/help directory)
        txt1= "DGUI is a graphical user interface to the beam dynamics code DYNAC. "
        txt2= dguiv + " requires DYNAC V6R19 or newer."
        abouttxt = txt1 + txt2
        QMessageBox.about(self, "About DGUI", abouttxt)

######################################################
# MAINLAYOUT class                                   #
######################################################
class MainLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # create layout and place widgets

        self.top_line = QtWidgets.QLabel(self)
#        self.top_line.setText(self.get_dynpath())
        self.top_line.setText(systembin)
        self.top_line.resize(750,25)
        self.top_line.move(150, 6)        

        self.top_DGUIV = QtWidgets.QLabel(self)
        self.top_DGUIV.setText(dgui_v)
        self.top_DGUIV.resize(200,25)
        self.top_DGUIV.move(1030, 6)        

        self.LeftBtn1 = QtWidgets.QPushButton('Get dist. file', self)
        self.LeftBtn1.resize(100,32)
        self.LeftBtn1.move(5, 50)        
        self.LeftBtn2 = QtWidgets.QPushButton('Get input file', self)
        self.LeftBtn2.resize(100,32)
        self.LeftBtn2.move(5, 100)        

        self.text_box1 = QtWidgets.QTextEdit(self)
        self.text_box1.resize(750,44)
        self.text_box1.move(120, 44)        
        self.text_box2 = QtWidgets.QTextEdit(self)
        self.text_box2.resize(750,44)
        self.text_box2.move(120, 94)

        self.RightBtn1 = QtWidgets.QPushButton('Plot dist. file', self)
        self.RightBtn1.resize(100,32)
        self.RightBtn1.move(880, 50)        
        self.RightBtn2 = QtWidgets.QPushButton('Run DYNAC', self)
        self.RightBtn2.resize(100,32)
        self.RightBtn2.move(880, 100)        
                
        self.save_button = QtWidgets.QPushButton('Save')
        self.clear_button = QtWidgets.QPushButton('Clear')
        
#       create top upper options box
        self.groupBox1 = QGroupBox(self)
        self.groupBox1.setGeometry(QtCore.QRect(990, 24, 250, 70))
        self.groupBox1.setTitle("Plot dist. options")
#       create top lower options box
        self.groupBox2 = QGroupBox(self)
        self.groupBox2.setGeometry(QtCore.QRect(990, 92, 250, 50))
        self.groupBox2.setTitle("Run time options")       
#       create top lower options box
        self.groupBox3 = QGroupBox(self)
        self.groupBox3.setGeometry(QtCore.QRect(1099, 280, 145, 70))
        self.groupBox3.setTitle("Envelope options")

#       create top upper options box buttons        
        # Add L radio button (coordinates within groupBox)
        self.radio1 = QRadioButton(self.groupBox1)
        self.radio1.setGeometry(QtCore.QRect(10, 20, 110, 25))
        self.radio1.setText("Distribution")
        self.radio1.setChecked(True)
        # Add R radio button (coordinates within groupBox)
        self.radio2 = QRadioButton(self.groupBox1)
        self.radio2.setGeometry(QtCore.QRect(140, 20, 90, 25))
        self.radio2.setText("Density")
        # Add L check box (coordinates within groupBox)        
        self.checkBox1 = QCheckBox(self.groupBox1)
        self.checkBox1.setGeometry(QtCore.QRect(10, 45, 90, 25))
        self.checkBox1.setText("Dst")
        self.checkBox1.setChecked(True)
        # Add R check box (coordinates within groupBox)        
        self.checkBox2 = QCheckBox(self.groupBox1)
        self.checkBox2.setGeometry(QtCore.QRect(140, 45, 90, 25))
        self.checkBox2.setText("Profiles")
#       create top lower options box buttons
        # Add L check box (coordinates within groupBox2)        
        self.checkBox3 = QCheckBox(self.groupBox2)
        self.checkBox3.setGeometry(QtCore.QRect(10, 20,110, 25))
        self.checkBox3.setText("Clear page")
        self.checkBox3.setChecked(True)
#       create bottom plot options box        
        # Add plotit button 
        self.PlotBtn1 = QtWidgets.QPushButton('plotit', self)
        self.PlotBtn1.resize(122,32)
        self.PlotBtn1.move(975, 150)        
        # Add close plotit windows button 
        self.PlotBtn1c = QtWidgets.QPushButton('Close gnuplots', self)
        self.PlotBtn1c.resize(122,32)
        self.PlotBtn1c.move(1100, 150)        
        # Add plot Erms button 
        self.PlotBtn2 = QtWidgets.QPushButton('Plot Erms', self)
        self.PlotBtn2.resize(122,32)
        self.PlotBtn2.move(975, 200)        
        # Add plot W button 
        b3txt="Plot W," + "\N{GREEK SMALL LETTER PHI}"
        self.PlotBtn3 = QtWidgets.QPushButton(b3txt, self)
        self.PlotBtn3.resize(122,32)
        self.PlotBtn3.move(975, 250)        
        # Add plot Erms button 
        self.PlotBtn4 = QtWidgets.QPushButton('Plot X,Y env.', self)
        self.PlotBtn4.resize(122,32)
        self.PlotBtn4.move(975, 300)        
        # Add plot dW button 
        b5txt="Plot dW,d" + "\N{GREEK SMALL LETTER PHI}" + " env."
        self.PlotBtn5 = QtWidgets.QPushButton(b5txt, self)
        self.PlotBtn5.resize(122,32)
        self.PlotBtn5.move(975, 350)        
        # Add plot dispersion button 
        self.PlotBtn6 = QtWidgets.QPushButton('Plot dispersion', self)
        self.PlotBtn6.resize(122,32)
        self.PlotBtn6.move(975, 400)        
        # Add OPTIONS button
        self.PlotBtn7 = QtWidgets.QPushButton('Options', self)
        self.PlotBtn7.resize(100,32)
        self.PlotBtn7.move(5, 5)                
        # Add Close plots button
        self.PlotBtn8 = QtWidgets.QPushButton('Close plots', self)
        self.PlotBtn8.resize(122,32)
        self.PlotBtn8.move(975, 600)               
        # Add plot transmission button 
        b9txt ="Plot x\u0304 , y\u0304 , TX"
#        b9txt = 'Plot <font><span style="text-decoration: overline">X</span></font>, <font><span style="text-decoration: overline">Y</span></font>, TX'
#        b9txt = '<font><span style="text-decoration: overline">X</span></font>'
        self.PlotBtn9 = QtWidgets.QPushButton(b9txt, self)
        self.PlotBtn9.resize(122,32)
        self.PlotBtn9.move(975, 450)  
              
        # Add plot Env check box (coordinates within groupBox)        
        self.checkBox4 = QCheckBox(self.groupBox3)
        self.checkBox4.setGeometry(QtCore.QRect(10, 22, 60, 25))
        self.checkBox4.setText("Env")
        self.checkBox4.setChecked(True)
        # Add plot Ext check box (coordinates within groupBox)        
        self.checkBox5 = QCheckBox(self.groupBox3)
        self.checkBox5.setGeometry(QtCore.QRect(75, 22, 60, 25))
        self.checkBox5.setText("Ext")
        # Add show elemente check box (coordinates within groupBox)        
        self.checkBox8 = QCheckBox(self.groupBox3)
        self.checkBox8.setGeometry(QtCore.QRect(10, 45, 60, 25))
        self.checkBox8.setText("ELE")
                

        # Add L button 1 call back
        self.LeftBtn1.clicked.connect(self.get_dst)
        self.LeftBtn1.setToolTip('Select a particle distribution file to be plotted')  
        # Add L button 2 call back
        self.LeftBtn2.clicked.connect(self.get_inp)
        self.LeftBtn2.setToolTip('Select a DYNAC input file')  
        # Add R button 1 call back
        self.RightBtn1.clicked.connect(self.plot_dst)
        self.RightBtn1.setToolTip('Plot a particle distribution file')  
#        self.RightBtn1.setStyleSheet("color : #0000ff; ")    
                # Add R button 2 call back
        self.RightBtn2.clicked.connect(self.run_dyn)
        self.RightBtn2.setToolTip('Run DYNAC using the input file') 
        self.RightBtn2.setStyleSheet("color : #0000ff; ")        
        # Add radio button 1 call back
        self.radio1.clicked.connect(self.get_r1)
        self.radio1.setToolTip('If selected and Dst selected, macro particles will be plotted')  
        # Add radio button 2 call back
        self.radio2.clicked.connect(self.get_r2)
        self.radio2.setToolTip('If selected, density plots will be displayed')  
        # Add L check 1 call back
        self.checkBox1.clicked.connect(self.get_cb1)
        self.checkBox1.setToolTip('If selected and Distribution selected, macro particles will be plotted')  
        # Add R check 2 call back
        self.checkBox2.clicked.connect(self.get_cb2)
        self.checkBox2.setToolTip('If selected, profiles will be plotted')  
        # Add L check 3 call back
        self.checkBox3.clicked.connect(self.get_cb3)
        self.checkBox3.setToolTip('If selected, the text window will be cleared before new output is displayed')  
        # Add Env check call back
        self.checkBox4.clicked.connect(self.get_cb4)
        self.checkBox4.setToolTip('If selected, envelopes will be plotted')  
        # Add Ext check  call back
#        self.checkBox5.clicked.connect(self.get_cb3)
        self.checkBox5.setToolTip('If selected, beam extents will be plotted')  
        # Add Ext check  call back
#        self.checkBox5.clicked.connect(self.get_cb3)
        self.checkBox8.setToolTip('If selected, beam line elements will be plotted')  
        # Add plotit button call back
        self.PlotBtn1.clicked.connect(self.plotit)
        self.PlotBtn1.setToolTip('Display the plots requested in the DYNAC input file')  
        self.PlotBtn1.setStyleSheet("color : #0000ff; ") 
        # Add close plotit windows button call back
        self.PlotBtn1c.clicked.connect(self.close_gnuplots)
        self.PlotBtn1c.setToolTip('Close the gnuplots created by plotit')  
        # Add plot Erms button call back
        self.PlotBtn2.clicked.connect(self.plot_erms)
        self.PlotBtn2.setToolTip('Plot the Erms for the 3 phase planes along the beam axis') 
        # Add plot W,phase button call back
        self.PlotBtn3.clicked.connect(self.plot_energy)
        self.PlotBtn3.setToolTip('Plot energy and synchronous phase along the beam axis')
        # Add plot transverse envelopes button call back         
        self.PlotBtn4.clicked.connect(self.plot_t_envelopes)
        self.PlotBtn4.setToolTip('Plot the horizontal and vertical envelopes along the beam axis') 
        # Add plot longitudinal envelopes button call back                 
        self.PlotBtn5.clicked.connect(self.plot_l_envelopes)
        self.PlotBtn5.setToolTip('Plot the longitudinal (energy and phase) envelopes along the beam axis') 
        # Add plot dispersion button call back                 
        self.PlotBtn6.clicked.connect(self.plot_dispersion)
        self.PlotBtn6.setToolTip('Plot the horizontal and vertical dispersion along the beam axis') 
        # Add OPTIONS button call back                 
        self.PlotBtn7.clicked.connect(self.select_opt)
        self.PlotBtn7.setToolTip('Select options and preferences') 
        # Add plot transmission button call back                 
        self.PlotBtn9.clicked.connect(self.plot_transmission)
        self.PlotBtn9.setToolTip('Plot the beam centroid and transmisssion along the beam axis') 

        # Add close graph windows button call back                 
        self.PlotBtn8.clicked.connect(self.select_closewins)
        self.PlotBtn8.setToolTip('Close all graphics windows') 


        # big text box at bottomgraphicsView
#        self.inpLog = QtGui.QTextDocument(self)
        self.inpLog = QtWidgets.QTextEdit(self)
#        self.inpLog = QtWidgets.QPlainTextEdit(self)
        self.inpLog.resize(960, 520)
        self.inpLog.move(10, 145)
# Change font, colour of big text box
#        self.inpLog.setStyleSheet(
#        """QPlainTextEdit {background-color: #333;
#                           color: #00FF00;
#                           text-decoration: underline;
#                           font-family: Courier;}""")
        self.cursor = self.inpLog.textCursor()

# allow user to interrupt if DYNAC is running
        self.interrupt_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self.interrupt_shortcut.activated.connect(self.sigint_handler)

######################################################
    def sigint_handler(self):                    
######################################################
        runbutcol=self.RightBtn2.styleSheet()        
        if runbutcol[8:15] == "#ff0000" :
            sys.stderr.write('\r')
            if QMessageBox.question(None, '', "Do you want to stop DYNAC execution?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                 kill_resp = self.dynraw.kill()
#                QApplication.quit() <-- would stop DGUI


######################################################
# define calls related to the buttons                #    
######################################################
    def select_opt(self):
        '''Select options and preferences'''
        self.selectopt = Options(self)
        self.selectopt.move(1270, 20)
        self.selectopt.show()

######################################################
    def select_closewins(self):                      #
        '''Close all graphics windows'''             #
######################################################
        if hasattr(self, 'win'): 
            self.win.close()
        if hasattr(self, 'win1'): 
            self.win1.close()
        if hasattr(self, 'win2'): 
            self.win2.close()
        if hasattr(self, 'win3'): 
            self.win3.close()
        if hasattr(self, 'win4'): 
            self.win4.close()
        if hasattr(self, 'win5'): 
            self.win5.close()
        if hasattr(self, 'win6'): 
            self.win6.close()

######################################################
    def get_dst(self):                               #
        '''get a DYNAC particle distribution file''' #
######################################################
        global dfname, last_dfpath
        fname1 = QFileDialog.getOpenFileName(self, "Open file",last_dfpath, 
         "Distribution files (*.dst);;Text files (*.txt);;All files (*.*)")
        if fname1:
            dfname=fname1[0]
            try:
                string_length=len(dfname)
                if string_length != 0 :
#                distLog.delete('1.0',fd.END)
#                distLog.insert(0.0, dfname)
                    # fix dfname
                    dfname = os.path.abspath(dfname)
#                print("dist. file name: ",dfname)
                    last_dfpath=""
                    last_sep=dfname.rfind(os.sep)
                    last_dfpath=dfname[0:last_sep]
#                print("new dist. path=",last_dfpath)
                    self.text_box1.setText(dfname)
            except:
                msg1 = QMessageBox()
                msg1.setIcon(QMessageBox.Critical)
                msg1.setText("Failed to read distribution file\n'%s'" % dfname)
                msg1.setInformativeText(e)
                msg1.setWindowTitle("Error Message")                                 
#                print("Open Source File", "Failed to read distribution file\n'%s'" % dfname)
            return
            
######################################################
    def get_inp(self):                               #
        '''get a DYNAC input file'''                 #
######################################################
        global ifname, ifpath, last_ifpath
        fname2 = QFileDialog.getOpenFileName(self, "Open file",last_ifpath, 
         "Input files (*.in);;Data files (*.dat);;Text files (*.txt);;All files (*.*)")
        if fname2:
            ifname=fname2[0]
            try:
                string_length=len(ifname)
                if string_length != 0 :
#                inpLog.delete('1.0',fd.END)
#                inpLog.insert(0.0, ifname)
                    # fix ifname
                    ifname = os.path.abspath(ifname)
                    plen= string_length - len(os.path.basename(ifname))
                    ifpath = os.path.abspath(ifname[0:plen])
                    ifpath = ifpath.rstrip()
                    ifpath = ifpath + os.sep
                    last_ifpath=ifpath
#                    self.text_box1.setText(dfname)
                    self.text_box2.setText(ifname)
#                else:    
#                    print("empty ifname=",ifname)
            except:                     
                msg2 = QMessageBox()
                msg2.setIcon(QMessageBox.Critical)
                msg2.setText("Failed to read input file\n'%s'" % ifname)
                msg2.setInformativeText(e)
                msg2.setWindowTitle("Error Message")                                 
#                print("Open Source File", "Failed to read input file\n'%s'" % ifname)
            return

######################################################
    def gen_ellips(self,TWISS):                      #
        '''Generate npoints on ellipse'''            #
######################################################
# Generate points on an ellipse based on Twiss parameters
# input:  TWISS (Array containing Twiss parameters,emittance, NRMS and centroid coordinates
#         NRMS is the ellips size in RMS multiples
# output: XPoints,YPoints are the coordinates of points on the ellips
        npoints=200
        Theta = np.linspace(0,2*pi,npoints)
        XPoints = np.zeros((npoints),float)
        YPoints = np.zeros((npoints),float)
        m11=math.sqrt(math.fabs(TWISS[1]))
        m21=-TWISS[0]/math.sqrt(math.fabs(TWISS[1]))
        m22=1/math.sqrt(math.fabs(TWISS[1]))
        Radius=math.sqrt(math.fabs(TWISS[3]))
        rmsmul = math.sqrt(TWISS[4])
        m12=0.
        PHI = math.atan(2.0*TWISS[0]/(TWISS[2]-TWISS[1]))/2.0
        for i in range(npoints):
            XPoints[i] = TWISS[5] + Radius*(m11*math.cos(Theta[i]) + m12*math.sin(Theta[i]))*rmsmul
            YPoints[i] = TWISS[6] + Radius*(m21*math.cos(Theta[i]) + m22*math.sin(Theta[i]))*rmsmul
        return XPoints,YPoints            

######################################################
    def plot_dst(self):                              #
        '''draw particle distributions'''            #
######################################################
        global noprtcls,iflag,freq,wref,wcog, dfname, xmat, lut, ener, emivals_selected
#        self.RightBtn1.setStyleSheet("color : #ff0000; ") 
#        print("Test: switching to red")       
        grafcols = ['blue', 'red', 'black', 'magenta', 'green', 'gold', 'darkorange', 'gray',
        'sienna', 'darkgreen', 'turquoise', 'cyan', 'purple', 'pink', 'olive', 
        'saddlebrown', 'steelblue', 'indigo', 'crimson', 'yellow']
        dfname=self.text_box1.toPlainText()
#        print("Using data (??) from: ",dfname)
        if(dfname == ""):
            self.get_dst()
#        print("Using data from: ",dfname)
#        print('n_of_KDE_bins in print dist=',n_of_KDE_bins)

        if(dfname):
            try:
#                print("Plotting " + dfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + dfname
                # read the first line
                with open(dfname,'r') as myf:
                    first_row = myf.readline()       
                my_args = first_row.split()
                num_args = len(first_row.split()) 
                noprtcls = int(my_args[0])
                flag = float(my_args[1])
                iflag = int(flag)
                freq = float(my_args[2])
                if(self.checkBox3.isChecked() != 0 ):   
                    self.inpLog.clear()            # Clear text in the log frame before running again
                if(num_args > 3 ):
                    wref = float(my_args[3])
                    wcog = float(my_args[4])
                    mytxt = ""
                    if(num_args == 5 ):
                        mytext = "Distribution file has " + str(num_args) + " arguments:  " + str(noprtcls) + " " + str(iflag) + " " + str(freq) + " " + str(wref) + " " + str(wcog)
                    else:
                        mytext = "Distribution file contains the following arguments:  " + str(noprtcls) + " " + str(iflag) + " " + str(freq) + " " + str(wref) + " " + str(wcog)
                    self.inpLog.insertPlainText("\r\n")
                    self.inpLog.insertPlainText(mytext)
                    self.inpLog.insertPlainText("\n")                
                    self.cursor.setPosition(0,0)        
                    self.inpLog.setTextCursor(self.cursor)        
                else:
                    mytxt = ""
                    mytext = "Distribution file has " + str(num_args) + " arguments:  " + str(noprtcls) + " " + str(iflag) + " " + str(freq)
                    self.inpLog.insertPlainText("\r\n")
                    self.inpLog.insertPlainText(mytext)
                    self.inpLog.insertPlainText("\n")                
                    self.cursor.setPosition(0,0)        
                    self.inpLog.setTextCursor(self.cursor)        
                # print("# of particles " + num_words)
                if(iflag in [0, 10, 100, 110]):
                    myDataFrame = pd.read_csv(dfname, skiprows=1, sep='\s+', header=None, names=["x", "xp", "y", "yp", "z", "zp"])
                if(iflag in [1, 2, 11, 12, 101, 102, 111, 112]):
                    myDataFrame = pd.read_csv(dfname, skiprows=1, sep='\s+', header=None, names=["x", "xp", "y", "yp", "z", "zp", "value"])
                if(iflag in [3, 13, 103, 113]):
                    myDataFrame = pd.read_csv(dfname, skiprows=1, sep='\s+', header=None, names=["x", "xp", "y", "yp", "z", "zp", "value", "pn"])
                # change from rads to mrads
                myDataFrame["xp"] = 1000 * myDataFrame["xp"]  
                myDataFrame["yp"] = 1000 * myDataFrame["yp"]
                # change from rads or ns to degs
                if(iflag in [0, 1, 2, 3, 100, 101, 102, 103]):
                    rad2deg = 180/np.pi
                    myDataFrame["z"] = rad2deg * myDataFrame["z"]           
                else:
                    if(freq != 0.):
                        print("RF Frequency ",freq," MHz")
                    else:
                        freq=tkinter.simpledialog.askfloat("Input Data Required", "Enter frequency [MHz]")
                        print("RF Frequency ",freq," MHz")
                    ns2deg  = 0.36*freq 
                    myDataFrame["z"] = ns2deg * myDataFrame["z"]  
                if(iflag in [2, 12, 102, 112]):
                # file with charge states
                    grouped = myDataFrame.groupby("value")
                    qstates = {}
                    qcount = 0
                    for name, group in grouped:
                        qstates[qcount] = name
                        qcount = qcount + 1
                    names = grouped.groups.keys()
                    print("There are ",qcount," charge states listed in ",dfname)
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
#############################################################
#               SET UP MAIN GRAPHICS WINDOW                 #                
#############################################################                
                self.win = QDialog()
                self.win.setWindowTitle(mytitle)
#               setGeometry(pos left, pos top, width, height)
                self.win.setGeometry(100, 100, 1180, 800)
#                stitle = '<div style="text-align: center"><span style="color: #000000; font-size: 14pt;"><b>Particle distribution plots for ' + str(noprtcls) + ' macro-particles</b></span></div>'
                stitle = "Particle distribution plots for " + str(noprtcls) + " macro-particles"
                self.win.horizontalGroupBox = QGroupBox(stitle)
                self.win.horizontalGroupBox.setAlignment(Qt.AlignCenter)
#red font:      self.win.horizontalGroupBox.setStyleSheet('color: #FF2222; font-weight: bold; font-size: 18px')
                self.win.horizontalGroupBox.setStyleSheet('font-weight: bold; font-size: 22px')
                layout = QGridLayout()
                layout.setHorizontalSpacing(0) 
                layout.setVerticalSpacing(0) 
                if (platform.system() == 'Darwin') :
                    layout.setContentsMargins(0,10,0,0) 
                else:    
                    layout.setContentsMargins(0,0,0,0)
                tax1=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax1=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax2=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax2=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax3=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax3=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax4=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax4=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax5=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax5=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax6=pg.AxisItem(orientation='top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)
                rax6=pg.AxisItem(orientation='right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = pg.PlotWidget(axisItems = {'top': tax1, 'right':rax1})
                p2 = pg.PlotWidget(axisItems = {'top': tax2, 'right':rax2})
                p3 = pg.PlotWidget(axisItems = {'top': tax3, 'right':rax3})
                p3a = pg.PlotWidget()
                p4 = pg.PlotWidget(axisItems = {'top': tax4, 'right':rax4})
                p5 = pg.PlotWidget(axisItems = {'top': tax5, 'right':rax5})
                p6 = pg.PlotWidget(axisItems = {'top': tax6, 'right':rax6})
                p6a = pg.PlotWidget()
                if(self.radio2.isChecked() != 0 ): 
# Density plots with 6 main graphs with 2 colorbars total on the right                
#                   layout.addWidget(p1, row pos, column pos, row span, column span)
# somehow, column span works the opposite way of what one would expect!
# as last argument in the following calls one would want to give 3 (where it says 1) and vice versa
                    layout.addWidget(p1, 2,0,1,1)
                    layout.addWidget(p2, 2,3,1,1)
                    layout.addWidget(p3, 2,6,1,1)
                    layout.addWidget(p3a,2,9,1,3)
                    layout.addWidget(p4, 3,0,1,1)
                    layout.addWidget(p5, 3,3,1,1)
                    layout.addWidget(p6, 3,6,1,1)
                    layout.addWidget(p6a,3,9,1,3)
                else:
# Scatter plots with 6 main graphs               
                    layout.addWidget(p1, 2,0,1,1)
                    layout.addWidget(p2, 2,1,1,1)
                    layout.addWidget(p3, 2,2,1,1)
                    layout.addWidget(p4, 3,0,1,1)
                    layout.addWidget(p5, 3,1,1,1)
                    layout.addWidget(p6, 3,2,1,1)
                self.win.horizontalGroupBox.setLayout(layout)
                windowLayout = QVBoxLayout()
                windowLayout.addWidget(self.win.horizontalGroupBox)
                self.win.setLayout(windowLayout)
#############################################################                
#############################################################                
                nbins=20
                if(noprtcls > 499):
                    nbins=50
                if(noprtcls > 9999):
                    nbins=100
                if(noprtcls > 99999):
                    nbins=200
                binctrx={}
                binctry={}
                binvalx={}
                binvaly={}
                xmax=np.nanmax(myDataFrame["x"].values)
                xmin=np.nanmin(myDataFrame["x"].values)
                xpmax=np.nanmax(myDataFrame["xp"].values)
                xpmin=np.nanmin(myDataFrame["xp"].values)
                ymax=np.nanmax(myDataFrame["y"].values)
                ymin=np.nanmin(myDataFrame["y"].values)
                ypmax=np.nanmax(myDataFrame["yp"].values)
                ypmin=np.nanmin(myDataFrame["yp"].values)
                zmax=np.nanmax(myDataFrame["z"].values)
                zmin=np.nanmin(myDataFrame["z"].values)
                zpmax=np.nanmax(myDataFrame["zp"].values)
                zpmin=np.nanmin(myDataFrame["zp"].values)

#                xmean = np.nanmean(myDataFrame["x"].values)
                xmean = myDataFrame["x"].mean()
                xpmean = myDataFrame["xp"].mean()
                ymean  = myDataFrame["y"].mean()
                ypmean = myDataFrame["yp"].mean()
                zmean  = myDataFrame["z"].mean()
                zpmean = myDataFrame["zp"].mean()
                ener=zpmean
                txtener = str(ener)
#                print("ener=",txtener)      
#                self.text_energy.setText(txtener)
                if(zpmean < 0.001):
                    if(wcog < 0.001):
                        rel_gamma=1.
                        rel_beta=0.
                    else:  
                        rel_gamma = 1. + wcog / (xmat*amu)
                        rel_beta = math.sqrt(1.-1./(rel_gamma*rel_gamma)) 
                else:                   
                    rel_gamma = 1. + zpmean / (xmat*amu)
                    rel_beta = math.sqrt(1.-1./(rel_gamma*rel_gamma)) 

                x2mom  = moment(myDataFrame["x"].values,  moment=2)
                xp2mom = moment(myDataFrame["xp"].values, moment=2)
                y2mom  = moment(myDataFrame["y"].values,  moment=2)
                yp2mom = moment(myDataFrame["yp"].values, moment=2)
                z2mom  = moment(myDataFrame["z"].values,  moment=2)
                zp2mom = moment(myDataFrame["zp"].values, moment=2)

                new12 =  (myDataFrame["x"].values - xmean) * (myDataFrame["xp"].values - xpmean)
                xxpmom = new12.sum() / float(noprtcls)
                new34 =  (myDataFrame["y"].values - ymean) * (myDataFrame["yp"].values - ypmean)
                yypmom = new34.sum() / float(noprtcls)
                new56 =  (myDataFrame["z"].values - zmean) * (myDataFrame["zp"].values - zpmean)
                zzpmom = new56.sum() / float(noprtcls)
                emitx = x2mom * xp2mom - xxpmom * xxpmom
                emity = y2mom * yp2mom - yypmom * yypmom
                emitz = z2mom * zp2mom - zzpmom * zzpmom
 
                xext = math.sqrt(x2mom)
                xpext= math.sqrt(xp2mom)
                yext = math.sqrt(y2mom)
                ypext= math.sqrt(yp2mom)
                zext = math.sqrt(z2mom)
                zpext= math.sqrt(zp2mom)
                xcor = xxpmom / math.sqrt(x2mom * xp2mom)
                ycor = yypmom / math.sqrt(y2mom * yp2mom)
                zcor = zzpmom / math.sqrt(z2mom * zp2mom)
  
                xbet = 10. * xext * xext / math.sqrt(emitx)
                ybet = 10. * yext * yext / math.sqrt(emity)
                zbet =       zext * zext / math.sqrt(emitz)
                
                xgam = 0.1 * xpext * xpext / math.sqrt(emitx)
                ygam = 0.1 * ypext * ypext / math.sqrt(emity)
                zgam = zpext * zpext / math.sqrt(emitz)
                
                xalp = math.sqrt(xbet*xgam-1.)
                if(xcor > 0. ): xalp = -xalp
                yalp = math.sqrt(ybet*ygam-1.)
                if(ycor > 0. ): yalp = -yalp
                zalp = math.sqrt(zbet*zgam-1.)
                if(zcor > 0. ): zalp = -zalp
  
                cogx  = 0.  
                cogxp = 0.   
                cogy  = 0.   
                cogyp = 0.   
                cogz  = 0.   
                cogzp = 0.   
                if(COG_selected == True): 
                    cogx  = -xmean * 10.   
                    cogxp = -xpmean   
                    cogy  = -ymean * 10.   
                    cogyp = -ypmean   
                    cogz  = -zmean    
                    cogzp = -zpmean
                   
                if(GRS=="File"):
# check that if user defined limits are to be used, that they are reasonable
                    if(xvals[0]  > xmax+cogx):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Xmin  > Xmax  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(xvals[1]  < xmin+cogx):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Xmax  < Xmin  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(xpvals[0] > xpmax+cogx):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined XPmin > XPmax in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(xpvals[1] < xpmin+cogxp):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined XPmax < XPmin in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(yvals[0]  > ymax+cogy):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Ymin  > Ymax  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(yvals[1]  < ymin+cogy):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Ymax  < Ymin  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(ypvals[0] > ypmax+cogyp):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined YPmin > YPmax in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(ypvals[1] < ypmin+cogyp):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined YPmax < YPmin in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()  
                    if(zvals[0]  > zmax+cogz):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Zmin  > Zmax  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(zvals[1]  < zmin+cogz):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined Zmax  < Zmin  in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()                          
                    if(zpvals[0] > zpmax+cogzp):
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('User defined ZPmin > ZPmax in data set')
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()  
                    if(zpvals[1] < zpmin+cogzp): 
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("User defined ZPmin > ZPmax in data set")
                        msg.setWindowTitle("DGUI error in user defined graph limits")
                        msg.exec_()       
                   
                if(plot_ellipse == True ): 
                    TwissXXP = [xalp, xbet, xgam, 10. * math.sqrt(emitx), NRMS, 10. * xmean, xpmean]
                    ELLX,ELLXP = self.gen_ellips(TwissXXP)
                    ELLX = 0.1 * ELLX
                    TwissYYP = [yalp, ybet, ygam, 10. * math.sqrt(emity), NRMS, 10. * ymean, ypmean]
                    ELLY,ELLYP = self.gen_ellips(TwissYYP)
                    ELLY = 0.1 * ELLY
                    TwissZZP = [zalp, zbet, zgam, math.sqrt(emitz), NRMS, zmean, zpmean]
                    ELLZ,ELLZP = self.gen_ellips(TwissZZP)
                if(zpmax == zpmin):
                    zpmax = 1.001 * zpmax
                    zpmin = 0.999 * zpmin
                # Get the LUT corresponding to the selected colormap
                cm_lut(colormap_name,1)
                rown=0
#                self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                rown=rown+1
                if(iflag in [2, 12, 102, 112]):
                    ## Add charge states list, use HTML style tags to specify color/size
                    qs = 0
                    ntitle="<span style='color: #000000; font-weight: bold; font-size:10pt'>Charge states: </span>"
                    while qs < qcount:
                        newone=""
                        colors=QColor(grafcols[int(qs)])
                        if(self.radio2.isChecked() != 0 ):   
                            newone="<span style='color: " + "#000000" + "; font-weight: bold; font-size:10pt'>" + str(qstates[qs]) + " " + "</span>"
                        else:
                            newone="<span style='color: " + colors.name() + "; font-weight: bold; font-size:10pt'>" + str(qstates[qs]) + " " + "</span>"
                        ntitle = ntitle + newone
                        qs = qs + 1 
                    addLabel = QLabel(ntitle)
                    addLabel.setAlignment(Qt.AlignCenter)
                    layout.addWidget(addLabel, 1,0,1,9)
                    rown=rown+1
                pg.setConfigOptions(antialias=True)
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Horizontal Phase Plane</b></span></div>'
                p1.setTitle(myttltxt)
                p1.showAxis('right')
                p1.showAxis('top')
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>'
                mylbltxt = mylbltxt + "X' [mrad]" + '</b></span></div>'
                p1.setLabel('left', mylbltxt)
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>X [cm]</b></span></div>'
#                p1.setStyle(tickTextOffset = 1)
                p1.setLabel('bottom', mylbltxt)
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Vertical Phase Plane</b></span></div>'
                p2.setTitle(myttltxt)
                p2.showAxis('right')
                p2.showAxis('top')
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>'
                mylbltxt = mylbltxt + "Y' [mrad]" + '</b></span></div>'
                p2.setLabel('left', mylbltxt)
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>Y [cm]</b></span></div>'
                p2.setLabel('bottom', mylbltxt)
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Longitudinal Phase Plane</b></span></div>'                
                p3.setTitle(myttltxt)
                p3.showAxis('right')
                p3.showAxis('top')
                mylbltxt = ''
                if(COG_selected == True): 
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>dW [MeV]</b></span></div>'
                    p3.setLabel('left', mylbltxt)
                    mylbltxt = ''
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>d&#x03D5; [deg]</b></span></div>'
                    p3.setLabel('bottom', mylbltxt)
                else:
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>W [MeV]</b></span></div>'
                    p3.setLabel('left', mylbltxt)
                    mylbltxt = ''
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>&#x03D5; [deg]</b></span></div>'
                    p3.setLabel('bottom', mylbltxt)
                                    
                rown=rown+1
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Transverse Plane</b></span></div>'
                p4.setTitle(myttltxt)
                p4.showAxis('right')
                p4.showAxis('top')
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>Y [cm]</b></span></div>'
                p4.setLabel('left', mylbltxt)
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>X [cm]</b></span></div>'
                p4.setLabel('bottom', mylbltxt)
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Top</b></span></div>'
                p5.setTitle(myttltxt)
                p5.showAxis('right')
                p5.showAxis('top')
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>X [cm]</b></span></div>'
                p5.setLabel('left', mylbltxt)
                mylbltxt = ''
                if(COG_selected == True): 
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>d&#x03D5; [deg]</b></span></div>'
                    p5.setLabel('bottom', mylbltxt)
                else:
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>&#x03D5; [deg]</b></span></div>'
                    p5.setLabel('bottom', mylbltxt)
                myttltxt = ''
                myttltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 12pt;"><b>Side</b></span></div>'
                p6.setTitle(myttltxt)
                p6.showAxis('right')
                p6.showAxis('top')
                mylbltxt = ''
                mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>Y [cm]</b></span></div>'
                p6.setLabel('left', mylbltxt)
                mylbltxt = ''
                pad_size=0.01
                if(COG_selected == True): 
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>d&#x03D5; [deg]</b></span></div>'
                    p6.setLabel('bottom', mylbltxt)
                else:
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 11pt;"><b>&#x03D5; [deg]</b></span></div>'
                    p6.setLabel('bottom', mylbltxt)
                if(rangex and GRS=="File"):
                    p1.setRange(xRange=[xvals[0],xvals[1]],padding=pad_size)
                    p4.setRange(xRange=[xvals[0],xvals[1]],padding=pad_size)
                    p5.setRange(yRange=[xvals[0],xvals[1]],padding=pad_size)
                    exlab_hrange=xvals[1]-xvals[0]
                    exlab_hmin=xvals[0]
                else:
                    if(COG_selected == True): 
                        p1.setRange(xRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                        p4.setRange(xRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                        p5.setRange(yRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                        exlab_hmin=xmin+cogx
                    else:
                        p1.setRange(xRange=[xmin,xmax],padding=pad_size)
                        p4.setRange(xRange=[xmin,xmax],padding=pad_size)
                        p5.setRange(yRange=[xmin,xmax],padding=pad_size)
                        exlab_hmin=xmin
                    exlab_hrange=xmax-xmin
                if(rangexp and GRS=="File"):
                    p1.setRange(yRange=[xpvals[0],xpvals[1]],padding=pad_size)
                    exlab_vrange=xpvals[1]-xpvals[0]
                    exlab_vmax=xpvals[1]
                else:
                    if(COG_selected == True): 
                        p1.setRange(yRange=[xpmin+cogxp,xpmax+cogxp],padding=pad_size)
                        exlab_vmax=xpmax+cogxp
                    else:
                        p1.setRange(yRange=[xpmin,xpmax],padding=pad_size)
                        exlab_vmax=xpmax
                    exlab_vrange=xpmax-xpmin
                if(rangey and GRS=="File"):
                    p2.setRange(xRange=[yvals[0],yvals[1]],padding=pad_size)
                    p4.setRange(yRange=[yvals[0],yvals[1]],padding=pad_size)
                    p6.setRange(yRange=[yvals[0],yvals[1]],padding=pad_size)
                    eylab_hrange=yvals[1]-yvals[0]
                    eylab_hmin=yvals[0]
                else:
                    if(COG_selected == True): 
                        p2.setRange(xRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                        p4.setRange(yRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                        p6.setRange(yRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                        eylab_hmin=ymin+cogy
                    else:
                        p2.setRange(xRange=[ymin,ymax],padding=pad_size)
                        p4.setRange(yRange=[ymin,ymax],padding=pad_size)
                        p6.setRange(yRange=[ymin,ymax],padding=pad_size)
                        eylab_hmin=ymin
                    eylab_hrange=ymax-ymin
                if(rangeyp and GRS=="File"):
                    p2.setRange(yRange=[ypvals[0],ypvals[1]],padding=pad_size)
                    eylab_vrange=ypvals[1]-ypvals[0]
                    eylab_vmax=ypvals[1]
                else:
                    if(COG_selected == True): 
                        p2.setRange(yRange=[ypmin+cogyp,ypmax+cogyp],padding=pad_size)
                        eylab_vmax=ypmax+cogyp
                    else:
                        p2.setRange(yRange=[ypmin,ypmax],padding=pad_size)
                        eylab_vmax=ypmax
                    eylab_vrange=ypmax-ypmin
                if(rangez and GRS=="File"):
                    p3.setRange(xRange=[zvals[0],zvals[1]],padding=pad_size)
                    p5.setRange(xRange=[zvals[0],zvals[1]],padding=pad_size)
                    p6.setRange(xRange=[zvals[0],zvals[1]],padding=pad_size)
                    ezlab_hrange=zvals[1]-zvals[0]
                    ezlab_hmin=zvals[0]
                else:
                    if(COG_selected == True): 
                        p3.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                        p5.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                        p6.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                        ezlab_hmin=zmin+cogz
                    else:
                        p3.setRange(xRange=[zmin,zmax],padding=pad_size)
                        p5.setRange(xRange=[zmin,zmax],padding=pad_size)
                        p6.setRange(xRange=[zmin,zmax],padding=pad_size)
                        ezlab_hmin=zmin
                    ezlab_hrange=zmax-zmin
                if(rangezp and GRS=="File"):
                    p3.setRange(yRange=[zpvals[0],zpvals[1]],padding=pad_size)
                    ezlab_vrange=zpvals[1]-zpvals[0]
                    ezlab_vmax=zpvals[1]
                else:
                    if(COG_selected == True): 
                        p3.setRange(yRange=[zpmin+cogzp,zpmax+cogzp],padding=pad_size)
                        ezlab_vmax=zpmax+cogzp
                    else:
                        p3.setRange(yRange=[zpmin,zpmax],padding=pad_size)
                        ezlab_vmax=zpmax
                    ezlab_vrange=zpmax-zpmin
                
                if(iflag in [2, 12, 102, 112]):
                    qs = 0
                    if (self.radio1.isChecked() != 0 ) and (self.checkBox1.isChecked() != 0 ):   
#                   X-XP plot of particles (multiple charge states)
                        cstep=int(255/(qcount+1))
                        while qs < qcount:
                            ByGroup = grouped.get_group(qstates[qs])                
#                            c1=int(255-qs*cstep)
#                            c2=int(15+qs*cstep)
#                            c3=int(10+qs*cstep)
#                            colors = pg.mkBrush(color=(c1, c2, c3))
                            colors=QColor(grafcols[int(qs)])
                            scatterplot = pg.ScatterPlotItem(cogx + ByGroup["x"], cogxp + ByGroup["xp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p1.addItem(scatterplot)
                            scatterplot = pg.ScatterPlotItem(cogy + ByGroup["y"], cogyp + ByGroup["yp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p2.addItem(scatterplot)
                            scatterplot = pg.ScatterPlotItem(cogz + ByGroup["z"], cogzp + ByGroup["zp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p3.addItem(scatterplot)
                            scatterplot = pg.ScatterPlotItem(cogx + ByGroup["x"], cogy + ByGroup["y"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p4.addItem(scatterplot)
                            scatterplot = pg.ScatterPlotItem(cogz + ByGroup["z"], cogx + ByGroup["x"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p5.addItem(scatterplot)
                            scatterplot = pg.ScatterPlotItem(cogz + ByGroup["z"], cogy + ByGroup["y"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = colors)
                            p6.addItem(scatterplot)
                            qs = qs + 1 
                        if (emivals_selected == True ):   
                        # add emittance valuess to the top 3 plots
                            exlabel=pg.TextItem(anchor=(0.5,0.5))
                            eylabel=pg.TextItem(anchor=(0.5,0.5))
                            ezlabel=pg.TextItem(anchor=(0.5,0.5))
                            if(emivals_bottom == True):
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.97*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.97*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.97*ezlab_vrange)
                            else:
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.03*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.03*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.03*ezlab_vrange)
                            exlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ex,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emitx)))
                            p1.addItem(exlabel)    
                            eylabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ey,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emity)))
                            p2.addItem(eylabel)    
                            ezlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ez,rms=%6.3f MeV.deg </span></div>'%(math.sqrt(emitz)))
                            p3.addItem(ezlabel)
                        if(plot_ellipse == True ): 
                            p1.plot(ELLX + cogx, ELLXP + cogxp, pen=pg.mkPen('g', width=2))
                            p2.plot(ELLY + cogy, ELLYP + cogyp, pen=pg.mkPen('g', width=2))
                            p3.plot(ELLZ + cogz, ELLZP + cogzp, pen=pg.mkPen('g', width=2))
                        self.win.show()
                else:
                #single charge state beam
                    if (self.radio1.isChecked() != 0 ) and (self.checkBox1.isChecked() != 0 ):   
                        # scatter plots
                        # top left plot
                        scatterplot = pg.ScatterPlotItem(cogx + myDataFrame["x"], cogxp + myDataFrame["xp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p1.addItem(scatterplot)
                        if(plot_ellipse == True ): 
                            p1.plot(ELLX + cogx, ELLXP + cogxp, pen=pg.mkPen('g', width=2))
                        # top middle plot
                        scatterplot = pg.ScatterPlotItem(cogy + myDataFrame["y"], cogyp + myDataFrame["yp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p2.addItem(scatterplot)
                        if(plot_ellipse == True ): 
                            p2.plot(ELLY + cogy, ELLYP + cogyp, pen=pg.mkPen('g', width=2))
                        # top right plot
                        scatterplot = pg.ScatterPlotItem(cogz + myDataFrame["z"], cogzp + myDataFrame["zp"], symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p3.addItem(scatterplot)
                        if(plot_ellipse == True ): 
                            p3.plot(ELLZ + cogz, ELLZP + cogzp, pen=pg.mkPen('g', width=2))
                            
                        # bottom left plot
                        scatterplot = pg.ScatterPlotItem(cogx + myDataFrame["x"], cogy + myDataFrame["y"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p4.addItem(scatterplot)
                        # bottom middle plot
                        scatterplot = pg.ScatterPlotItem(cogz + myDataFrame["z"], cogx + myDataFrame["x"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p5.addItem(scatterplot)
                        # bottom right plot
                        scatterplot = pg.ScatterPlotItem(cogz + myDataFrame["z"], cogy + myDataFrame["y"],  symbol='o', size=1.2, pen=pg.mkPen(None), brush = 'b')
                        p6.addItem(scatterplot)
                        if (emivals_selected == True ):   
                        # add emittance valuess to the top 3 plots
                            if(rel_beta == 0):
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Critical)
                                msg.setText('Average energy of particle distribution is quasi 0 keV, normalized emittances will be zero')
                                msg.setWindowTitle("DGUI warning")
                                msg.exec_()                          
                            exlabel=pg.TextItem(anchor=(0.5,0.5))
                            eylabel=pg.TextItem(anchor=(0.5,0.5))
                            ezlabel=pg.TextItem(anchor=(0.5,0.5))
                            if(emivals_bottom == True):
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.97*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.97*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.97*ezlab_vrange)
                            else:
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.03*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.03*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.03*ezlab_vrange)
                            exlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ex,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emitx)))
                            p1.addItem(exlabel)    
                            eylabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ey,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emity)))
                            p2.addItem(eylabel)    
                            ezlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ez,rms=%6.3f MeV.deg </span></div>'%(math.sqrt(emitz)))
                            p3.addItem(ezlabel)
                hticksz1 = 0.
                hticksz2 = 0.
                hticksz3 = 0.
                vticksz1 = 0.
                vticksz2 = 0.
                vticksz3 = 0.
                if(self.radio2.isChecked() != 0 ): 
                    # Density plots
#        # Setup colorbar, implemented as an ImageItem
                    bar1=pg.ImageItem()
                    bar2=pg.ImageItem()
#        # The color bar ImageItem levels run from 0 to 1
                    bar1.setImage(np.linspace(0,1,8192)[None,:])
                    bar2.setImage(np.linspace(0,1,8192)[None,:])
# Add a color bar to the first row, linked to the image. 
                    mylbltxt = ''
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>'
                    mylbltxt = mylbltxt + "Intensity [%]" + '</b></span></div>'
                    p3a.setLabel('left', mylbltxt)
                    p3a.hideAxis('bottom')
                    bar1.setLookupTable(lut)
                    bar1.scale(0.01, 0.0122)
                    bar1.setPos(0, 0)
                    p3a.addItem(bar1)
# Add a color bar to the second row, linked to the image.                                              
                    mylbltxt = ''
                    mylbltxt = '<div style="text-align: center"><span style="color: #000000; font-size: 10pt;"><b>'
                    mylbltxt = mylbltxt + "Intensity [%]" + '</b></span></div>'
                    p6a.setLabel('left', mylbltxt)                         
                    p6a.hideAxis('bottom')
                    bar2.setLookupTable(lut)
                    bar2.scale(0.01, 0.0122)
                    bar2.setPos(0, 0)
                    p6a.addItem(bar2)
                    if(inter_selected != 0 ):                         
                    # Perform interpolation
                        newbins=4*nbins
                        # top left plot
                        plotDataFrame = myDataFrame 
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]+cogx > xvals[0]) & (plotDataFrame["x"]+cogx < xvals[1]) & (plotDataFrame["xp"]+cogxp > xpvals[0]) & (plotDataFrame["xp"] + cogxp < xpvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(myDataFrame["x"]>xvals[0]) & (myDataFrame["x"]<xvals[1]) & (myDataFrame["xp"]>xpvals[0]) & (myDataFrame["xp"]<xpvals[1])]    
                            xmin=np.nanmin(plotDataFrame["x"].values)
                            xmax=np.nanmax(plotDataFrame["x"].values)
                            xpmin=np.nanmin(plotDataFrame["xp"].values)
                            xpmax=np.nanmax(plotDataFrame["xp"].values)  
                            if(colormap_name == "jet"): 
                                p1.setRange(xRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                                p1.setRange(yRange=[xpmin+cogxp,xpmax+cogxp],padding=pad_size)
                                exlab_hmin=xmin+cogx
                                exlab_hrange=xmax-xmin
                                exlab_vmax=xpmax+cogxp
                                exlab_vrange=xpmax-xpmin
                        histxxp, bin_edgex, bin_edgexp = np.histogram2d(plotDataFrame["x"], plotDataFrame["xp"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgex)):
                            xcords.append(0.5*(bin_edgex[indx-1]+bin_edgex[indx]) + cogx)
                        for indx in range(1, len(bin_edgexp)):
                            ycords.append(0.5*(bin_edgexp[indx-1]+bin_edgexp[indx]) + cogxp)
                        f = interpolate.interp2d(xcords, ycords, histxxp, kind='linear')
                        hticksz1 = (xpmax-xpmin)*0.01 
                        vticksz1 = (xmax-xmin)*0.01 
                        xstep=(xmax-xmin)/newbins
                        ystep=(xpmax-xpmin)/newbins
                        xnew = np.arange(xmin + cogx, xmax + cogx, xstep)
                        ynew = np.arange(xpmin + cogxp, xpmax + cogxp, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(xmin + cogx, xpmin + cogxp)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p1.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p1.plot(ELLX + cogx, ELLXP + cogxp, pen=pg.mkPen('g', width=2))
                        # top middle plot
                        plotDataFrame = myDataFrame 
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["y"]+cogy > yvals[0]) & (plotDataFrame["y"]+cogy < yvals[1]) & (plotDataFrame["yp"]+cogyp > ypvals[0]) & (plotDataFrame["yp"] + cogyp < ypvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(myDataFrame["y"]>yvals[0]) & (myDataFrame["y"]<yvals[1]) & (myDataFrame["yp"]>ypvals[0]) & (myDataFrame["yp"]<ypvals[1])]    
                            ymin=np.nanmin(plotDataFrame["y"].values)
                            ymax=np.nanmax(plotDataFrame["y"].values)
                            ypmin=np.nanmin(plotDataFrame["yp"].values)
                            ypmax=np.nanmax(plotDataFrame["yp"].values)  
                            if(colormap_name == "jet"): 
                                p2.setRange(xRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                                p2.setRange(yRange=[ypmin+cogyp,ypmax+cogyp],padding=pad_size)
                                eylab_hmin=ymin+cogy
                                eylab_hrange=ymax-ymin
                                eylab_vmax=ypmax+cogyp
                                eylab_vrange=ypmax-ypmin
                        histyyp, bin_edgey, bin_edgeyp = np.histogram2d(plotDataFrame["y"], plotDataFrame["yp"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgey)):
                            xcords.append(0.5*(bin_edgey[indx-1]+bin_edgey[indx]) + cogy)
                        for indx in range(1, len(bin_edgeyp)):
                            ycords.append(0.5*(bin_edgeyp[indx-1]+bin_edgeyp[indx]) + cogyp)
                        f = interpolate.interp2d(xcords, ycords, histyyp, kind='linear')
                        hticksz2 = (ypmax-ypmin)*0.01 
                        vticksz2 = (ymax-ymin)*0.01 
                        xstep=(ymax-ymin)/newbins
                        ystep=(ypmax-ypmin)/newbins
                        xnew = np.arange(ymin + cogy, ymax + cogy, xstep)
                        ynew = np.arange(ypmin + cogyp, ypmax + cogyp, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(ymin + cogy, ypmin + cogyp)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p2.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p2.plot(ELLY + cogy, ELLYP + cogyp, pen=pg.mkPen('g', width=2))
                        # top right plot
                        plotDataFrame = myDataFrame
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]+cogz > zvals[0]) & (plotDataFrame["z"]+cogz < zvals[1]) & (plotDataFrame["zp"]+cogzp > zpvals[0]) & (plotDataFrame["zp"] + cogzp < zpvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]>zvals[0]) & (plotDataFrame["z"]<zvals[1]) & (plotDataFrame["zp"]>zpvals[0]) & (plotDataFrame["zp"]<zpvals[1])]    
                            zmin=np.nanmin(plotDataFrame["z"].values)
                            zmax=np.nanmax(plotDataFrame["z"].values)
                            zpmin=np.nanmin(plotDataFrame["zp"].values)
                            zpmax=np.nanmax(plotDataFrame["zp"].values)
                            if(colormap_name == "jet"): 
                                p3.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                                p3.setRange(yRange=[zpmin+cogzp,zpmax+cogzp],padding=pad_size)  
                                ezlab_hmin=zmin+cogz
                                ezlab_hrange=zmax-zmin
                                ezlab_vmax=zpmax+cogzp
                                ezlab_vrange=zpmax-zpmin
                        histzzp, bin_edgez, bin_edgezp = np.histogram2d(plotDataFrame["z"], plotDataFrame["zp"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgez)):
                            xcords.append(0.5*(bin_edgez[indx-1]+bin_edgez[indx]) + cogz)
                        for indx in range(1, len(bin_edgezp)):
                            ycords.append(0.5*(bin_edgezp[indx-1]+bin_edgezp[indx]) + cogzp)
                        f = interpolate.interp2d(xcords, ycords, histzzp, kind='linear')
                        hticksz3 = (zpmax-zpmin)*0.01 
                        vticksz3 = (zmax-zmin)*0.01
                        xstep = (zmax-zmin)/newbins
                        ystep = (zpmax-zpmin)/newbins
                        xnew = np.arange(zmin + cogz ,  zmax + cogz,  xstep)
                        ynew = np.arange(zpmin + cogzp, zpmax + cogzp, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(zmin + cogz, zpmin + cogzp)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p3.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p3.plot(ELLZ + cogz, ELLZP + cogzp, pen=pg.mkPen('g', width=2))
                        if (emivals_selected == True ):   
                        # add emittance valuess to the top 3 plots
#                            exlabel=pg.TextItem(anchor=(0.5,0.5), border='r', fill=(255,255,255))
                            exlabel=pg.TextItem(anchor=(0.5,0.5))
                            eylabel=pg.TextItem(anchor=(0.5,0.5))
                            ezlabel=pg.TextItem(anchor=(0.5,0.5))
                            if(emivals_bottom == True):
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.97*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.97*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.97*ezlab_vrange)
                            else:
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.03*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.03*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.03*ezlab_vrange)
                            exlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ex,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emitx)))
                            p1.addItem(exlabel)    
                            eylabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ey,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emity)))
                            p2.addItem(eylabel)    
                            ezlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ez,rms=%6.3f MeV.deg </span></div>'%(math.sqrt(emitz)))
                            p3.addItem(ezlabel) 
                                                   
                        # bottom left plot
                        plotDataFrame = myDataFrame
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]+cogx > xvals[0]) & (plotDataFrame["x"]+cogx < xvals[1]) & (plotDataFrame["y"]+cogy > yvals[0]) & (plotDataFrame["y"]+cogy < yvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]>xvals[0]) & (plotDataFrame["x"]<xvals[1]) & (plotDataFrame["y"]>yvals[0]) & (plotDataFrame["y"]<yvals[1])]    
                            xmin=np.nanmin(plotDataFrame["x"].values)
                            xmax=np.nanmax(plotDataFrame["x"].values)  
                            ymin=np.nanmin(plotDataFrame["y"].values)
                            ymax=np.nanmax(plotDataFrame["y"].values)  
                            if(colormap_name == "jet"): 
                                p4.setRange(xRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                                p4.setRange(yRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                        histxy, bin_edgex, bin_edgey = np.histogram2d(plotDataFrame["x"], plotDataFrame["y"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgex)):
                            xcords.append(0.5*(bin_edgex[indx-1]+bin_edgex[indx]) + cogx)
                        for indx in range(1, len(bin_edgey)):
                            ycords.append(0.5*(bin_edgey[indx-1]+bin_edgey[indx]) + cogy)
                        f = interpolate.interp2d(xcords, ycords, histxy, kind='linear')
                        xstep = (xmax-xmin)/newbins
                        ystep = (ymax-ymin)/newbins
                        xnew = np.arange(xmin + cogx, xmax + cogx, xstep)
                        ynew = np.arange(ymin + cogy, ymax + cogy, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(xmin + cogx, ymin + cogy)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p4.addItem(twodplot)
                        # bottom middle plot
                        plotDataFrame = myDataFrame
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]+cogz > zvals[0]) & (plotDataFrame["z"]+cogz < zvals[1]) & (plotDataFrame["x"]+cogx > xvals[0]) & (plotDataFrame["x"]+cogx < xvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]>zvals[0]) & (plotDataFrame["z"]<zvals[1]) & (plotDataFrame["x"]>xvals[0]) & (plotDataFrame["x"]<xvals[1])]    
                            zmin=np.nanmin(plotDataFrame["z"].values)
                            zmax=np.nanmax(plotDataFrame["z"].values)
                            ymin=np.nanmin(plotDataFrame["x"].values)
                            ymax=np.nanmax(plotDataFrame["x"].values)  
                            if(colormap_name == "jet"): 
                                p5.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                                p5.setRange(yRange=[xmin+cogx,xmax+cogx],padding=pad_size)
                        histzx, bin_edgez, bin_edgex = np.histogram2d(plotDataFrame["z"], plotDataFrame["x"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgez)):
                            xcords.append(0.5*(bin_edgez[indx-1]+bin_edgez[indx]) + cogz)
                        for indx in range(1, len(bin_edgex)):
                            ycords.append(0.5*(bin_edgex[indx-1]+bin_edgex[indx]) + cogx)
                        f = interpolate.interp2d(xcords, ycords, histzx, kind='linear')
                        xstep = (zmax-zmin)/newbins
                        ystep = (xmax-xmin)/newbins
                        xnew = np.arange(zmin + cogz, zmax + cogz, xstep)
                        ynew = np.arange(xmin + cogx, xmax + cogx, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(zmin + cogz, xmin + cogx)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p5.addItem(twodplot)
                        # bottom right plot
                        plotDataFrame = myDataFrame
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]+cogz > zvals[0]) & (plotDataFrame["z"]+cogz < zvals[1]) & (plotDataFrame["y"]>yvals[0]) & (plotDataFrame["y"]<yvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]>zvals[0]) & (plotDataFrame["z"]<zvals[1]) & (plotDataFrame["y"]>yvals[0]) & (plotDataFrame["y"]<yvals[1])]    
                            zmin=np.nanmin(plotDataFrame["z"].values)
                            zmax=np.nanmax(plotDataFrame["z"].values)
                            ymin=np.nanmin(plotDataFrame["y"].values)
                            ymax=np.nanmax(plotDataFrame["y"].values)  
                            if(colormap_name == "jet"): 
                                p6.setRange(xRange=[zmin+cogz,zmax+cogz],padding=pad_size)
                                p6.setRange(yRange=[ymin+cogy,ymax+cogy],padding=pad_size)
                        histzy, bin_edgez, bin_edgey = np.histogram2d(plotDataFrame["z"], plotDataFrame["y"], nbins, normed = True)
                        xcords = [ ]
                        ycords = [ ]
                        for indx in range(1, len(bin_edgez)):
                            xcords.append(0.5*(bin_edgez[indx-1]+bin_edgez[indx]) + cogz)
                        for indx in range(1, len(bin_edgey)):
                            ycords.append(0.5*(bin_edgey[indx-1]+bin_edgey[indx]) + cogy)
                        f = interpolate.interp2d(xcords, ycords, histzy, kind='linear')
                        xstep = (zmax-zmin)/newbins
                        ystep = (ymax-ymin)/newbins
                        xnew = np.arange(zmin + cogz, zmax + cogz, xstep)
                        ynew = np.arange(ymin + cogy, ymax + cogy, ystep)
                        znew = f(xnew, ynew)
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(zmin + cogz, ymin + cogy)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(znew)
                        p6.addItem(twodplot)
                    if(KDE_selected != 0 ):                         
                    # Perform Kernel Density Estimate (KDE)
                        # top left plot
                        plotDataFrame = myDataFrame   
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]+cogx > xvals[0]) & (plotDataFrame["x"]+cogx < xvals[1]) & (plotDataFrame["xp"]+cogxp > xpvals[0]) & (plotDataFrame["xp"] + cogxp < xpvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(myDataFrame["x"]>xvals[0]) & (myDataFrame["x"]<xvals[1]) & (myDataFrame["xp"]>xpvals[0]) & (myDataFrame["xp"]<xpvals[1])]    
                            xmin=xvals[0]
                            xmax=xvals[1]                
                            xpmin=xpvals[0]
                            xpmax=xpvals[1]
                        if(GRS=="Auto"):
                            if(COG_selected == True):
                                xmin=np.nanmin(plotDataFrame["x"].values) + cogx
                                xmax=np.nanmax(plotDataFrame["x"].values) + cogx
                                xpmin=np.nanmin(plotDataFrame["xp"].values) + cogxp
                                xpmax=np.nanmax(plotDataFrame["xp"].values) + cogxp
                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]+cogx > xmin) & (plotDataFrame["x"]+cogx < xmax) & (plotDataFrame["xp"]+cogxp > xpmin) & (plotDataFrame["xp"] + cogxp < xpmax)]    
                                if(colormap_name == "jet"): 
                                    p1.setRange(xRange=[xmin,xmax],padding=pad_size)
                                    p1.setRange(yRange=[xpmin,xpmax],padding=pad_size)  
                        xx, yy = np.mgrid[xmin:xmax:n_of_KDE_bins*1j, xpmin:xpmax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogx + xx.ravel(), cogxp + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogx + plotDataFrame["x"].values, cogxp + plotDataFrame["xp"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        hticksz1 = (xpmax-xpmin)*0.01 
                        vticksz1 = (xmax-xmin)*0.01 
                        xstep=(xmax-xmin)/n_of_KDE_bins
                        ystep=(xpmax-xpmin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
#                        twodplot.setPos(xmin + cogx, xpmin + cogxp)
                        twodplot.setPos(xmin, xpmin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p1.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p1.plot(ELLX + cogx, ELLXP + cogxp, pen=pg.mkPen('g', width=2))
                        # top middle plot
                        # Peform the kernel density estimate
                        plotDataFrame = myDataFrame    
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["y"]+cogy > yvals[0]) & (plotDataFrame["y"]+cogy < yvals[1]) & (plotDataFrame["yp"]+cogyp > ypvals[0]) & (plotDataFrame["yp"] + cogyp < ypvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(myDataFrame["y"]>yvals[0]) & (myDataFrame["y"]<yvals[1]) & (myDataFrame["yp"]>ypvals[0]) & (myDataFrame["yp"]<ypvals[1])]    
                            ymin=yvals[0]
                            ymax=yvals[1]                
                            ypmin=ypvals[0]
                            ypmax=ypvals[1]                
                        if(GRS=="Auto"):
                            if(COG_selected == True):
                                ymin=np.nanmin(plotDataFrame["y"].values) + cogy
                                ymax=np.nanmax(plotDataFrame["y"].values) + cogy
                                ypmin=np.nanmin(plotDataFrame["yp"].values) + cogyp
                                ypmax=np.nanmax(plotDataFrame["yp"].values) + cogyp
                                plotDataFrame = plotDataFrame[(plotDataFrame["y"]+cogy > ymin) & (plotDataFrame["y"]+cogy < ymax) & (plotDataFrame["yp"]+cogyp > ypmin) & (plotDataFrame["yp"] + cogyp < ypmax)]    
                                if(colormap_name == "jet"): 
                                    p2.setRange(xRange=[ymin,ymax],padding=pad_size)
                                    p2.setRange(yRange=[ypmin,ypmax],padding=pad_size)  
                        xx, yy = np.mgrid[ymin:ymax:n_of_KDE_bins*1j, ypmin:ypmax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogy + xx.ravel(), cogyp + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogy + plotDataFrame["y"].values, cogyp + plotDataFrame["yp"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        hticksz2 = (ypmax-ypmin)*0.01
                        vticksz2 = (ymax-ymin)*0.01
                        xstep=(ymax-ymin)/n_of_KDE_bins
                        ystep=(ypmax-ypmin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
#                        twodplot.setPos(ymin + cogy, ypmin + cogyp)
                        twodplot.setPos(ymin, ypmin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p2.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p2.plot(ELLY + cogy, ELLYP + cogyp, pen=pg.mkPen('g', width=2))
                        # top right plot
                        # Peform the kernel density estimate                        
                        plotDataFrame = myDataFrame    
                        if(GRS=="File"):
                            if(COG_selected == True):
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]+cogz > zvals[0]) & (plotDataFrame["z"]+cogz < zvals[1]) & (plotDataFrame["zp"]+cogzp > zpvals[0]) & (plotDataFrame["zp"] + cogzp < zpvals[1])]    
                            else: 
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]>zvals[0]) & (plotDataFrame["z"]<zvals[1]) & (plotDataFrame["zp"]>zpvals[0]) & (plotDataFrame["zp"]<zpvals[1])]    
                            zmin=zvals[0]
                            zmax=zvals[1]                
                            zpmin=zpvals[0]
                            zpmax=zpvals[1]                
                        if(GRS=="Auto"):
                            if(COG_selected == True):
                                zmin=np.nanmin(plotDataFrame["z"].values) + cogz
                                zmax=np.nanmax(plotDataFrame["z"].values) + cogz
                                zpmin=np.nanmin(plotDataFrame["zp"].values) + cogzp
                                zpmax=np.nanmax(plotDataFrame["zp"].values) + cogzp
                                plotDataFrame = plotDataFrame[(plotDataFrame["z"]+cogz > zmin) & (plotDataFrame["z"]+cogz < zmax) & (plotDataFrame["zp"]+cogzp > zpmin) & (plotDataFrame["zp"] + cogzp < zpmax)]    
                                if(colormap_name == "jet"): 
                                    p3.setRange(xRange=[zmin,zmax],padding=pad_size)
                                    p3.setRange(yRange=[zpmin,zpmax],padding=pad_size)  
                                
                        xx, yy = np.mgrid[zmin:zmax:n_of_KDE_bins*1j, zpmin:zpmax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogz + xx.ravel(), cogzp + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogz + plotDataFrame["z"].values, cogzp + plotDataFrame["zp"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        hticksz3 = (zpmax-zpmin)*0.01
                        vticksz3 = (zmax-zmin)*0.01 
                        xstep=(zmax-zmin)/n_of_KDE_bins
                        ystep=(zpmax-zpmin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
                        twodplot.setPos(zmin + cogz, zpmin + cogzp)
                        twodplot.setPos(zmin, zpmin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p3.addItem(twodplot)
                        if(plot_ellipse == True ): 
                            p3.plot(ELLZ + cogz, ELLZP + cogzp, pen=pg.mkPen('g', width=2))
                        if (emivals_selected == True ):   
                        # add emittance values to the top 3 plots
                            exlabel=pg.TextItem(anchor=(0.5,0.5))
                            eylabel=pg.TextItem(anchor=(0.5,0.5))
                            ezlabel=pg.TextItem(anchor=(0.5,0.5))
                            if(emivals_bottom == True):
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.97*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.97*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.97*ezlab_vrange)
                            else:
                                exlabel.setPos(exlab_hmin+0.5*exlab_hrange,exlab_vmax-0.03*exlab_vrange)
                                eylabel.setPos(eylab_hmin+0.5*eylab_hrange,eylab_vmax-0.03*eylab_vrange)
                                ezlabel.setPos(ezlab_hmin+0.5*ezlab_hrange,ezlab_vmax-0.03*ezlab_vrange)
                            exlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ex,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emitx)))
                            p1.addItem(exlabel)    
                            eylabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ey,n,rms=%1.5f mm.mrad </span></div>'%(10.*rel_beta*rel_gamma*math.sqrt(emity)))
                            p2.addItem(eylabel)    
                            ezlabel.setHtml('<div style="text-align: center"><span style="color: #ff3336;">Ez,rms=%6.3f MeV.deg </span></div>'%(math.sqrt(emitz)))
                            p3.addItem(ezlabel)                        
                            
                        # bottom left plot
                        # Peform the kernel density estimate                        
#                            if(COG_selected == True):
#                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]+cogx > xvals[0]) & (plotDataFrame["x"]+cogx < xvals[1]) & (plotDataFrame["y"]+cogy > yvals[0]) & (plotDataFrame["y"]+cogy < yvals[1])]    
#                            else: 
#                                plotDataFrame = plotDataFrame[(plotDataFrame["x"]>xvals[0]) & (plotDataFrame["x"]<xvals[1]) & (plotDataFrame["y"]>yvals[0]) & (plotDataFrame["y"]<yvals[1])]    
                        xx, yy = np.mgrid[xmin:xmax:n_of_KDE_bins*1j, ymin:ymax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogx + xx.ravel(), cogy + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogx + plotDataFrame["x"].values, cogy + plotDataFrame["y"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        xstep=(xmax-xmin)/n_of_KDE_bins
                        ystep=(ymax-ymin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
#                        twodplot.setPos(xmin + cogx, ymin + cogy)
                        twodplot.setPos(xmin, ymin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p4.addItem(twodplot)
                        # bottom middle plot
                        # Peform the kernel density estimate
                        xx, yy = np.mgrid[zmin:zmax:n_of_KDE_bins*1j, xmin:xmax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogz + xx.ravel(), cogx + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogz + plotDataFrame["z"].values, cogx + plotDataFrame["x"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        xstep=(zmax-zmin)/n_of_KDE_bins
                        ystep=(xmax-xmin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
#                        twodplot.setPos(zmin + cogz, xmin + cogx)
                        twodplot.setPos(zmin, xmin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p5.addItem(twodplot)
                        # bottom right plot
                        # Peform the kernel density estimate                        
                        xx, yy = np.mgrid[zmin:zmax:n_of_KDE_bins*1j, ymin:ymax:n_of_KDE_bins*1j]
#                        positions = np.vstack([cogz + xx.ravel(), cogy + yy.ravel()])
                        positions = np.vstack([xx.ravel(), yy.ravel()])
                        values = np.vstack([cogz + plotDataFrame["z"].values, cogy + plotDataFrame["y"].values])
                        kernel = stats.gaussian_kde(values)
                        f = np.reshape(kernel(positions).T, xx.shape)
                        xstep=(zmax-zmin)/n_of_KDE_bins
                        ystep=(ymax-ymin)/n_of_KDE_bins
                        twodplot = pg.ImageItem()
                        twodplot.scale(xstep, ystep)
#                        twodplot.setPos(zmin + cogz, ymin + cogy)
                        twodplot.setPos(zmin, ymin)
                        # Apply the colormap
                        twodplot.setLookupTable(lut)
                        twodplot.setImage(f)
                        p6.addItem(twodplot)
                if(self.checkBox2.isChecked() != 0 ):
#               Plot of beam profiles
                    ##############################################################################
                    if(colormap_name != 'jet'):
                        hticksz1 = 0.
                        vticksz1 = 0. 
                        hticksz2 = 0.
                        vticksz2 = 0. 
                        hticksz3 = 0.
                        vticksz3 = 0.                        
#                   X-XP profiles
                    # reset arrays first (avoid using old, out of bound parts)
                    xranges = p1.viewRange()
                    try:
                        del profxraw
                        del profyraw
                        del profx
                        del profy
                        del binctrx
                        del binctry
                        del binvalx
                        del binvaly
                        binctrx={}
                        binctry={}
                        binvalx={}
                        binvaly={}
                    except:
                    # do nothing
                        i = 0
                    histx, bin_edgex  = np.histogram(myDataFrame["x"],  density=False, bins=nbins)
                    histy, bin_edgey  = np.histogram(myDataFrame["xp"], density=False, bins=nbins)
                    binmax=float(histx[0])
                    binmay=float(histy[0])
                    for i in range(0,nbins):
                        binctrx[i] = 0.5*(bin_edgex[i] + bin_edgex[i+1])
                        binctry[i] = 0.5*(bin_edgey[i] + bin_edgey[i+1])
                        binvalx[i] = float(histx[i])
                        binvaly[i] = float(histy[i])
                        if(binvalx[i] > binmax):
                            binmax = binvalx[i]
                        if(binvaly[i] > binmay):
                            binmay = binvaly[i]
                    for i in range(0,nbins):
#                        binvaly[i] = (binvaly[i]/binmay)*(xmax-xmin)/fit_amp
#                        binvalx[i] = (binvalx[i]/binmax)*(xpmax-xpmin)/fit_amp
                        binvaly[i] = (binvaly[i]/binmay)*(xranges[0][1]-xranges[0][0])/fit_amp
                        binvalx[i] = (binvalx[i]/binmax)*(xranges[1][1]-xranges[1][0])/fit_amp
                    profxraw = pd.Series(binctrx)
                    profyraw = pd.Series(binvalx) 
                    profx = pd.Series(binctrx)
                    profy = pd.Series(binvalx) 
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):   
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff=0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                        print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        if(rangex and GRS=="File"):                    
                            step = bin_edgex[1]-bin_edgex[0]
                            nfbins = int((xvals[1]-xvals[0])/step)
                            step = (xmax-xmin)/nfbins
                            for i in range(0,nfbins):
                                binctrx[i] = xmin + step/2 + i * step
                                binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
                            p1.plot(cogx + profx.values, hticksz1 + xranges[1][0] + profy.values, pen='g')
                        else:    
                            p1.plot(cogx + profxraw.values, hticksz1 + xranges[1][0] + result.best_fit, pen='g')
                    if(pro_raw != 0 ):
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p1.plot(cogx + profxraw.values, hticksz1 + xranges[1][0] + profyraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212))
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p1.plot(cogx + profxraw.values, hticksz1 + xranges[1][0] + profyraw.values, pen=yellow)
                            else:
                                p1.plot(cogx + profxraw.values, hticksz1 + xranges[1][0] + profyraw.values, pen='r')
                    del profxraw
                    del profyraw
                    del profx
                    del profy
                    profxraw = pd.Series(binctry)
                    profyraw = pd.Series(binvaly)
                    profx = pd.Series(binctry)
                    profy = pd.Series(binvaly)
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff = 0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                        print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        flof = result.best_values['lof']
                        if(rangexp and GRS=="File"):                    
                            del profx
                            del profy
                            del binctrx
                            del binvalx
                            binctrx={}
                            binvalx={}
                            step = bin_edgey[1]-bin_edgey[0]
                            nfbins = int((xpvals[1]-xpvals[0])/step)
                            step = (xpmax-xpmin)/nfbins
                            for i in range(0,nfbins):
                                binctrx[i] = xpmin + step/2 + i * step
                                binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
                            p1.plot(vticksz1 + xranges[0][0] + profy.values, cogxp + profx.values, pen='g')
                        else:    
                            p1.plot(vticksz1 + xranges[0][0] + result.best_fit, cogxp + profxraw.values, pen='g')
                    if(pro_raw != 0 ):
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p1.plot(vticksz1 + xranges[0][0] + profyraw.values, cogxp + profxraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212)) 
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p1.plot(vticksz1 + xranges[0][0] + profyraw.values, cogxp + profxraw.values, pen=yellow)
                            else:
                                p1.plot(vticksz1 + xranges[0][0] + profyraw.values, cogxp + profxraw.values, pen='r')
                    ############################################################################## 
#                   Y-YP profiles                        
                    yranges = p2.viewRange()
                    del profxraw
                    del profyraw
                    del profx
                    del profy
                    del binctrx
                    del binctry
                    del binvalx
                    del binvaly
                    binctrx={}
                    binctry={}
                    binvalx={}
                    binvaly={}
                    histx, bin_edgex  = np.histogram(myDataFrame["y"],  density=False, bins=nbins)
                    histy, bin_edgey  = np.histogram(myDataFrame["yp"], density=False, bins=nbins)
                    binmax=float(histx[0])
                    binmay=float(histy[0])
                    for i in range(0,nbins):
                        binctrx[i] = 0.5*(bin_edgex[i] + bin_edgex[i+1])
                        binctry[i] = 0.5*(bin_edgey[i] + bin_edgey[i+1])
                        binvalx[i] = float(histx[i])
                        binvaly[i] = float(histy[i])
                        if(binvalx[i] > binmax):
                            binmax = binvalx[i]
                        if(binvaly[i] > binmay):
                            binmay = binvaly[i]
                    for i in range(0,nbins):
#                        binvaly[i] = (binvaly[i]/binmay)*(ymax-ymin)/fit_amp
#                        binvalx[i] = (binvalx[i]/binmax)*(ypmax-ypmin)/fit_amp
                        binvaly[i] = (binvaly[i]/binmay)*(yranges[0][1]-yranges[0][0])/fit_amp
                        binvalx[i] = (binvalx[i]/binmax)*(yranges[1][1]-yranges[1][0])/fit_amp
                    profxraw = pd.Series(binctrx)
                    profyraw = pd.Series(binvalx) 
                    profx = pd.Series(binctrx)
                    profy = pd.Series(binvalx)
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):   
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff=0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                        print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        if(rangey and GRS=="File"):                    
                            step = bin_edgex[1]-bin_edgex[0]
                            nfbins = int((yvals[1]-yvals[0])/step)
                            step = (ymax-ymin)/nfbins
                            for i in range(0,nfbins):
                                binctrx[i] = ymin + step/2 + i * step
                                binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
                            p2.plot(cogy + profx.values, hticksz2 + yranges[1][0] + profy.values, pen='g')
                        else:    
                            p2.plot(cogy + profxraw.values, hticksz2 + yranges[1][0] + result.best_fit, pen='g')
                    if(pro_raw != 0 ):
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p2.plot(cogy + profxraw.values, hticksz2 + yranges[1][0] + profyraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212)) 
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p2.plot(cogy + profxraw.values, hticksz2 + yranges[1][0] + profyraw.values, pen=yellow)
                            else:
                                p2.plot(cogy + profxraw.values, hticksz2 + yranges[1][0] + profyraw.values, pen='r')
                    del profxraw
                    del profyraw
                    del profx
                    del profy
                    profxraw = pd.Series(binctry)
                    profyraw = pd.Series(binvaly)
                    profx = pd.Series(binctry)
                    profy = pd.Series(binvaly) 
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):   
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff=0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                        print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        if(rangeyp and GRS=="File"):                    
                            del profx
                            del profy
                            del binctrx
                            del binvalx
                            binctrx={}
                            binvalx={}
                            step = bin_edgey[1]-bin_edgey[0]
                            nfbins = int((ypvals[1]-ypvals[0])/step)
                            step = (ypmax-ypmin)/nfbins
                            fslope = 0.
                            for i in range(0,nfbins):
                                binctrx[i] = ypmin + step/2 + i * step
                                binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
                            p2.plot(vticksz2 + yranges[0][0] + profy.values, cogyp + profx.values, pen='g')
                        else:    
                            p2.plot(vticksz2 + yranges[0][0] + result.best_fit, cogyp + profxraw.values, pen='g')
                    if(pro_raw != 0 ): 
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p2.plot(vticksz2 + yranges[0][0] + profyraw.values, cogyp + profxraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212)) 
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p2.plot(vticksz2 + yranges[0][0] + profyraw.values, cogyp + profxraw.values, pen=yellow)
                            else:
                                p2.plot(vticksz2 + yranges[0][0] + profyraw.values, cogyp + profxraw.values, pen='r')
                    ##############################################################################    
#                   Z-ZP profiles                        
                    zranges = p3.viewRange()
                    del profxraw
                    del profyraw
                    del profx
                    del profy
                    del binctrx
                    del binctry
                    del binvalx
                    del binvaly
                    binctrx={}
                    binctry={}
                    binvalx={}
                    binvaly={}
                    histx, bin_edgex  = np.histogram(myDataFrame["z"],  density=False, bins=nbins)
                    histy, bin_edgey  = np.histogram(myDataFrame["zp"], density=False, bins=nbins)
                    binmax=float(histx[0])
                    binmay=float(histy[0])
                    binmix=float(histx[0])
                    binmiy=float(histy[0])
                    for i in range(0,nbins):
                        binctrx[i] = 0.5*(bin_edgex[i] + bin_edgex[i+1])
                        binctry[i] = 0.5*(bin_edgey[i] + bin_edgey[i+1])
                        binvalx[i] = float(histx[i])
                        binvaly[i] = float(histy[i])
                        if(binvalx[i] > binmax):
                            binmax = binvalx[i]
#                            xmaxat = binctrx[i]
                        if(binvaly[i] > binmay):
                            binmay = binvaly[i]
                        if(binvalx[i] < binmix):
                            binmix = binvalx[i]
                        if(binvaly[i] < binmiy):
                            binmiy = binvaly[i]
                    for i in range(0,nbins):
#                        binvaly[i] = (binvaly[i]/binmay)*(zmax-zmin)/fit_amp
#                        binvalx[i] = (binvalx[i]/binmax)*(zpmax-zpmin)/fit_amp
                        binvaly[i] = (binvaly[i]/binmay)*(zranges[0][1]-zranges[0][0])/fit_amp
                        binvalx[i] = (binvalx[i]/binmax)*(zranges[1][1]-zranges[1][0])/fit_amp
                    profxraw = pd.Series(binctrx)
                    profyraw = pd.Series(binvalx)
                    profx = pd.Series(binctrx)
                    profy = pd.Series(binvalx) 
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):   
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
#                        xbar = xmaxat
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff=0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                    print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        if(rangez and GRS=="File"):                    
                            step = bin_edgex[1]-bin_edgex[0]
                            nfbins = int((zvals[1]-zvals[0])/step)
                            step = (zmax-zmin)/nfbins
                            for i in range(0,nfbins):
                                binctrx[i] = zmin + step/2 + i * step
                                binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
                            p3.plot(cogz + profx.values, hticksz3 + zranges[1][0] + profy.values, pen='g')
                        else:    
                            p3.plot(cogz + profxraw.values, hticksz3 + zranges[1][0] + result.best_fit, pen='g')
                    if(pro_raw != 0 ): 
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p3.plot(cogz + profxraw.values, hticksz3 + zranges[1][0] + profyraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212)) 
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p3.plot(cogz + profxraw.values, hticksz3 + zranges[1][0] + profyraw.values, pen=yellow)
                            else:
                                p3.plot(cogz + profxraw.values, hticksz3 + zranges[1][0] + profyraw.values, pen='r')
                    del profxraw
                    del profyraw
                    del profx
                    del profy
                    profxraw = pd.Series(binctry)
                    profyraw = pd.Series(binvaly)
                    profx = pd.Series(binctry)
                    profy = pd.Series(binvaly) 
                    # make estimate of where center of Gaussian is; need to correct for offset in y
                    if(pro_fit != 0 ):   
                        slop = (profy.values[len(profy.values)-1]-profy.values[0])/(profx.values[len(profx.values)-1]-profx.values[0])
                        intcpt=profy.values[0]
                        yac=profy.values-(profx.values*slop+intcpt)
                        xbar = np.sum(profx.values*yac)/np.sum(yac)
                        width = np.sqrt(np.abs(np.sum(yac*(profx.values-xbar)**2)/np.sum(yac)))
                        ampl = 0.5*(max(yac)-min(yac))
                        loff=0.
                        mod = Model(gaussian) 
                        pars = mod.make_params(amp=ampl, cen=xbar, wid=width, lof=loff)
                        result = mod.fit(profy.values, pars, x=profx.values)
#                    print(result.fit_report())
                        flof = result.best_values['lof']
                        famp = result.best_values['amp']
                        fcen = result.best_values['cen']
                        fwid = result.best_values['wid']
                        if(rangezp and GRS=="File"):                    
                            del profx
                            del profy
                            del binctrx
                            del binvalx
                            binctrx={}
                            binvalx={}
                            step = bin_edgey[1]-bin_edgey[0]
                            nfbins = int((zpvals[1]-zpvals[0])/step)
                            step = (zpmax-zpmin)/nfbins
                            for i in range(0,nfbins):
                                binctrx[i] = zpmin + step/2 + i * step
                                if(COG_selected == True and self.radio2.isChecked() != 0 and KDE_selected != 0):
                                    binvalx[i] = flof + famp * exp(-(binctrx[i])**2 / (2*fwid**2))
                                else:    
                                    binvalx[i] = flof + famp * exp(-(binctrx[i]-fcen)**2 / (2*fwid**2))
                            profx = pd.Series(binctrx)
                            profy = pd.Series(binvalx)
#                            if(COG_selected == True  and KDE_selected != 0):
#                                p3.plot(vticksz3 + zranges[0][0] + profy.values, profx.values, pen='g')
#                            else:
#                                p3.plot(vticksz3 + zranges[0][0] + profy.values, cogzp + profx.values, pen='g')
                            if(COG_selected == True  and self.radio2.isChecked() != 0 and KDE_selected != 0):
                                p3.plot(vticksz3 + zranges[0][0] + profy.values, profx.values, pen='g')
                            else:
                                p3.plot(vticksz3 + zranges[0][0] + profy.values, cogzp + profx.values, pen='g')
                        else:
                            p3.plot(vticksz3 + zranges[0][0] + result.best_fit, cogzp + profxraw.values, pen='g')
                    if(pro_raw != 0 ): 
                        if(self.radio1.isChecked() != 0) :
                        # scatter plots were chosen
                            p3.plot(vticksz3 + zranges[0][0] + profyraw.values, cogzp + profxraw.values, pen='r')
                        else:
                            if(colormap_name=="jet"):
                                aquamarine = pg.mkPen(color=(127, 255, 212)) 
                                yellow = pg.mkPen(color=(255, 255, 0))
                                p3.plot(vticksz3 + zranges[0][0] + profyraw.values, cogzp + profxraw.values, pen=yellow)
                            else:
                                p3.plot(vticksz3 + zranges[0][0] + profyraw.values, cogzp + profxraw.values, pen='r')
                self.win.show()
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % dfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message") 
#            print("Test: already done?")                                    
#            self.RightBtn1.setStyleSheet("color : #0000ff; ") 
            return



######################################################
    def plot_erms(self):                             #
        '''plot Erms'''                              #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
#    pfname = ifpath + os.sep + "dynac.print"
        pfname = ifpath + "dynac.print"
#        print("Using data from: ",pfname)

        if pfname:
            try:
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # read the remainder of the data
                myDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win1 = pg.GraphicsWindow(title=mytitle)
                self.win1.resize(1000,700)
                stitle = "Erms as a function of position"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win1.addLabel(stitle, row=0, col=0)
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = self.win1.addPlot(title="Transverse emittances", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(myDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                p1.plot(myDataFrame["l(m)"], myDataFrame["Ex,n,RMS(mm.mrd)"], pen='r', name='Ex')
                p1.plot(myDataFrame["l(m)"], myDataFrame["Ey,n,RMS(mm.mrd)"], pen='b', name='Ey')
                p1.setLabel('left', 'Ex, Ey (mm.mrad)')
                p1.setLabel('bottom', 'z (m)')
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win1.addPlot(title="Longitudinal emittance", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
                p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                p2.plot(myDataFrame["l(m)"], myDataFrame["Ez,RMS(keV.ns)"], pen="#000000", name='Ez')
                p2.setLabel('left', 'Ez (keV.ns)')
                p2.setLabel('bottom', 'z (m)')
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return

######################################################
    def plot_energy(self):                           #
        '''plot energy and synchronous phase'''      #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
#    pfname = ifpath + os.sep + "dynac.print"
        pfname   = ifpath + "dynac.print"
        dmpfname = ifpath + "dynac.dmp"
#        print("Using data from 1: ",pfname)
#        print("Using data from 2: ",dmpfname)
        if pfname:
            try:
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the data, filter out the lines that contain the # character, and convert to numbers
                dmpDataFrame = pd.read_csv(dmpfname, skiprows=3, sep='\s+', header=None, names=["element", "Z", "trans", "PHIs", "TOF(COG)", "Beta(COG)", "Wcog", "TOF(REF)", "Beta(REF)", "Wref", "Ex,RMS,n", "Ey,RMS,n", "El,RMS", "dWref", "EffVolt"])
#                dmpDataFrame=dmpDataFrame[~dmpDataFrame.element.str.contains("#")]
                if(dmpDataFrame.dtypes.element == 'object'): dmpDataFrame=dmpDataFrame[~dmpDataFrame.element.str.contains("#")]
                dmpDataFrame=dmpDataFrame.apply(pd.to_numeric, errors='coerce')
                printDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
#                printDataFrame=printDataFrame[~printDataFrame.element.str.contains("#")]
#                printDataFrame=printDataFrame.apply(pd.to_numeric, errors='coerce')
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win2 = pg.GraphicsWindow(title=mytitle)
                self.win2.resize(1000,700)
                stitle = "Energy and synchronous phase as a function of position"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win2.addLabel(stitle, row=0, col=0)
                # set up the 2 grafs                
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = self.win2.addPlot(title="Energy", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(printDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                p1.plot(printDataFrame["l(m)"], printDataFrame["Wcog(MeV)"], pen='r', name='Wcog')
                p1.plot(printDataFrame["l(m)"], printDataFrame["Wref(MeV)"], pen='b', name='Wref')
                p1.setLabel('left', 'Wtotal (MeV)')
                p1.setLabel('bottom', 'z (m)')
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win2.addPlot(title="Synchronous Phase", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
#                p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                phis="\N{GREEK SMALL LETTER PHI}" + "<SUB> s</SUB>"
#                phis="\N{LATIN SUBSCRIPT SMALL LETTER S}"
#                phis = 'PHIs'
#                p2.plot(dmpDataFrame["Z"], dmpDataFrame["PHIs"], pen="#000000", name=phis)
#  BUG               legend (name = 'phis') doesn't work
#                scatterplot = pg.ScatterPlotItem(dmpDataFrame["Z"], dmpDataFrame["PHIs"], name = 'phis', symbol='o', size=4., pen=pg.mkPen(None), brush = 'b')
                scatterplot = pg.ScatterPlotItem(dmpDataFrame["Z"], dmpDataFrame["PHIs"], symbol='o', size=4., pen=pg.mkPen(None), brush = 'b')
                p2.addItem(scatterplot)
                
                p2.setLabel('left', 'Phase (deg)')
                p2.setLabel('bottom', 'z (m)')
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return

######################################################
    def plot_t_envelopes(self):                      #
        '''plot transverse envelopes'''              #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
#    pfname = ifpath + os.sep + "dynac.print"
        pfname = ifpath + "dynac.print"
#        print("Using data from: ",pfname)

        if pfname:
            try:
                ellength=np.zeros(10000)
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # read the remainder of the data
                myDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win3 = pg.GraphicsWindow(title=mytitle)
                self.win3.resize(1000,700)
                stitle = "No plots selected"
                if (self.checkBox4.isChecked() != 0 ):   
                    stitle = "RMS beam size"
                if (self.checkBox5.isChecked() != 0 ):   
                    stitle = "Beam extent"
                if (self.checkBox4.isChecked() != 0 ) and (self.checkBox5.isChecked() != 0 ):            
                    stitle = "Beam extent and RMS beam size"
                if (self.checkBox4.isChecked() == 0 ) and (self.checkBox5.isChecked() == 0 ) and (self.checkBox8.isChecked() != 0):            
                    stitle = "Beam line elements"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win3.addLabel(stitle, row=0, col=0)
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = self.win3.addPlot(title="Horizontal beam size", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                if (self.checkBox4.isChecked() != 0 ) or (self.checkBox5.isChecked() != 0 ):            
                    p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(myDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                if (self.checkBox4.isChecked() != 0 ): 
                    exmax=math.ceil(np.nanmax(myDataFrame["x(mm)"].values))
                    eheight = 0.05 * exmax
                    eoffset = 0. 
                    p1.setYRange(0.,exmax,padding=0)
                    p1.plot(myDataFrame["l(m)"], myDataFrame["x(mm)"], pen='r', name='Xrms')
                if (self.checkBox5.isChecked() != 0 ):   
                    xext="X" + "<SUB> ext</SUB>"   
                    exmax=math.ceil(np.nanmax(myDataFrame["xmax(mm)"].values))
                    exmin=math.ceil(np.nanmax(myDataFrame["xmin(mm)"].values))
                    if (abs(exmin) >> exmax ):
                        exmax = abs(exmin)
                    eheight = 0.1 * exmax
                    eoffset = -0.5 * eheight 
                    p1.setYRange(-exmax,exmax,padding=0)
                    p1.plot(myDataFrame["l(m)"], myDataFrame["xmax(mm)"], pen="#000000", name='Xext')
                    p1.plot(myDataFrame["l(m)"], myDataFrame["xmin(mm)"], pen="#000000")
                if (self.checkBox4.isChecked() == 0 ) and (self.checkBox5.isChecked() == 0 ) and (self.checkBox8.isChecked() != 0):            
                    exmax=math.ceil(np.nanmax(myDataFrame["x(mm)"].values))
                    eheight = 0.05 * exmax
                    eoffset = 0. 
                    p1.setYRange(0.,exmax,padding=0)
                p1.setLabel('left', 'X (mm)')
                p1.setLabel('bottom', 'z (m)')
#                myrect = np.array([  [3,2],[3,3],[4,3],[4,2],[3,2]  ])
#                qitem = pg.PlotDataItem(myrect, fillLevel=True, pen=pg.mkPen('b', width=2), brush = 'g')
#                p1.addItem(qitem)
#               number of rows: myDataFrame.shape[0],  number of columns: myDataFrame.shape[1]
                if (self.checkBox8.isChecked() != 0 ):   
                    nelements=-1+myDataFrame.shape[0]
#                    print("Number of beam line elements=",nelements)
                    indx=1
                    newindx=0
# {'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'},  
# blue, green, red, cyan, magenta, yellow, black, and white
                    while indx < nelements+1:
                        if (myDataFrame["ELEMENT"][indx] != "DRIFT" ):
                            #set default colour for the element border to black             
                            elcolor='r'
                            elbcolor='k'
                            newindx = newindx +1 
                            myrect = np.array([  [myDataFrame["l(m)"][indx-1],eoffset],
                                [myDataFrame["l(m)"][indx-1],eoffset+eheight],
                                [myDataFrame["l(m)"][indx],eoffset+eheight],
                                [myDataFrame["l(m)"][indx],eoffset],
                                [myDataFrame["l(m)"][indx-1],eoffset]  ])
                            if (myDataFrame["ELEMENT"][indx] == "RFQPTQ" ):
                                elcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "RFQPTQ" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">RFQ</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVSC" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.9,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">C</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVMC" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.8,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">CA</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVNUM" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.8,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">CA</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUADRUPO" ):
                                elcolor='r'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUADRUPO" ):
                                    ellabel = pg.TextItem(anchor=(0.4,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUAFK" ):
                                elcolor='r'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUAFK" ):
                                    ellabel = pg.TextItem(anchor=(0.4,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "BUNCHER" ):
                                elcolor='g'
                                elbcolor='g'
#                                ellabel = pg.TextItem(anchor=(0.,0.), border='w', fill=(0,0,255))
                                ellabel = pg.TextItem(anchor=(0.5,0.8))
#                                ellabel.setHtml('<div style="text-align: center"><span style="color: #FFF;">Vmax=%0.1f mm/s @ %0.1f s</span></div>'%(np.abs(signemax),tmax))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">B</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "MHB" ):
                                elcolor='g'
                                elbcolor='g'
                                ellabel = pg.TextItem(anchor=(0.9,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">MHB</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "BMAGNET" ):
                                elcolor='y'
                                elbcolor='k'
                                if (myDataFrame["ELEMENT"][indx-1] != "BMAGNET" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">DI</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUAELEC" ):
                                elcolor='r'
                                elbcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUAELEC" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "EDFLEC" ):
                                elcolor='y'
                                elbcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "EDFLEC" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">DI</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "SOLENO" ):
                                elcolor='c'
                                if (myDataFrame["ELEMENT"][indx-1] != "SOLENO" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">S</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "SEXTUPO" ):
                                elcolor='m'
                                if (myDataFrame["ELEMENT"][indx-1] != "SEXTUPO" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">SX</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUADSXT" ):
                                elcolor='r'
#                                elbcolor='m'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUADSXT" ):
                                    ellabel = pg.TextItem(anchor=(0.3,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">QS</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p1.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "FSOLE" ):
                                elcolor='c'
                                ellabel = pg.TextItem(anchor=(0.,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">S</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p1.addItem(ellabel)
                            else:
                                elcolor='w'
                                elbcolor='k'
                            qitem = pg.PlotDataItem(myrect, fillLevel=True, pen=pg.mkPen(elbcolor, width=2), brush = elcolor)
                            p1.addItem(qitem)
                        indx = indx + 1
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win3.addPlot(title="Vertical beam size", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
                if (self.checkBox4.isChecked() != 0 ) or (self.checkBox5.isChecked() != 0 ):            
                    p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                if (self.checkBox4.isChecked() != 0 ):   
                    eymax=math.ceil(np.nanmax(myDataFrame["y(mm)"].values))
                    eheight = 0.05 * eymax
                    eoffset = 0. 
                    p2.setYRange(0.,eymax,padding=0)
                    p2.plot(myDataFrame["l(m)"], myDataFrame["y(mm)"], pen='b', name='Yrms')
                if (self.checkBox5.isChecked() != 0 ):
                    yext="Y" + "<SUB> ext</SUB>"   
                    eymax=math.ceil(np.nanmax(myDataFrame["ymax(mm)"].values))
                    eymin=math.ceil(np.nanmax(myDataFrame["ymin(mm)"].values))
                    if (abs(eymin) >> eymax ):
                        eymax = abs(eymin)
                    eheight = 0.1 * eymax
                    eoffset = -0.5 * eheight 
                    p2.setYRange(-eymax,eymax,padding=0)
                    p2.plot(myDataFrame["l(m)"], myDataFrame["ymax(mm)"], pen="#000000", name='Yext')
                    p2.plot(myDataFrame["l(m)"], myDataFrame["ymin(mm)"], pen="#000000")
                if (self.checkBox4.isChecked() == 0 ) and (self.checkBox5.isChecked() == 0 ) and (self.checkBox8.isChecked() != 0):            
                    eymax=math.ceil(np.nanmax(myDataFrame["y(mm)"].values))
                    eheight = 0.05 * eymax
                    eoffset = 0. 
                    p2.setYRange(0.,eymax,padding=0)
                p2.setLabel('left', 'Y (mm)')
                p2.setLabel('bottom', 'z (m)')
                if (self.checkBox8.isChecked() != 0 ):   
                    indx=1
                    newindx=0
                    while indx < nelements+1:
                        if (myDataFrame["ELEMENT"][indx] != "DRIFT" ):
                            #set default colour for the element border to black             
                            elcolor='r'
                            elbcolor='k'
                            newindx = newindx +1 
                            myrect = np.array([  [myDataFrame["l(m)"][indx-1],eoffset],
                                [myDataFrame["l(m)"][indx-1],eoffset+eheight],
                                [myDataFrame["l(m)"][indx],eoffset+eheight],
                                [myDataFrame["l(m)"][indx],eoffset],
                                [myDataFrame["l(m)"][indx-1],eoffset]  ])
                            if (myDataFrame["ELEMENT"][indx] == "RFQPTQ" ):
                                elcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "RFQPTQ" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">RFQ</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVSC" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.9,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">C</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVMC" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.8,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">CA</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "CAVNUM" ):
                                elcolor='g'
                                ellabel = pg.TextItem(anchor=(0.8,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">CA</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUADRUPO" ):
                                elcolor='r'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUADRUPO" ):
                                    ellabel = pg.TextItem(anchor=(0.4,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUAFK" ):
                                elcolor='r'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUAFK" ):
                                    ellabel = pg.TextItem(anchor=(0.4,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "BUNCHER" ):
                                elcolor='g'
                                elbcolor='g'
#                                ellabel = pg.TextItem(anchor=(0.,0.), border='w', fill=(0,0,255))
                                ellabel = pg.TextItem(anchor=(0.5,0.8))
#                                ellabel.setHtml('<div style="text-align: center"><span style="color: #FFF;">Vmax=%0.1f mm/s @ %0.1f s</span></div>'%(np.abs(signemax),tmax))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">B</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "MHB" ):
                                elcolor='g'
                                elbcolor='g'
                                ellabel = pg.TextItem(anchor=(0.9,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">MHB</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "BMAGNET" ):
                                elcolor='y'
                                elbcolor='k'
                                if (myDataFrame["ELEMENT"][indx-1] != "BMAGNET" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">DI</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUAELEC" ):
                                elcolor='r'
                                elbcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUAELEC" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">Q</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "EDFLEC" ):
                                elcolor='y'
                                elbcolor='g'
                                if (myDataFrame["ELEMENT"][indx-1] != "EDFLEC" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">DI</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "SOLENO" ):
                                elcolor='c'
                                if (myDataFrame["ELEMENT"][indx-1] != "SOLENO" ):
                                    ellabel = pg.TextItem(anchor=(0.,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">S</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "SEXTUPO" ):
                                elcolor='m'
                                if (myDataFrame["ELEMENT"][indx-1] != "SEXTUPO" ):
                                    ellabel = pg.TextItem(anchor=(0.2,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">SX</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "QUADSXT" ):
                                elcolor='r'
#                                elbcolor='m'
                                if (myDataFrame["ELEMENT"][indx-1] != "QUADSXT" ):
                                    ellabel = pg.TextItem(anchor=(0.3,0.8))
                                    ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">QS</span></div>')
                                    ellabel.setPos(myDataFrame["l(m)"][indx-1], eoffset+eheight)
                                    p2.addItem(ellabel)
                            elif (myDataFrame["ELEMENT"][indx] == "FSOLE" ):
                                elcolor='c'
                                ellabel = pg.TextItem(anchor=(0.,0.8))
                                ellabel.setHtml('<div style="text-align: left"><span style="color: #000000;">S</span></div>')
                                ellabel.setPos(myDataFrame["l(m)"][indx], eoffset+eheight)
                                p2.addItem(ellabel)
                            else:
                                elcolor='w'
                                elbcolor='k'
                            qitem = pg.PlotDataItem(myrect, fillLevel=True, pen=pg.mkPen(elbcolor, width=2), brush = elcolor)
                            p2.addItem(qitem)
                        indx = indx + 1
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return

######################################################
    def plot_l_envelopes(self):                      #
        '''plot longitudinal envelopes'''            #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
#    pfname = ifpath + os.sep + "dynac.print"
        pfname = ifpath + "dynac.print"
#        print("Using data from: ",pfname)

        if pfname:
            try:
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # read the remainder of the data
                myDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win4 = pg.GraphicsWindow(title=mytitle)
                self.win4.resize(1000,700)
                stitle = "No plots selected"
                if (self.checkBox4.isChecked() != 0 ):   
                    stitle = "RMS beam size"
                if (self.checkBox5.isChecked() != 0 ):   
                    stitle = "Beam extent"
                if (self.checkBox4.isChecked() != 0 ) and (self.checkBox5.isChecked() != 0 ):            
                    stitle = "RMS beam size and beam extent"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win4.addLabel(stitle, row=0, col=0)
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = self.win4.addPlot(title="Energy spread", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(myDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                if (self.checkBox4.isChecked() != 0 ):   
                    p1.plot(myDataFrame["l(m)"], myDataFrame["dW(MeV)"], pen='r', name="<font>dW<SUB>rms</SUB></font>")
                if (self.checkBox5.isChecked() != 0 ):   
                    p1.plot(myDataFrame["l(m)"], myDataFrame["Wmax(MeV)"], pen="#000000", name="<font>dW<SUB>ext</SUB></font>")
                    p1.plot(myDataFrame["l(m)"], myDataFrame["Wmin(MeV)"], pen="#000000")
                p1.setLabel('left', 'dW (MeV)')
                p1.setLabel('bottom', 'z (m)')
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win4.addPlot(title="Phase spread", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
                p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                if (self.checkBox4.isChecked() != 0 ): 
                    mylab =  'd\N{GREEK SMALL LETTER PHI}' + "<font><SUB>rms</SUB></font>" 
                    p2.plot(myDataFrame["l(m)"], myDataFrame["z(deg)"], pen='b', name=mylab)
                if (self.checkBox5.isChecked() != 0 ):   
                    mylab =  'd\N{GREEK SMALL LETTER PHI}' + "<font><SUB>ext</SUB></font>" 
                    p2.plot(myDataFrame["l(m)"], myDataFrame["phmax(deg)"], pen="#000000", name=mylab)
                    p2.plot(myDataFrame["l(m)"], myDataFrame["phmin(deg)"], pen="#000000")
                p2.setLabel('left', 'd\N{GREEK SMALL LETTER PHI} (deg)')
                p2.setLabel('bottom', 'z (m)')
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return
            
######################################################
    def plot_dispersion(self):                       #
        '''plot dispersion'''                        #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
        pfname = ifpath + "dynac.print"
#        print("Using data from: ",pfname)

        if pfname:
            try:
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # read the remainder of the data
                myDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win5 = pg.GraphicsWindow(title=mytitle)
                self.win5.resize(1000,700)
                stitle = "Dispersion as a function of position"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win5.addLabel(stitle, row=0, col=0)
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p1 = self.win5.addPlot(title="H dispersion", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(myDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                p1.plot(myDataFrame["l(m)"], myDataFrame["Dx(m)"], pen='r', name='Dx')
                p1.setLabel('left', 'Dx (m)')
                p1.setLabel('bottom', 'z (m)')
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win5.addPlot(title="V dispersion", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
                p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                p2.plot(myDataFrame["l(m)"], myDataFrame["Dy(m)"], pen='b', name='Dy')
                p2.setLabel('left', 'Dy (m)')
                p2.setLabel('bottom', 'z (m)')
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return

######################################################
    def plot_transmission(self):                       #
        '''plot transmission'''                        #
######################################################
        if (ifpath == ""):
#            self.inpLog.insertPlainText("\n")                
#            self.inpLog.insertPlainText("Path to file missing; select input file \n")
#            self.inpLog.insertPlainText("\n")                
#            self.cursor.setPosition(1,0)        
#            self.inpLog.setTextCursor(self.cursor)                    
            self.get_inp()
        pfname = ifpath + "dynac.print"
#        print("Using data from: ",pfname)

        if pfname:
            try:
                # print("Plotting " + pfname)
                mytime = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                mytitle = "DYNAC " + mytime + "      " + pfname
                # read the first line
                with open(pfname,'r') as myf:
                    first_row = myf.readline()
                    second_row = myf.readline()
                    second_row_args = second_row.split()
                    nopatinput = int(second_row_args[10])
                my_args = first_row.split()
                num_args = len(first_row.split())
                #print(num_args ,"arguments: ",my_args[0],my_args[1],my_args[2],my_args[3],my_args[4])
                #print(num_args ,"arguments read ")
                # read the remainder of the data
                myDataFrame = pd.read_csv(pfname, skiprows=1, sep='\s+', header=None, names=["ELEMENT", "l(m)", "x(mm)", "y(mm)", "z(deg)", "z(mm)", "Ex,n,RMS(mm.mrd)", "Ey,n,RMS(mm.mrd)", "Ez,RMS(keV.ns)", "Wcog(MeV)", "n_of_particles", "xmin(mm)", "xmax(mm)", "ymin(mm)", "ymax(mm)", "tmin(s)", "tmax(s)", "phmin(deg)", "phmax(deg)", "Wmin(MeV)", "Wmax(MeV)", "Dx(m)", "Dy(m)", "dW(MeV)", "Wref(MeV)", "Tref(s)", "Tcog(s)", "xbar(mm)", "ybar(mm)"])
                # set up white background
                pg.setConfigOption('background', 'w')
                pg.setConfigOption('foreground', 'k')
                self.win6 = pg.GraphicsWindow(title=mytitle)
                self.win6.resize(1000,700)
                stitle = "Centroids and transmission as a function of position"
#            self.win.setWindowTitle('plotWidget title') <- use this to update the window title
                self.win6.addLabel(stitle, row=0, col=0)
                pg.setConfigOptions(antialias=True)
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
#                p1 = self.win6.addPlot(title="Transmission", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1 = self.win6.addPlot(title="Transverse centroids", row=1, col=0, axisItems=({'right': rax,'top': tax}))
                p1.showAxis('right')
                p1.showAxis('top')
                p1.addLegend(offset=(10, 10))
                ezmax=math.ceil(np.nanmax(myDataFrame["l(m)"].values))
                p1.setXRange(0.,ezmax,padding=0)
                mylab = '<font><span style="text-decoration: overline">X</span></font>'
#                p1.plot(myDataFrame["l(m)"], myDataFrame["xbar(mm)"], pen='r', name='x\u0304')
                p1.plot(myDataFrame["l(m)"], myDataFrame["xbar(mm)"], pen='r', name=mylab)
                mylab = '<font><span style="text-decoration: overline">Y</span></font>'
                p1.plot(myDataFrame["l(m)"], myDataFrame["ybar(mm)"], pen='b', name=mylab)
                p1.setLabel('left', 'Position (mm)')
                p1.setLabel('bottom', 'z (m)')
                # lower plot
                rax=pg.AxisItem('right', pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                tax=pg.AxisItem('top',   pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=False)                
                p2 = self.win6.addPlot(title="Transmission", row=2, col=0, axisItems=({'right': rax,'top': tax}))
                p2.showAxis('right')
                p2.showAxis('top')
#                p2.addLegend(offset=(10, 10))
                p2.setXRange(0.,ezmax,padding=0)
                p2.plot(myDataFrame["l(m)"], 100*myDataFrame["n_of_particles"]/nopatinput, pen='r', name='')
                p2.setLabel('left', 'Transmission (%)')
                p2.setLabel('bottom', 'z (m)')
            except:
                msg3 = QMessageBox()
                msg3.setIcon(QMessageBox.Critical)
                msg3.setText("Failed to read file\n'%s'" % pfname)
#                msg3.setInformativeText(e)
                msg3.setWindowTitle("Error Message")                                 
            return

######################################################
    def plotit(self):                                #
        '''plotit'''                                 #
######################################################
        self.PlotBtn1.setStyleSheet("color : #ff0000; ")        
        #print("System=",platform.system())
        if (platform.system() == 'Windows') :
            ndynpath= dynpath[:-5] + os.sep
            doplotit = '"' + ndynpath + "plot" + os.sep + "dynplt" + '"'
            plotitopt = "w"
#            doplotit = os.path.abspath(doplotit)
        if (platform.system() == 'Linux') :
            doplotit = dynpath[0:-4] + os.sep + "plot" + os.sep + "dynplt"
            plotitopt = "l"
            doplotit = '"' + os.path.abspath(doplotit) + '"'                 
        if (platform.system() == 'Darwin') :
            doplotit = dynpath[0:-4] + os.sep + "plot" + os.sep + "dynplt"
            plotitopt = "m"
            doplotit = os.path.abspath(doplotit)                    
            doplotit = '"' + os.path.abspath(doplotit) + '"'                 
        if (ifpath == ""):
            self.get_inp()
        pathop= "-p" 
        pathop= pathop + '"' + ifpath + '"'
        dgo = "-dgui"        
        cmd = doplotit + " " + plotitopt + " " + dgo + " " + pathop
#        print("Run plotit using ",cmd)
        mystr="Run plotit using " + cmd
        if (self.checkBox3.isChecked() != 0 ):   
            self.inpLog.clear()            # Clear text in the log frame before running again
        self.inpLog.insertPlainText("\r\n")
        self.inpLog.insertPlainText(mystr)
        self.inpLog.insertPlainText("\n")                
        self.cursor.setPosition(0,0)        
        self.inpLog.setTextCursor(self.cursor)        
        self.plotitraw = QtCore.QProcess()
        if (self.checkBox3.isChecked() != 0 ):   
            self.inpLog.clear()            # Clear text in the log frame before running again
        self.plotitraw.readyReadStandardOutput.connect(self.procServer1)
        self.plotitraw.finished.connect(self.plotitraw_done)
        self.plotitraw.start(cmd)

######################################################
    def close_gnuplots(self):                        #
        '''Close gnuplot windows opened by plotit''' #
######################################################
        self.plotitclose = QtCore.QProcess()
        if (platform.system() == 'Windows') :
            cmd = "Taskkill /IM gnuplot_qt.exe /F"
        if (platform.system() == 'Linux') :
            self.getuser()
            cmd = "killall -u " + cuser + " gnuplot_x11"
        if (platform.system() == 'Darwin') :
            self.getuser()
            cmd = "killall -u " + cuser + " gnuplot_x11"
#        print("Run close gnuplots using ",cmd)
        self.plotitclose.start(cmd)

######################################################
    def run_dyn(self):                               #
        '''Run DYNAC'''                              #
######################################################
        global dorun,dynopt,ifname
        self.RightBtn2.setStyleSheet("color : #ff0000; ")        
        if (platform.system() == 'Windows') :
            dorun=dynpath[:-1] + os.sep + dynacv
            dorun='"' + dorun + '"'
            newifpath='"' + ifpath + '"'
            dynopt="-p" + newifpath
        else:    
            dorun=dynpath + os.sep + dynacv
            dorun='"' + dorun + '"'
            newifpath='"' + ifpath + '"'
            dynopt="-p" + newifpath
        ifname=self.text_box2.toPlainText() 
        if(ifname == ""):
            self.get_inp()
            if (platform.system() == 'Windows') :
                lastsep=ifname.rfind(os.sep)
                newifpath='"' + ifname[0:lastsep+1] + '"'
                dynopt="-p" + newifpath
                cmd=dorun + " " + dynopt + " "
                cmd=cmd + '"' + ifname + '"'
            else:    
                newifpath='"' + ifpath + '"'
                dynopt="-p" + newifpath
                cmd=dorun + " " + dynopt + " " 
                cmd=cmd + '"' + ifname + '"'
        else:
            if (platform.system() == 'Windows') :
                cmd=dorun + " " + dynopt + " "
                cmd=cmd + '"' + ifname + '"'
            else:    
                cmd=dorun + " " + dynopt + " " 
                cmd=cmd + '"' + ifname + '"'
#        print("Run DYNAC using ",cmd)
        self.dynraw = QtCore.QProcess()
        if (self.checkBox3.isChecked() != 0 ):   
            self.inpLog.clear()            # Clear text in the log frame before running again
        self.firstTransport = True  
        self.dynraw.readyReadStandardOutput.connect(self.procServer2)
#        self.dynraw.readyReadStandardOutput.connect(partial(self.procServer3, self.dynraw))
        self.dynraw.finished.connect(self.dynraw_done)
        self.dynraw.start(cmd)

######################################################
    def procServer3(self, other):                    #
######################################################
        global pos1
        self.inpLog.insertPlainText("\n")                
        income = self.dynraw.readAllStandardOutput().data()
        pincome = income.decode('utf-8','ignore').strip()
        pincome.replace("\r\n","")
        if "Transport" in pincome:  
            if self.firstTransport:
                self.firstTransport = False
                self.pos1=self.cursor.position()        
#                print("B4   2=",self.pos1)
                self.inpLog.insertPlainText(pincome)
            else:
#                print("B4   3=",self.pos1)
                self.cursor.setPosition(self.pos1, 1)        
                self.inpLog.setTextCursor(self.cursor)        
                self.inpLog.insertPlainText(pincome)
        else:
#            self.inpLog.insertPlainText("\r\n")
            self.inpLog.insertPlainText(pincome)


######################################################
    def procServer2(self):                           #
######################################################
        global pos1
        self.inpLog.insertPlainText("\n")                
        income = self.dynraw.readAllStandardOutput().data()
        pincome = income.decode('utf-8','ignore').strip()
        pincome.replace("\r\n","")
        if "Transport" in pincome:  
            if self.firstTransport:
                self.firstTransport = False
                self.pos1=self.cursor.position()        
#                print("B4   2=",self.pos1)
                self.inpLog.insertPlainText(pincome)
            else:
#                print("B4   3=",self.pos1)
                self.cursor.setPosition(self.pos1, 1)        
                self.inpLog.setTextCursor(self.cursor)        
                self.inpLog.insertPlainText(pincome)
        else:
#            self.inpLog.insertPlainText("\r\n")
            self.inpLog.insertPlainText(pincome)


######################################################
    def procServer1(self):                           #
######################################################
        self.inpLog.insertPlainText("\n")                
        income = self.plotitraw.readAllStandardOutput().data()
        pincome = income.decode('utf-8','ignore').strip()
        self.inpLog.insertPlainText(pincome+"\n")


######################################################
    def getuser(self):                               #
######################################################
        global cuser
#        print("In GetUser ", platform.system())
        if (platform.system() != 'Windows') :
            cuser=subprocess.getoutput(['whoami'])
#        print("User=",cuser)


######################################################
    def dynraw_done(self):                           #
######################################################
        #dynac execution done; change button color back to blue    
        self.RightBtn2.setStyleSheet("color : #0000ff; ") 
        self.inpLog.insertPlainText("\n")                
        self.cursor.setPosition(0,0)        
        self.inpLog.setTextCursor(self.cursor)        

######################################################
    def plotitraw_done(self):                        #
######################################################
        #plotit execution done; change button color back to blue    
        self.PlotBtn1.setStyleSheet("color : #0000ff; ") 
        self.inpLog.insertPlainText("\n")                
        self.cursor.setPosition(0,0)        
        self.inpLog.setTextCursor(self.cursor)        


    def get_r1(self):
        dummy=0 
#        print('R1 selected')

    def get_r2(self):
        dummy=0 
#        print('R2 Selected')
        
    def get_cb1(self):
        dummy=0 
#        print('CB1 selected')

    def get_cb2(self):
        dummy=0 
#        print('CB2 Selected')
        
    def get_cb3(self):
        if (self.checkBox3.isChecked() != 0 ):   
            dummy=0 
#            print('CB3 Selected')
        else:    
            dummy=0 
#            print('CB3 Not Selected')

    def get_cb4(self):
        dummy=0 
#        print('CB4 Selected')
        
######################################################
    def get_dynpath(self):                           #
        '''Get DYNAC path'''  
#   !!!  this function currently not in use  !!!     #
######################################################
        global dynpath, default_dfpath, default_ugpath
        if (platform.system() == 'Windows') :
            mylist=subprocess.run(['cmd','/c','cd'], stdout=subprocess.PIPE)
            dynpath=mylist.stdout.decode('utf-8')
            # remove crt
            dynpath=dynpath[:-6] + "bin"
            default_dfpath=dynpath[:-3] + "datafiles"
            default_ugpath=dynpath[:-3] + "help"
        else:
            dynpath=subprocess.getoutput(['pwd'])
            dynpath=dynpath[:-4] + "bin"
            default_dfpath=dynpath[:-3] + "datafiles"
            default_ugpath=dynpath[:-3] + "help"
        myplatform=platform.system()
        systembin="Running on " + platform.system() + " with DYNAC binary in " + dynpath
        return systembin


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
# next shows icon in tray at top of MAC, bottom if linux or windows (if tray at bottom)
    try:
        trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(dynpath  + os.sep + 'dynicon.png'), app)
    except:
        if (platform.system() == 'Linux') :
            trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(dynpath  + os.sep + 'dynicon.png'), app)
    trayIcon.setToolTip('DGUI')
    trayIcon.show()
# next shows icon in dock at bottom of MAC    
    app.setWindowIcon(QtGui.QIcon(dynpath  + os.sep + 'dynicon.png'))
#    app.setToolTip('DGUI')
#    app.setWindowIconText('DGUI')
    # creating main window
    mw = MainWindow()
    mw.move(10, 20)
    mw.show()
    sys.exit(app.exec_())
    
   
    
    
