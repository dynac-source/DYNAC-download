# DYNAC V8R0-download 

**DYNAC DOWNLOAD PAGE for DYNAC V8R0, a Multiparticle Beam Simulation Code for linacs and beam transport lines.**  
LINUX, MAC and WINDOWS downloads for the simulation code DYNAC V8R0 can be found on this page. Instructions for installation after downloading are in the file: [readme.txt](https://github.com/dynac-source/DYNAC-download/blob/main/readme.txt). This file is also contained in the full package below.

**MODIFICATIONS PERTAINING TO DYNAC V8R0 (16-Dec-2025)**  
Please see the [change log](https://github.com/dynac-source/DYNAC-download/blob/main/modV8R0.txt) for a full list of changes with respect to V7R5.  
DYNAC V8R0 has some minor additions and modifications compared to the previous version/revision (V7R5) in terms of functionality, but has significant changes in the way the program is structured in view of bringing it closer to modern Fortran standards.


**REQUIRED SOFTWARE FOR DYNAC**  
DYNAC needs to be compiled with gfortran, which is available from the [gfortran web site](http://gcc.gnu.org/wiki/GFortranBinaries). DYNAC has been successfully tested with gfortran/gcc 15.1.0 and older.
GNU Plot (ZIP format) for WINDOWS can be obtained from the [gnuplot web site](http://sourceforge.net/projects/gnuplot/).
Using the same link you can find a GNU Plot download for the MAC (download not always required for LINUX, as gnuplot is standard with some flavors of LINUX). On the MAC, it is suggested to install gnuplot with the wxt terminal (e.g. brew install gnuplot --with-wxmac --with-cairo), as it is considerably faster than the aqua terminal and the xquartz/X11 terminal (as it is used by DGUI). 

DYNAC has been succesfully tested on LINUX (Mint 22.2 and older, Red Hat 4.4.7-17 and some older, Kali 2025.3 and Ubuntu 24), MAC (Sequoia, Catalina, Mojave and older) and WINDOWS (11 and older).

**OPEN ISSUES (16-Dec-2025)**  
The charge stripper model requires further development (e.g. energy loss model).

**DYNAC V8R0 (FULL PACKAGE)**  
DYNAC source, data, plot and help files (for WINDOWS, ZIP format) [dynacv8r0_w.zip](https://github.com/dynac-source/DYNAC-download/blob/main/dynacv8r0_w.zip)  
DYNAC source, data, plot and help files (for LINUX/MAC, tar/gz format) [dynacv8r0.tar.gz](https://github.com/dynac-source/DYNAC-download/blob/main/dynacv8r0.tar.gz)  

*Note: To unzip the linux/mac version, type: tar xvfz dynacv8r0.tar.gz*   

**DYNAC V8R0 (INDIVIDUAL FILES)**  
DYNAC User Guide (PDF format) [dynac_UG.pdf](https://github.com/dynac-source/DYNAC-download/blob/main/dynac_UG.pdf)  
DYNAC input file (example) for an electron gun (text format) [egun_example2.in](https://github.com/dynac-source/DYNAC-download/blob/main/egun_example2.in)  
DYNAC input file (example) for describing the field in an electron gun (text format; to be used with the egun example above) [egun_field.txt](https://github.com/dynac-source/DYNAC-download/files/6633699/egun_field.txt)  
DYNAC input file for the SNS H- MEBT (Medium Energy Beam Transport) line and DTL Tank 1 (text format) [sns_mebt_dtl1.in](https://github.com/dynac-source/DYNAC-download/blob/main/sns_mebt_dtl1.in)  
DYNAC source (for WINDOWS, ZIP format) [dynacv8r0_w_source.zip](https://github.com/dynac-source/DYNAC-download/blob/main/dynacv8r0_w_source.zip)  
Script to compile the DYNAC source (for WINDOWS, .bat file) [comv8.bat](https://github.com/dynac-source/DYNAC-download/blob/main/comv8.bat)  
DYNAC source file (for LINUX and MAC, tar/gz format) [dynacv8r0_source.tar.gz](https://github.com/dynac-source/DYNAC-download/blob/main/dynacv8r0_source.tar.gz)  
Script to compile the DYNAC source (for LINUX and MAC, text format) [comv8](https://github.com/dynac-source/DYNAC-download/blob/main/comv8)  


[dynplt.f08](https://github.com/dynac-source/DYNAC-download/blob/main/dynplt.f08) (source file (V4R0) in text format) is used for GNUPLOT based plots.  
Script to compile the dynplt source (for WINDOWS, .bat file) [complt.bat](https://github.com/dynac-source/DYNAC-download/blob/main/complt.bat)  
Script to compile the dynplt source (for LINUX and MAC, text format) [complt](https://github.com/dynac-source/DYNAC-download/blob/main/complt)  

*Note: To unzip the linux/mac version of the source, type: tar xvfz dynacv8r0_source.tar.gz*

**OTHER DYNAC UTILITIES**  
[DGUI](https://github.com/dynac-source/DYNAC-download/blob/main/README.md#dgui-v3r0-download), a DYNAC Graphical User Interface.  
[ptq2dyn.f](https://github.com/dynac-source/DYNAC-download/blob/main/ptq2dyn.f) : prepares the input data file used by the RFQPTQ card. Source file in text format, compile with:  
*gfortran ptq2dyn.f -o ptq2dyn*  
An alternative to the above mentioned DYNAC GUI has been developed at [MSU](https://github.com/NSCLAlt/DynacGUI).


# DGUI V3R0-download
**DGUI, a DYNAC Graphical User Interface**  

DGUI V3R0 is a Python3 based GUI to DYNAC. Alternatively, the DYNAC code can be exectued from the terminal.  
DGUI has been tested on LINUX (Mint 22 and older, Ubuntu 24, Kali 2025.03), MAC (Sequoia, Catalina and Mojave) and WINDOWS (11, 10) and works best with DYNAC V8R0.
Instructions for installation after downloading are in the [DGUI User Guide](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_UG.pdf).    
Modifications and changes in DGUI V3R0 (16-Dec-2025) as compared to GUI V2R8 are listed in [dgui_modV3R0.txt](https://github.com/dynac-source/DYNAC-download/blob/main/dgui_modV3R0.txt). This file also contains the changes to previous versions.   

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

Updated 16-Dec-2025
  
  


