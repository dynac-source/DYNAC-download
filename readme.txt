DYNAC V7 (WINDOWS and LINUX/MAC versions)                         15-Aug-2024

Software License Agreement

NOTICE TO USERS: 
This End User License Agreement (the "Agreement") is a legally binding 
agreement between you (either an individual or an entity, the "User"), and the 
DYNAC development team (currently Saby Valero and Eugene Tanke) regarding 
a) the DYNAC software (the "Software" or the "Program", which includes scripts 
and the Graphical User Interface (GUI) software), and 
b) all successor upgrades, revisions, patches, fixes, modifications, copies, 
additions or maintenance releases of the Software, if any, licensed to you by 
the DYNAC development team (collectively, the "Updates"), and 
c) related user documentation and explanatory materials or files provided in 
written, "online" or electronic form (the "Documentation" and together with the 
Software and Updates, the "PRODUCT" or the "Distribution Package"). 

CAREFULLY READ THE FOLLOWING LEGAL AGREEMENT. USE OF THE PRODUCT PROVIDED WITH
THIS AGREEMENT CONSTITUTES YOUR ACCEPTANCE OF THESE TERMS. IF YOU DO NOT AGREE
TO THE TERMS OF THIS AGREEMENT, DO NOT INSTALL AND/OR USE THE PRODUCT. YOUR 
USE OF THE PRODUCT IS CONDITIONED UPON COMPLIANCE WITH THE TERMS OF THIS 
AGREEMENT.

1. Intellectual property rights  

The DYNAC Program and associated software ("PRODUCT") is owned by the DYNAC 
development team. Your possession, installation or use of the PRODUCT does
not transfer to you any title to the intellectual property in the PRODUCT, and
you will not acquire any rights in the PRODUCT except as expressly set forth 
in this Agreement. 

The DYNAC Program and associated software is freeware and as such the authors
cannot be held accountable for any problems and or costs arising from its
usage. As freeware, DYNAC and associated software may be used for commercial 
goals, with the exception of commercializing DYNAC PRODUCT, parts of the DYNAC
Program and/or associated software itself.

2. Scope of the License 

You are granted a non-exclusive license to use the PRODUCT as set forth 
herein. You can use the PRODUCT as set forth in the Agreement for 
non-commercial purposes in non-business, non-commercial environment. As 
freeware, DYNAC and associated software may be used for commercial goals, with
the exception of commercializing DYNAC, parts of DYNAC and/or associated 
software itself. 

The Software may be freely distributed, but no person or company may charge a
fee for the distribution of the PRODUCT without written permission from the 
DYNAC development team. 

3. Limited warranties 

The DYNAC development team DOES NOT WARRANT THAT THE SOFTWARE IS FIT FOR ANY 
PARTICULAR PURPOSE. The DYNAC development team DISCLAIMS ALL OTHER WARRANTIES
WITH RESPECT TO THE SOFTWARE, EITHER EXPRESS OR IMPLIED. SOME JURISDICTIONS 
DO NOT ALLOW THE EXCLUSION OF IMPLIED WARRANTIES OR LIMITATIONS ON HOW LONG 
AN IMPLIED WARRANTY MAY LAST, SO THE ABOVE LIMITATIONS OR EXCLUSIONS MAY NOT 
APPLY TO YOU. 

4. Legality statement

The program that is licensed to you is absolutely legal and you can use it 
provided that you are the legal owner of all files or data you are going to
use with our software or have permission from the legitimate owner to perform
these acts. Any illegal use of our software will be solely your 
responsibility. Accordingly, you affirm that you have the legal right to 
access all data, information and files. 

You further attest that the data and/or files will not be used for any illegal
purpose. 
 
5. Final provisions 

All rights not expressly granted here are reserved by the DYNAC development
team. 


GETTING STARTED:
Make sure to have gfortran and gnuplot installed and operable on your operating
system. See also below. 



MAC SPECIFIC: 
For the MAC, it is suggested to install gnuplot with the wxt, qt and x11 terminals
(this can for instance be done with macports, but apparently no longer with home-brew), as it is 
considerably faster than the aqua terminal.
It is also advised to install quartz (gnu plot can interact with this for the X11 terminal). This
is also needed if one uses DGUI (DYNAC gui).

LINUX SPECIFIC:
On LINUX (Ubuntu, Mint), one can install gfortran by opening a terminal window and typing
sudo apt install gfortran
You will also need cc1plus, which you can install with
sudo apt-get install --reinstall build-essential  
For linux, it is suggested to install gnuplot with the wxt, qt and x11 terminals. 

WINDOWS SPECIFIC:
For 64 bit Windows versions, the SEH version from the following link has been successfully used in the past:
https://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win64/Personal%20Builds/mingw-builds/8.1.0/threads-win32/
Make sure to choose the correct architure (X86_64) and win32 threads. Once
installed, open an MS-DOS window and execute the following 2 commands 
(this assumes you used the above mentioned link to install that particular version of mingw/gfortran):
set PATH=%PATH%;C:\Program Files\mingw-w64\x86_64-8.1.0-win32-seh-rt_v6-rev0\mingw64\bin
setx PATH "%PATH%;C:\Program Files\mingw-w64\x86_64-8.1.0-win32-seh-rt_v6-rev0\mingw64\bin"
Make sure you are pointing to the right path and revision!

Verify with the following command that gfortran is now a recognized command:
gfortran -v
Once gnuplot installed, open an MS-DOS window and execute the following 2 
commands:
set PATH=%PATH%;C:\Program Files (x86)\gnuplot\bin
setx PATH "%PATH%;C:\Program Files (x86)\gnuplot\bin"
Of course, change this path if you installed gnuplot elsewhere. 

Now download the complete DYNAC package. For Windows, you may want to
unzip it in the top level of the C:\ directory or the top level D:\ one.
After downloading and unzipping the complete DYNAC package, you should 
have the following directories in the current (dynac) directory:
bin  datafiles  help  plot  source

For Windows, now open an MS-DOS window and execute the following two 
commands (modify the path drive and DYNAC version as needed):
set PATH=%PATH%;C:\dynacv7_w\bin
setx PATH "%PATH%;C:\dynacv7_w\bin"
With this the PATH variable will point to the location of the DYNAC
executable.

Under linux/MAC you can set an alias in the shell script (e.g. .bashrc
or .cshrc in your top directory) to point to the executable or better
(and preferred) you can add the dynac/bin directory to the $PATH variable
in the shell script (e.g. .bashrc or .cshrc in your top directory)

In order to create a DYNAC executable, go to the source directory and
type comv7 in the case of WINDOWS.
On linux/MAC you may have to render comv7 executable by typing
chmod u+x comv7
and then for linux/MAC type:
./comv7
It is assumed here that you have already installed the gfortran compiler 
and set the path for it.
On linux/MAC you may have to render comv7 executable by typing
chmod u+x comv7
One only needs to do this once.

If you have updated your MAC to Catalina, you encounter an error message, 
stating that -lstdc++ library cannot be found. You may need to type the 
following command on the terminal first:
xcode-select --install
so that this missing library becomes available. You can the compile with
./comv7 

If you are using the 32 bit version of the gfortran compiler, you will
need to add -ffloat-store as compiler flag in the comv7 script.
To test if the DYNAC executable works on a linux, MAC or Windows terminal, 
type:
dynacv7 -h
after which the dynac version, revision and version date should appear in
the terminal window, as well as the DYNAC command format. If it does not,
you may not have compiled the source (see above) or may not have set up the
path or alias that allows to link directly to the DYNAC source (see above).

In order to create an executable for the plotting post-processor, which
is based on GNU plot, go to the plot directory and for windows type 
complt
On linux/MAC you may have to render comv7 executable first by typing
chmod u+x compltFor linux/mac, type
./complt
Then go to the datafiles directory.

You are now ready to run DYNAC. An example file is given for 2
different types of accelerators:
sns_mebt_dtl1.in     -> THE MEBT and first DTL tank for the SNS
egun_example2.in     -> Electron gun (you will also need egun_field.txt)

Run it on linux/MAC/Windows by typing:
dynacv7 sns_mebt_dtl1.in
or
dynacv7 egun_example2.in

From here we can in principle look at the plots generated by DYNAC, in
using "plotit", which is a script located in the dynac/bin directory.
It points to the dyndat executable located in dynac/bin

You may view the plots by typing " plotit ". There is a minor problem
with plotit for the WINDOWS version: the first time you use it it may
complain about not finding 3 files. Ignore this message. Details on
"plotit" may be found in chapter 7 of the DYNAC User Guide.

Users can change the default gnuplot terminal by changing plotit using the 
-tt option. For this, open the plot it script in dynamic/bin and append
the -tt option, e.g.
~/your_path/dynac/plot/dynplt m -ttxxxx
where xxxx is the gnuplot terminal name. On MAC, if not specified, aqua will 
be used. But aqua yields a very slow response in gnuplot for scatter plots, 
whereas wxt is much faster.

If you already have an older version of DYNAC installed, you may wish
to download only the relevant files upon an update. These are typically 
the source code, the plotting program dyndat.f90 and the user guide. They can
be found under the "Individual files" heading. Starting from dynacv7, one also
needs to copy cgof.cc to the source directory.

Input files contain a sequence of keywords or type code entries. For user 
instructions for these, please refer to the DYNAC User Guide in the help 
directory.

Please feel free to send any suggestions, corrections, comments, modifications
or new routines to Eugene Tanke (dynacatgithub@gmail.com).
