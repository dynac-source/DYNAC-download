# DYNAC V7R2-download (3-Jan-2024 page under construction, links will not necessairly point to V7R2 yet. Will happen within the next few weeks)
**DYNAC DOWNLOAD PAGE for DYNAC V7R2, a Multiparticle Beam Simulation Code for linacs and beam transport lines.**  
LINUX, MAC and WINDOWS downloads for the simulation code DYNAC V7R2 can be found on this page. Instructions for installation after downloading are in the file: [readme.txt](https://github.com/dynac-source/DYNAC-download/files/6633754/readme.txt). This file is also contained in the full package below.

**MODIFICATIONS PERTAINING TO DYNAC V7R2 (6-Jan-2024)**  
Please see the [change log](https://github.com/dynac-source/DYNAC-download/files/6633795/modV7R1.txt) for a full list of changes with respect to V7R1.  
DYNAC V7R2 has some minor additions, modifications and corrections compared to the previous revision.


**REQUIRED SOFTWARE FOR DYNAC**  
DYNAC needs to be compiled with gfortran, which is available from the [gfortran web site](http://gcc.gnu.org/wiki/GFortranBinaries). DYNAC has been successfully tested with gfortran/gcc 9.2.0 and older.
GNU Plot (ZIP format) for WINDOWS can be obtained from the [gnuplot web site](http://sourceforge.net/projects/gnuplot/).
Using the same link you can find a GNU Plot download for the MAC (download not always required for LINUX, as gnuplot is standard with some flavors of LINUX). On the MAC, it is suggested to install gnuplot with the wxt terminal (e.g. brew install gnuplot --with-wxmac --with-cairo), as it is considerably faster than the aqua terminal.

DYNAC has been succesfully tested on LINUX (Mint 20.2 and older, Red Hat 4.4.7-17), MAC (Catalina, Mojave and some older) and WINDOWS (11 and older).

**OPEN ISSUES (3-Jan-2024)**  
The charge stripper model requires further development (e.g. energy loss model).

**DYNAC V7R2 (FULL PACKAGE)**  
DYNAC source, data, plot and help files (for WINDOWS, ZIP format) [dynacv7r1_w.zip](https://github.com/dynac-source/DYNAC-download/files/7769406/dynacv7r1_w.zip)  
DYNAC source, data, plot and help files (for LINUX/MAC, tar/gz format) [dynacv7r1.tar.gz](https://github.com/dynac-source/DYNAC-download/files/7769411/dynacv7r1.tar.gz)  

*Note: To unzip the linux/mac version, type: tar xvfz dynacv7r1.tar.g*z  

**DYNAC V7R2 (INDIVIDUAL FILES)**  
DYNAC User Guide (PDF format) [dynac_UG.pdf](https://github.com/dynac-source/DYNAC-download/files/6633231/dynac_UG.pdf)  
DYNAC input file (example) for an electron gun (text format) [egun_example2.in](https://github.com/dynac-source/DYNAC-download/blob/main/egun_example2.in)  
DYNAC input file (example) for describing the field in an electron gun (text format; to be used with the egun example above) [egun_field.txt](https://github.com/dynac-source/DYNAC-download/files/6633699/egun_field.txt)  
DYNAC input file for the SNS H- MEBT (Medium Energy Beam Transport) line and DTL Tank 1 (text format) [sns_mebt_dtl1.in](https://github.com/dynac-source/DYNAC-download/blob/main/sns_mebt_dtl1.in)  
DYNAC source (for WINDOWS, ZIP format) [dynacv7r1_w_source.zip](https://github.com/dynac-source/DYNAC-download/files/6633779/dynacv7r1_w_source.zip)    
Script to compile the DYNAC source (for WINDOWS, .bat file) [comv7.bat](https://github.com/dynac-source/DYNAC-download/blob/main/comv7.bat)  
DYNAC source file (for LINUX and MAC, tar/gz format) [dynacv7r1_source.tar.gz](https://github.com/dynac-source/DYNAC-download/files/7769414/dynacv7r1_source.tar.gz)  
Script to compile the DYNAC source (for LINUX and MAC, text format) [comv7](https://github.com/dynac-source/DYNAC-download/blob/main/comv7)  


[dyndat.f90](https://github.com/dynac-source/DYNAC-download/blob/main/dyndat.f90) (source file (V3.1) in text format) is used for GNUPLOT based plots.  
Script to compile the dyndat source (for WINDOWS, .bat file) [complt.bat](https://github.com/dynac-source/DYNAC-download/blob/main/complt.bat)  
Script to compile the dyndat source (for LINUX and MAC, text format) [complt](https://github.com/dynac-source/DYNAC-download/blob/main/complt)  

*Note: To unzip the linux/mac version of the source, type: tar xvfz dynacv7r1_source.tar.gz*

**OTHER DYNAC UTILITIES**  
[DGUI](https://github.com/dynac-source/DYNAC-download/blob/main/README.md#dgui-v2r2-download), a DYNAC Graphical User Interface.  
[ptq2dyn.f](https://github.com/dynac-source/DYNAC-download/blob/main/ptq2dyn.f) : prepares the input data file used by the RFQPTQ card. Source file in text format, compile with:  
*gfortran ptq2dyn.f -o ptq2dyn*  
An alternative to the above mentioned DYNAC GUI has been developed at [MSU](https://github.com/NSCLAlt/DynacGUI).

# DGUI V2R3-download
**DGUI, a DYNAC Graphical User Interface**  
DGUI V2R3 is a Python3 based GUI to DYNAC. Alternatively, the DYNAC code can be exectued from the terminal.  
DGUI V2R3 has been tested on LINUX (Mint 20 and older), MAC (Catalina and Mojave) and WINDOWS (11, 10 and 7) and requires DYNAC V6R19 or newer and python3.8 or newer.
Instructions for installation after downloading are in the [DGUI User Guide](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_UG.pdf).  
Modifications pertaining to DGUI V2R3 (6-Jan-2024): [dgui_modV2R2.txt](https://github.com/dynac-source/DYNAC-download/files/7769687/dgui_modV2R2.txt)  

Please refer to the DGUI User Guide for download and installation instructions.  
DGUI source (.py) [dgui.py](https://github.com/dynac-source/DYNAC-download/blob/main/dgui.py)  
DGUI icon (.png) to be stored in directory dynac/bin [dynicon.png](https://github.com/dynac-source/DYNAC-download/blob/main/dynicon.png)  
DGUI example .ini file for linux and MAC [dgui_example_linmac.ini](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_example_linmac.ini)  
DGUI example .ini file for  Windows [dgui_example_windows.ini](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_example_windows.ini)  
DGUI User Guide (pdf format) [DGUI User Guide](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_UG.pdf)  

*Note: The example .ini file needs to be renamed to dgui.ini (see User Guide)*  

**CONTACT**  
Eugene Tanke 
Email: dynacatgithub at gmail.com  

Updated 3-Jan-2024
  
  


