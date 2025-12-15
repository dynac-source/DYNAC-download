!> *******************************************************************
!! PROGRAM dynplt
!!
!! @version V4R0
!! @date 16-Dec-2025
!!
!! Modified and maintained by :
!! Eugene Tanke                     
!
!! V4R0  From DYNACV8 on, fortran file extensions are f08. Changed program name of source
!!       from dyndat to dynplt. Improved compatability with cygwin. Under Windows, call
!!       gnuplot in stead of wgnuplot. 10M particles set as upper limit. Allocation
!!       of memory added for this purpose.
!! V3R6  Replaced "call command" calls with newer "call EXECUTE_COMMAND_LINE" calls. For 
!!       profiles with logarithmic scale, changed format from F type to E type to allow
!!       for larger range. Changed from 1M to 2M macro-particles.
!! V3R5  Updated to be compatible with gnuplot v6.0, e.g. -noraise option no longer valid
!! V3R4  Fixed issue with vertical position of titles for some X11 plots 
!! V3R3  Align version/revision numbering scheme to the one of DYNAC. Charge states are now 
!!       printed with more significant digits.
!! V3.2  Added the possibility of saving to png, jpeg or gif files. This is achieved by setting
!!       the -tt option with any of these 3 gnuplot terminal types.
!! V3.1  Slightly larger windows for Windows OS. Changed to full path (as opposed to assuming
!!       local directory usage) for all 3 operating systems. As a consequence, when this
!!       version is started by dgui, it will write the gnuplot files to the directory that
!!       was selected in dgui. One can now save density plots.
!! V3.0  Source code changed from .f to .f90; updated deprecated gnuplot syntax. Use
!!       wxt as default terminal for all 3 operating systems.
!! V2.11 Added 2-D plots for xx'-yy'-xy-zz' an xz-yz.
!! V2.10 For QT terminal, line colors in gnuplot are platform dependent. Fixed this for
!!       xx'-yy'-xy-zz' an xz-yz plots
!! V2.9  Change maximum number of macro particles to 1000000. Add code that allows for
!!       interfacing with DGUI (-dg option).
!! V2.8  Also read plotfile path; this was introduced to be compatible with the DYNAC GUI
!!       Allow to read the terminal type for MAC
!! V2.7  Various changes related to changes in the names of certain GNUPLOT parameters; these
!!       changes in dyndat.f were needed to for instance avoid that the dots in the
!!       particle distributions would no longer be plotted.
!! V2.6  Change from 100k to 250k macro particles
!! V2.5  Allow for longer file names under the save option
!!       Made dyndat compatible with MINGW gfortran in view of different result for ctime
!!       function than standard gfortran
!!       Fixed bug related to MAC: on a MAC 02 Apr is shown as 2 Apr (on windows as
!!       02 Apr); fill the blank with the character '0' to avoid error message on file
!!       copy
!!       Fix color of points used in particle plots for MAC (changed from grey to black)
!! V2.4  Allow for non-integer charge states
!! V2.3  Mods to add MAC as a valid operating system for gnuplot
!! V2.2  Fixed compiler warnings related to array sizing of ctrx1,2,3 and ctry1,2,3
!! V2.3  Mods to add MAC as a valid operating system for gnuplot
!! V2.2  Fixed compiler warnings related to array sizing of ctrx1,2,3 and ctry1,2,3
!! V2.1  Replaced 'dots' with 'points' syntax
!! V2.0  Formatting changed to be compatible with gfortran and with WGNUPLOT gp440win32
!! V1.2  Original released version, compatible with g77
!!
!< *******************************************************************
MODULE DynacConstants
!---------------------------------------------------------------------
!  Module containing definitions needed by the wfile routines
!---------------------------------------------------------------------
!   use, intrinsic :: ISO_FORTRAN_ENV, only : real64
   INTEGER, PARAMETER :: iptsz=10000002
   REAL(8), PARAMETER :: PIO4=ATAN(1.D0)
   REAL(8), PARAMETER :: FPREC=epsilon(PIO4)
   logical cygwin
   character(len=2) :: backslash
   parameter (backslash="\\")   
END MODULE DynacConstants
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE m4wfiles
!---------------------------------------------------------------------
!  Module containing definitions needed by the wfile routines
!---------------------------------------------------------------------
!        common/wfil2/title,labels
   character(len=80) :: title
   character(len=40), dimension(20) :: labels   
!        common/wfil2l/uxmin,uxmax,uymin,uymax
   REAL(8) uxmin,uxmax,uymin,uymax
!        common/wfil20/xmin(10),xmax(10),ymin(10),ymax(10)
   REAL(8) xmin(10),xmax(10),ymin(10),ymax(10)
!        common/wfil120/xxpmax,yypmax,xymax,zzpmax,zxmax,zymax,ndx,ndy,bex
!        dimension bex(30)
   REAL(8) xxpmax,yypmax,xymax,zzpmax,zxmax,zymax,bex(30)
   INTEGER ndx,ndy
!        common/fpath/ppath
   character(len=256) :: ppath
!        common/iopsys/iopsy,termtype,ltt,s2gr
!                                     ltt no longer used
   INTEGER iopsy
   character(len=16) :: termtype   
   logical s2gr
!        common/fichier/filenm,pfnm
   character(len=23) :: filenm
   character(len=255), dimension(20) :: pfnm
END MODULE m4wfiles
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE m4cstates
!---------------------------------------------------------------------
!  Module containing definitions needed by the wfile routines
!---------------------------------------------------------------------
   USE DynacConstants, ONLY: iptsz
!        common/chstat1/cst(2000002),cstat(20),fcstat(20),ncstat,mcstat
!   REAL(8) cst(iptsz)
   REAL(8), allocatable :: cst(:)
   REAL(8) cstat(20),fcstat(20)
   INTEGER ncstat,mcstat
!        common/chstat2/cccst
   character(len=8), dimension(20) :: cccst
END MODULE m4cstates
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE mrouti1
!---------------------------------------------------------------------
!  Module containing additional definitions for the wfile routines
!---------------------------------------------------------------------
!        common/prtcnt/imax
!        common/grtyp/igrtyp
   INTEGER imax,igrtyp
!        common/gui/dgui
   logical dgui
END MODULE mrouti1
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE mrouti2
!---------------------------------------------------------------------
!  Module containing additional definitions for the wfile routines
!---------------------------------------------------------------------
!        common/pscl/yminsk,iskale
   REAL(8) yminsk
   INTEGER iskale
!        common/p2d/xxpar(100,100), yypar(100,100), xyar(100,100), &
!              zzpar(100,100), zxar(100,100), zyar(100,100)
   REAL(8) xxpar(100,100), yypar(100,100), xyar(100,100), &
           zzpar(100,100),  zxar(100,100), zyar(100,100)
!        common/mingw/mg
   logical mg
END MODULE mrouti2
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE m4files
!---------------------------------------------------------------------
!  Module containing additional definitions for the wfile routines
!---------------------------------------------------------------------
!        common/files/fname,lpath
   character(len=256) :: fname
   INTEGER lpath
END MODULE m4files
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MODULE m4files2
!---------------------------------------------------------------------
!  Module containing additional definitions for wfile10 routine
!---------------------------------------------------------------------
   USE DynacConstants, ONLY: iptsz
!   REAL(8) cx(iptsz),cxp(iptsz),cy(iptsz),cyp(iptsz)
   REAL(8), allocatable :: cx(:),cxp(:),cy(:),cyp(:)   
!   REAL(8) cz(iptsz),czp(iptsz)
   REAL(8), allocatable :: cz(:),czp(:)   
!   REAL(8) ctrx1(iptsz),ctry1(iptsz),ctrx2(iptsz),ctry2(iptsz)
   REAL(8), allocatable :: ctrx1(:),ctry1(:),ctrx2(:),ctry2(:)   
!   REAL(8) ctrx3(iptsz),ctry3(iptsz)
   REAL(8), allocatable :: ctrx3(:),ctry3(:)
END MODULE m4files2
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!> *******************************************************************
!! SUBROUTINE wfile1
!! Writes the data points which will be plotted by GNU to a file as
!! ell as the contour data for the ellipse
!!   dW/W envelope as f(z)
!!   dPHI envelope as f(z)
!< *******************************************************************
   SUBROUTINE wfile1(imax)
!  SUBROUTINE wfile1(imax,x,xp,cx,cy)
   USE DynacConstants, ONLY: cygwin
   USE m4wfiles, ONLY: iopsy,ppath
   USE m4files2, ONLY: cx,cxp,cy,cyp
   IMPLICIT NONE
!   REAL(8) x(2000002),xp(2000002),cx(300),cy(300)
   character(len=280) :: command
   character(len=256) :: fwpath
   INTEGER imax,i
!*******************************************************************
   command=''
   fwpath=''
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     fwpath=trim(ppath)//'dynac.cnt'
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
     if(cygwin) then
       fwpath=trim(ppath)//'dynac.cnt'
       command='rm -f '//trim(fwpath)
     else
       fwpath=trim(ppath)//'dynac.cnt'
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
! 2025 DBX this call not needed (?)   
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
   OPEN(unit=48,file=trim(fwpath))
   DO i=1,201
!     write(48,*) cx(i),cy(i)
     write(48,*) cy(i),cyp(i)
   ENDDO
   CLOSE(48)
   fwpath=''
   command=''
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     fwpath=trim(ppath)//'dynac.plt'
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
     if(cygwin) then
       fwpath=trim(ppath)//'dynac.plt'
       command='rm -f '//trim(fwpath)
     else
       fwpath=trim(ppath)//'dynac.plt'
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
   OPEN(unit=49,file=trim(fwpath))
   DO i=1,imax
     write(49,*) cx(i),cxp(i)
   ENDDO
   CLOSE(49)
   END SUBROUTINE wfile1
!> *******************************************************************
!! SUBROUTINE wfile2
!! Writes the .GNU file containing the commands to be executed by
!! GNUPLOT
!< *******************************************************************
   SUBROUTINE wfile2(isave,icontr,ipn)
   USE m4wfiles, ONLY: iopsy,termtype,s2gr,ppath,title,labels, &
                     uxmin,uxmax,uymin,uymax,filenm
   USE mrouti1, ONLY: dgui
   USE DynacConstants, ONLY: backslash,cygwin
   IMPLICIT NONE
   character(len=255) :: txt,outtxt
   character(len=280) :: command
   character(len=256) :: fwpath,myfrmt
   character(len=33) :: paf
   character(len=3) :: cpn,cfn
   REAL(8) ytitle
   INTEGER isave,icontr,ipn        
!*******************************************************************
   command=''
   fwpath=''
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     fwpath=trim(ppath)//'dynac.gnu'
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
     if(cygwin) then
       fwpath=trim(ppath)//'dynac.gnu'
       command='rm -f '//trim(fwpath)
     else
       fwpath=trim(ppath)//'dynac.gnu'
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
   if (isave.eq.0) then
     OPEN(unit=50,file=trim(fwpath))
   else
     call fn
     if (icontr.eq.2) filenm(1:2)='s3'
     if (icontr.eq.3) filenm(1:2)='s4'
     if (icontr.eq.4) filenm(1:2)='s5'
     filenm(18:21)='.gnu'
     paf(1:10)='savedplots'
     if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
       paf(11:11)="/"
     else
! WINDOWS
       paf(11:11)=backslash
     endif
     paf(12:32)=filenm(1:21)
     OPEN(unit=50,file=paf(1:32))
   endif
   write(50,"('set style data dots')")
   ytitle=0.99
   txt=''
   ipn=ipn-1
   cpn='   '
   txt=''
   txt='set terminal '//trim(termtype)
! number the plot window and number the file
   cfn='000'
   cpn=''
   if(ipn+1.lt.10) then
     write(cpn(1:1),'(I1)') ipn+1
     write(cfn(3:3),'(I1)') ipn+1
   elseif(ipn.lt.100) then
     write(cpn(1:2),'(I2)') ipn+1
     write(cfn(2:3),'(I2)') ipn+1
   else
     write(cpn(1:3),'(I3)') ipn+1
     write(cfn(1:3),'(I3)') ipn+1
   endif   
!   write(cpn,'(I3.3)') ipn+1
   outtxt=''
   outtxt="set output '"//trim(ppath)//"dynplot"//cfn//"."//trim(termtype)//"'"
   if(iopsy.eq.1) then
! LINUX
     if(dgui) then
! then number the plot window and let it persist
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
        txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 900,500'
        write(50,'(A)') trim(txt)
      endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 900,500'
         write(50,'(A)') trim(txt)
       endif
     endif
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 900,500'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 900,500'
         write(50,'(A)') trim(txt)
       endif
     endif
     if(dgui) then
       ytitle=0.985
     else
       ytitle=0.995
     endif
   else
! WINDOWS
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 900,500'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 900,500'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 900,500'
         write(50,'(A)') trim(txt)
       endif
     endif
   endif
   write(50,"('unset key')")
   if(iopsy.eq.1) then
! LINUX
     if(s2gr) then
       ytitle=0.980
     elseif(dgui) then
       ytitle=0.985
     else
       ytitle=0.980
     endif
   else
     ytitle=0.97
   endif
   write(50,'(A,A,A,F5.3)') 'set label "',trim(title),'" at screen 0.1 ,',ytitle
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(1)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(2)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") uxmin,uxmax
   write(50,"('set yrange [',f12.5,':',f12.5,']')") uymin,uymax
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set size 1., 0.98')")
   else
     write(50,"('set size 1., 0.98')")
   endif
   write(50,"('set samples 50')")
   if (icontr.eq.2) then
     if (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(ppath)//'dynac.plt'
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:2 with lines, "
         write(50,'(A,A1)') trim(myfrmt),backslash
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 3:4 with lines"
         write(50,'(A)') trim(myfrmt)
       else
         write(50,'(A,A1)') 'plot "dynac.plt" using 1:2 with lines, ',backslash
         write(50,'(A)') '"dynac.plt" using 3:4 with lines'
       endif
     else
       filenm(18:21)='.plt'
       write(50,'(A,A21,A,A1)') 'plot "',filenm,'" using 1:2 with lines, ',backslash
       write(50,'(A,A21,A)') '"',filenm,'" using 3:4 with lines'
     endif
   endif
   if (icontr.eq.3) then
     if (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(ppath)//'dynac.plt'
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:2 with lines"
         write(50,'(A)') trim(myfrmt)
       else
         write(50,'(A)') 'plot "dynac.plt" using 1:2 with lines'
       endif
     else
       filenm(18:21)='.plt'
       write(50,'(A,A21,A)')'plot "',filenm,'" using 1:2 with lines'
     endif
   endif
   if (icontr.eq.4) then
     if (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(ppath)//'dynac.plt'
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:2 with lines"
         write(50,'(A)') trim(myfrmt)
       else
         write(50,'(A)') 'plot "dynac.plt" using 1:2 with lines'
       endif
     else
       filenm(18:21)='.plt'
       write(50,'(A,A21,A)') 'plot "',filenm,'" using 1:2 with lines'
     endif
   endif
   if(.not. s2gr) then
     if(.not. dgui) write(50,'(A)')'pause -1 "hit return to continue"'
   endif  
   close (50)
   END SUBROUTINE wfile2
!> *******************************************************************
!! SUBROUTINE wfile3
!! Writes the data points which will be plotted by GNU to a file
!!        x,y envelopes as f(z)
!< *******************************************************************
   SUBROUTINE wfile3(imax)
   USE DynacConstants, ONLY: cygwin
   USE m4wfiles, ONLY: iopsy,ppath
   USE m4files2, ONLY: cx,cxp,cy,cyp
   IMPLICIT NONE
   character(len=256) :: fwpath
   character(len=280) :: command
!   REAL(8) x(2000002),xp(2000002),y(2000002),yp(2000002)
   INTEGER imax,i        
!*******************************************************************
   command=''
   fwpath=''
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     fwpath=trim(ppath)//"dynac.plt"
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
     if(cygwin) then
       fwpath=trim(ppath)//"dynac.plt"
       command='rm -f '//trim(fwpath)
     else
       fwpath=trim(ppath)//"dynac.plt"
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
   OPEN(unit=48,file=trim(fwpath))
   DO i=1,imax
     write(48,*) cx(i),cxp(i),cy(i),cyp(i)
   ENDDO
   CLOSE(48)
   END SUBROUTINE wfile3
!> *******************************************************************
!! SUBROUTINE wfile10
!! Writes the data points which will be plotted by GNU to a file and
!! stores the ellips contour
!< *******************************************************************
   SUBROUTINE wfile10(icont,imax)
   USE DynacConstants, ONLY: iptsz,cygwin
   USE m4wfiles, ONLY: iopsy,ppath,pfnm
   USE m4files2
   USE m4cstates
   USE mrouti1, ONLY: igrtyp
   IMPLICIT NONE
   character(len=256) :: fwpath
   character(len=280) :: command
   REAL(8) fprec   
   INTEGER klm,iunit,j,llpath   
!   REAL(8) x(2000002),xp(2000002),y(2000002),yp(2000002),z(2000002),zp(2000002)
   INTEGER icont,imax,i        
!*******************************************************************
   if (.not. allocated(cst))  allocate(cst(iptsz))
   llpath=len_trim(ppath)
!   write(6,*) "DBX in wfile10 at input ppath=",trim(ppath)
   if (icont.eq.1) then
     command=''
     fwpath=''
     fwpath=trim(ppath)//'dynac.cnt'
     if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
       command='rm -f '//trim(fwpath)      
     else
! WINDOWS
       if(cygwin) then
         command='rm -f '//trim(fwpath)            
       else
         command='if exist '//trim(fwpath)//' del '//trim(fwpath)
       endif
     endif
!     write(6,*) "DBX in wfile10 1 cmd=",command
     call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
!     write(6,*) "DBX in wfile10 1 after cmd"
!     write(6,*) "DBX in wfile10 1 fwpath=",trim(fwpath)
     OPEN(unit=51,file=trim(fwpath))
     DO i=1,201
       write(51,*) ctrx1(i),ctry1(i),ctrx2(i),ctry2(i),ctrx3(i),ctry3(i)
     ENDDO
     CLOSE(51)
   endif
   if (icont.eq.0) then
! store particle coordinates
     if(igrtyp.eq.1) then
       command=''
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command='rm -f '//trim(fwpath)
       else
! WINDOWS
         if(cygwin) then
           command='rm -f '//trim(fwpath)
         else
           fwpath=trim(ppath)//'dynac.plt'
         endif
       endif
!       write(6,*) "DBX in wfile10 0 cmd=",command
       call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
!       write(6,*) "DBX in wfile10 0 after cmd"
!       write(6,*) "DBX in wfile10 0 fwpath=",trim(fwpath)
       OPEN(unit=52,file=trim(fwpath))
       DO i=1,imax
         write(52,*) cx(i),cxp(i),cy(i),cyp(i),cz(i),czp(i)
       ENDDO
       CLOSE(52)
     else
       mcstat=0
       fprec=epsilon(cstat(1))
       DO j=1,ncstat
         klm=0
         DO i=1,imax
           if(abs(cst(i)-cstat(j)).le.fprec ) then
             klm=klm+1
           endif
         ENDDO
         if(igrtyp.eq.6) then 
           write(6,'(i8,A,f9.5)') klm,' particles with charge state ',cstat(j)
         elseif(igrtyp.eq.11) then
           if(j.eq.1) then
             write(6,'(i8,A,A,f5.2,A)') klm,' particles originally within zone ', &
                     'delimited by  0.0  and ',cstat(j),'*RMS'
           elseif(j.lt.ncstat) then
             write(6,'(i8,A,A,f5.2,A,f5.2,A)') klm,' particles originally within ', &
                     'zone delimited by ',cstat(j-1),' and ',cstat(j),'*RMS'
           else
             write(6,'(i8,A,f5.2,A)') klm,' particles beyond ',cstat(j-1),'*RMS'
           endif
         endif
         if(klm.ne.0) then
           mcstat=mcstat+1
           iunit=20+j
           command=''
           fwpath=''
           fwpath=trim(pfnm(j))
           if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
             fwpath='"'//trim(fwpath)//'"'
!             write(6,*) "DB wfile 10 fwpath3 ",trim(fwpath)
             command='rm -f '//trim(fwpath)
             call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
           else
! WINDOWS
             if(cygwin) then
               command='rm -f '//trim(fwpath)
             else
               command='if exist '//trim(fwpath)//' del '//trim(fwpath)
             endif
             call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
           endif
           fcstat(mcstat)=cstat(j)
           if(iopsy.le.3) then
             fwpath=trim(pfnm(j))
             OPEN(unit=iunit,file=trim(fwpath))
           else
!             write(6,*) "DBX88 in wfile10 0 pfnm=",j,trim(pfnm(j))
             OPEN(unit=iunit,file=pfnm(j))
           endif
           DO i=1,imax
             if(abs(cst(i)-cstat(j)).le.fprec ) then
               write(iunit,*) cx(i),cxp(i),cy(i),cyp(i),cz(i),czp(i)
             endif
           ENDDO
           CLOSE(iunit)
         endif
       ENDDO
     endif
   endif
   END SUBROUTINE wfile10
!> *******************************************************************
!! SUBROUTINE wfile11
!! Writes the data points which will be plotted by GNU to a file
!< *******************************************************************
   SUBROUTINE wfile11(imax)
   USE DynacConstants, ONLY: iptsz,cygwin
   USE m4wfiles, ONLY: iopsy,ppath,pfnm  
   USE m4files2, ONLY: cx,cxp,cy,cyp  
   USE m4cstates
   USE mrouti1, ONLY: igrtyp
   IMPLICIT NONE
   character(len=256) :: fwpath
   character(len=280) :: command
   REAL(8) fprec   
   INTEGER klm,iunit,j,llpath
!   REAL(8) x(2000002),xp(2000002),y(2000002),yp(2000002)
   INTEGER imax,i
!*******************************************************************
   if (.not. allocated(cst))  allocate(cst(iptsz))
   if (.not. allocated(cx))  allocate(cx(iptsz))
   if (.not. allocated(cxp)) allocate(cxp(iptsz))
   if (.not. allocated(cy))  allocate(cy(iptsz))
   if (.not. allocated(cyp)) allocate(cyp(iptsz))
   llpath=len_trim(ppath)
!   write(6,*) "DBX in wfile11 imax=",imax
! store particle coordinates
   IF(igrtyp.eq.2) then
     command=''
     fwpath=''
     fwpath=trim(ppath)//'dynac.plt'
     if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
       command='rm -f '//trim(fwpath)
     else
! WINDOWS
       if(cygwin) then
         command='rm -f '//trim(fwpath)
       else
         command='if exist '//trim(fwpath)//' del '//trim(fwpath)
       endif
     endif
!     write(6,*) "DBX cmd in wfile11: ",trim(COMMAND)
     call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
     if(iopsy.le.3) then
       OPEN(unit=52,file=trim(fwpath))
     else
       OPEN(unit=52,file='dynac.plt')
     endif
     DO i=1,imax
       write(52,*) cx(i),cxp(i),cy(i),cyp(i)
     ENDDO
     CLOSE(52)
   ELSE
     mcstat=0
     fprec=epsilon(cstat(1))
     DO j=1,ncstat
       klm=0
       DO i=1,imax
         if(abs(cst(i)-cstat(j)).le.fprec ) then
           klm=klm+1
         endif
       ENDDO
       if(igrtyp.eq.7) then 
         write(6,'(i8,A,f9.5)') klm,' particles with charge state ',cstat(j)
       elseif(igrtyp.eq.12) then
         if(j.eq.1) then
           write(6,'(i8,A,A,f5.2,A)') klm,' particles originally within zone ', &
                   'delimited by  0.0  and ',cstat(j),'*RMS'
         elseif(j.lt.ncstat) then
           write(6,'(i8,A,A,f5.2,A,f5.2,A)') klm,' particles originally within ', &
                   'zone delimited by ',cstat(j-1),' and ',cstat(j),'*RMS'
         else
           write(6,'(i8,A,f5.2,A)') klm,' particles beyond ',cstat(j-1),'*RMS'
         endif
       endif
       if(klm.ne.0) then
         mcstat=mcstat+1
         iunit=20+j
         fwpath=''
         fwpath=trim(pfnm(j))
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           command='rm -f '//trim(fwpath)
           call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)                                
         else
! WINDOWS
           if(cygwin) then
             command='rm -f '//trim(fwpath)
           else
             command='if exist '//trim(fwpath)//' del '//trim(fwpath)
           endif
           call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)                                
         endif
         fcstat(mcstat)=cstat(j)
         if(iopsy.le.3) then
!           fwpath=''
!           fwpath=trim(pfnm(j))
!           write(6,*) "DBX88 in wfile11 0 fwpath=",trim(fwpath)
           OPEN(unit=iunit,file=trim(fwpath))
         else
           OPEN(unit=iunit,file=pfnm(j))
         endif  
         DO i=1,imax
           if(abs(cst(i)-cstat(j)).le.fprec ) then
             write(iunit,*) cx(i),cxp(i),cy(i),cyp(i)
           endif
         ENDDO
         CLOSE(iunit)
       endif
     ENDDO
   ENDIF
   END SUBROUTINE wfile11
!> *******************************************************************
!! SUBROUTINE wfile21
!! xz-yz distribution plots and x,y,z & x',y',z' profiles
!< *******************************************************************
   SUBROUTINE wfile21(isave,ipn)
   USE m4wfiles, ONLY: iopsy,termtype,s2gr,ppath,filenm,pfnm, &
                     xmin,xmax,ymin,ymax,title,labels
   USE m4cstates
   USE mrouti1, ONLY: dgui,igrtyp,imax
   USE mrouti2, ONLY: yminsk,iskale
   USE DynacConstants, ONLY: backslash,iptsz,cygwin
   IMPLICIT NONE
   character(len=256) :: fwpath,myfrmt
   character(len=255) :: strng,fnm,txt,outtxt
   character(len=280) :: command
   character(len=40) :: labels3,labels4
   character(len=33) :: paf
   character(len=8) :: parcnt
   character(len=8) :: toc
   character(len=7) :: indxx
   character(len=3) :: cpn,cfn
   character(len=2) :: indx
   INTEGER j,isave,ipn,llpath
   REAL(8) xmin2,xmax2,ymin2,ymax2,ytitle
   INTEGER nn        
!*******************************************************************
   if (.not. allocated(cst))  allocate(cst(iptsz))
   command=''
   fwpath=''
   fwpath=trim(ppath)//'dynac.gnu'
   llpath=len_trim(ppath)
   write(6,"(i8,' particles total')") imax
   write(parcnt,'(I8)') imax
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     command='rm -f '//trim(fwpath)    
   else
! WINDOWS
     if(cygwin) then
       command='rm -f '//trim(fwpath)    
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
   if(isave.eq.0) then
     if(iopsy.le.3) then
!       if(iopsy.eq.2) then
!         if(cygwin) then
!           command='rm -f '//trim(fwpath)
!         else
!             fwpath=trim(ppath)//'dynac.gnu'
!             command='if exist '//trim(fwpath)//' del '//trim(fwpath)
!         endif
!       else
!         fwpath=trim(ppath)//'dynac.gnu'
!       endif
!       write(6,*) "DBX44 in wfile21 fwpath=",trim(fwpath)
       OPEN(unit=50,file=trim(fwpath))
     else
       OPEN(unit=50,file='dynac.gnu')
     endif
   else
     call fn
     filenm(1:2)='s2'
     filenm(18:21)='.gnu'
     paf(1:10)='savedplots'
     if(iopsy.eq.1) then
! LINUX
       paf(11:11)="/"
     elseif(iopsy.eq.3) then
! MAC
       paf(11:11)="/"
     else
! WINDOWS
       paf(11:11)=backslash
     endif
     paf(12:32)=filenm(1:21)
     OPEN(unit=50,file=paf(1:32))
   endif
   write(50,"('set style data dots',/,'set pointsize 0.01')")
   ipn=ipn-1
   cpn='   '
   txt=''
   txt='set terminal '//trim(termtype)
! number the plot window 
   cfn='000'
   cpn=''
   if(ipn+1.lt.10) then
     write(cpn(1:1),'(I1)') ipn+1
     write(cfn(3:3),'(I1)') ipn+1
   elseif(ipn.lt.100) then
     write(cpn(1:2),'(I2)') ipn+1
     write(cfn(2:3),'(I2)') ipn+1
   else
     write(cpn(1:3),'(I3)') ipn+1
     write(cfn(1:3),'(I3)') ipn+1
   endif   
!   write(cpn,'(I3.3)') ipn+1
   outtxt=''
   outtxt="set output '"//trim(ppath)//"dynplot"//cfn//"."//trim(termtype)//"'"
   ytitle=0.99
   if(iopsy.eq.1) then
! LINUX
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     endif
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.985
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
         ytitle=0.990
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.985
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
         ytitle=0.990
       endif
     endif
   else
! WINDOWS
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.52'
     if(dgui) then
       ytitle=0.99
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     else
       ytitle=0.985
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.990
       else  
         txt=trim(txt)//' title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     endif
   endif
   if(ncstat.eq.1) then
     write(50,"('unset key')")
   else
     if(iopsy.eq.1) then
! LINUX
       if(igrtyp.eq.12) then
         if(s2gr) then
           write(50,"('set key at screen 0.6, 0.96 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         elseif(dgui) then
           write(50,"('set key at screen 0.58, 0.95 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.59, 0.95 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         endif              
       else
         if(s2gr) then
           write(50,"('set key at screen 0.57, 0.96 spacing 0.8', &
           & ' samplen 1 textcolor rgb variable ')")
         elseif(dgui)then
           write(50,"('set key at screen 0.555, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.565, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         endif              
       endif
     elseif(iopsy.eq.3) then
! MAC
       if(igrtyp.eq.12) then
         if(s2gr) then
           write(50,"('set key at screen 0.6, 0.96 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         else
!           write(50,"('set key at screen 0.59, 0.95 spacing 0.8', &
           write(50,"('set key at screen 0.58, 0.95 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         endif              
       else
         if(s2gr) then
           write(50,"('set key at screen 0.57, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         else
!           write(50,"('set key at screen 0.57, 0.95 spacing 0.8', &
           write(50,"('set key at screen 0.555, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")
         endif              
       endif
     else
! WINDOWS
       if(igrtyp.eq.12) then
         if(s2gr) then
           write(50,"('set key at screen 0.585, 0.95 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")   
         else
           write(50,"('set key at screen 0.585, 0.95 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")            
         endif                        
       else
         if(s2gr) then
           write(50,"('set key at screen 0.565, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")   
         else
           write(50,"('set key at screen 0.565, 0.97 spacing 0.8', &
           & ' samplen 1 textcolor rgb variable ')")             
         endif                       
       endif
     endif
   endif
   write(50,'(A,A,A,F5.3)') 'set label "',trim(title),'" at screen 0.13 ,',ytitle
   write(50,"('set multiplot')")
! x-z
   write(50,"('set size 0.5,0.5')")
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.,0.49')")
   else
     write(50,"('set origin 0.,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(1)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(2)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(1),xmax(1)
   write(50,"('set yrange [',f12.6,':',f12.6,']')") ymin(1),ymax(1)
   if(igrtyp.eq.2) then
     if(isave.eq.0) then
       llpath=len_trim(ppath)
       myfrmt=''
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.le.3) then
         if(iopsy.eq.2) then
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         else
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A)') 'plot "dynac.plt" using 1:2 with dots lc 7'
       else
         write(50,'(A)') 'plot "dynac.plt" using 1:2 with dots lc 0'
       endif
     else
       filenm(18:21)='.plt'
       if(iopsy.eq.3) then
! MAC
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 1:2 with dots lc 8'
       elseif(iopsy.eq.2 .and. termtype.eq.'qt') then
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 1:2 with dots lc 8'
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 1:2 with dots lc 7'
       else
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 1:2 with dots lc 0' 
       endif
     endif
   else
     strng=pfnm(1)
     toc=cccst(1)
     indxx=trim(toc)
     if(isave.eq.0) then
       strng=pfnm(1)
       toc=cccst(1)
       indxx=trim(toc)
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
!         write(6,*) "DBX45 in wfile21 fwpath=",trim(fwpath)
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indxx//"' with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A4,A,A1)') 'plot "',pfnm(1),'" using 1:2 title "',indxx, &
               '" with dots lc 1, ',backslash
       endif
       do j=2,mcstat-1
         strng=''
         write(strng,'(I2)') j
         toc=cccst(j)
         indxx=trim(toc)
         if(iopsy.le.3) then
           fwpath=''
           fwpath=trim(pfnm(j))
!           write(6,*) "DBX47 in wfile21 fwpath=",trim(fwpath)
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indxx//"' with dots lc "//trim(strng)//", "
           write(50,'(A,A1)') trim(myfrmt),backslash
         else           
           write(50,'(A,A11,A,A4,A,I2,A,A1)') '     "',pfnm(j),'" using 1:2 title "',indxx, &
               '" with dots lc ',j,',',backslash
         endif
       enddo
       strng=''
       write(strng,'(I2)') mcstat
       if(igrtyp.eq.12) then
         toc=cccst(mcstat-1)
         indxx=trim(toc)
         if(iopsy.le.3) then
           fwpath=''
           fwpath=trim(pfnm(mcstat))
!           write(6,*) "DBX48 in wfile21 fwpath=",trim(fwpath)
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 1:2 title ' >"//indxx//"' with dots lc "//trim(strng)
           write(50,'(A)') trim(myfrmt)
         else           
           write(50,'(A,A11,A,A4,A,I2)') '     "',pfnm(j),'" using 1:2 title " >',indxx, &
               '" with dots lc ',mcstat
         endif
       else
         toc=cccst(mcstat)
         indxx=trim(toc)
         if(iopsy.le.3) then
           fwpath=''
           fwpath=trim(pfnm(mcstat))
!           write(6,*) "DBX49 in wfile21 fwpath=",trim(fwpath)
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indxx//"' with dots lc "//trim(strng)
           write(50,'(A)') trim(myfrmt)
         else           
           write(50,'(A,A11,A,A4,A,I2)') '     "',pfnm(j),'" using 1:2 title " ',indxx, &
               '" with dots lc ',mcstat
         endif
       endif
     else
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A4,A,A1)') 'plot "',filenm,'" using 1:2 title "',indxx, &
               '" with dots lc 1, ',backslash
       do j=2,mcstat-1
         strng=pfnm(j)
         toc=cccst(j)
         indxx=trim(toc)
         filenm(18:23)=strng(6:11)
         write(50,'(A,A23,A,A4,A,I2,A,A1)') '     "',filenm,'" using 1:2 title "',indxx, &
               '" with dots lc ',j,',',backslash
       enddo
       strng=pfnm(mcstat)
       filenm(18:23)=strng(6:11)
       if(igrtyp.eq.12) then
         toc=cccst(mcstat-1)
         indxx=trim(toc)
         write(50,'(A,A23,A,A4,A,I2)') '     "',filenm,'" using 1:2 title " >',indxx, &
               '" with dots lc ',mcstat
       else
         toc=cccst(mcstat)
         indxx=trim(toc)
         write(50,'(A,A23,A,A4,A,I2)') '     "',filenm,'" using 1:2 title " ',indxx, &
               '" with dots lc ',mcstat
       endif
     endif
   endif
   write(50,"('unset key')")
   write(50,"('unset label')")
! y-z
   write(50,"('set size 0.5,0.5')")
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.5,0.49')")
   else
     write(50,"('set origin 0.5,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(3)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(4)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(2),xmax(2)
   write(50,"('set yrange [',f12.6,':',f12.6,']')") ymin(2),ymax(2)
   if(igrtyp.eq.2) then
     if(isave.eq.0) then
       llpath=len_trim(ppath)
       myfrmt=''
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.le.3) then
         if(iopsy.eq.2) then
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         else
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A)') 'plot "dynac.plt" using 3:4 with dots lc 7'
       else
         write(50,'(A)') 'plot "dynac.plt" using 3:4 with dots lc 0'
       endif
     else
       filenm(18:21)='.plt'
       if(iopsy.eq.3) then
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 3:4 with dots lc 8'
       elseif(iopsy.eq.2 .and. termtype.eq.'qt') then
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 3:4 with dots lc 8'
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 3:4 with dots lc 7'
       else
         write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 3:4 with dots lc 0'
       endif
     endif
   else
     if(isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 3:4 with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A,A1)') 'plot "',pfnm(1),'" using 3:4', &
               ' with dots lc 1, ',backslash
       endif
       do j=2,mcstat-1
         strng=''
         write(strng,'(I2)') j
         if(iopsy.le.3) then
           fwpath=''
           fwpath=trim(pfnm(j))
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 3:4 with dots lc "//trim(strng)//", "
           write(50,'(A,A1)') trim(myfrmt),backslash
         else           
           write(50,'(A,A11,A,A,I2,A,A1)') '     "',pfnm(j),'" using 3:4', &
               ' with dots lc ',j,',',backslash
         endif
       enddo
       strng=''
       write(strng,'(I2)') mcstat
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(mcstat))
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 3:4 with dots lc "//trim(strng)
         write(50,'(A)') trim(myfrmt)
       else           
         write(50,'(A,A11,A,A,I2)') '     "',pfnm(mcstat),'" using 3:4', &
               ' with dots lc ',mcstat
       endif
     else
       strng=pfnm(1)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,A1)') 'plot "',filenm,'" using 3:4', &
               ' with dots lc 1, ',backslash
       do j=2,mcstat-1
         strng=pfnm(j)
         filenm(18:23)=strng(6:11)
         write(50,'(A,A23,A,A,I2,A,A1)') '     "',filenm,'" using 3:4', &
               ' with dots lc ',j,',',backslash
       enddo
       strng=pfnm(mcstat)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,I2)') '     "',filenm,'" using 3:4', &
               ' with dots lc ',mcstat
     endif
   endif
! x,y,z profiles
! new start
   labels3="X, Y, Z (RMS multiples)"
   labels4="N (normalized)"
   xmin2=-5.
   xmax2=5.
   ymin2=0.
   if(iskale.eq.1) then
     if (yminsk.gt.0. .and. yminsk.lt.1.) then
       ymin2=yminsk 
     else
       write(6,*) '***         Error in logscale          ***'
       write(6,*) '** log scale minimum defaults to 1.E-06 **'
       ymin2=1.e-6
     endif
   endif
   ymax2=1.
! new end
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels3),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels4),'"'
   if(iskale.eq.1) then
     write(50,"('set logscale y')")
     write(50,'(A)') 'set format y "%.0t.E%+02T"'
   endif
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin2,xmax2
   write(50,"('set yrange [',E10.4,':',f12.6,']')") ymin2,ymax2
   if(iopsy.eq.1) then
! LINUX        
     if(s2gr) then
       write(50,"('set key at screen 0.55, 0.47 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.545, 0.46 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     endif              
   elseif(iopsy.eq.3) then
! MAC
     if(s2gr) then
       write(50,"('set key at screen 0.535, 0.475 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.535, 0.46 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     endif              
   else
! WINDOWS
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.47 spacing 1.0', &
       &     ' samplen 1 textcolor rgb variable ')")    
     else
       write(50,"('set key at screen 0.545, 0.47 spacing 1.0', &
       &     ' samplen 1 textcolor rgb variable ')")             
     endif         
   endif
   if(isave.eq.0) then
     if(iopsy.le.3) then
       fnm=pfnm(1)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' X'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines, "
!       write(6,*) "DBX at 1519 ",trim(fwpath)
       write(50,'(A,A1)') trim(myfrmt),backslash
       fnm=pfnm(2)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' Y'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 2, "
       write(50,'(A,A1)') trim(myfrmt),backslash
       fnm=pfnm(3)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' Z'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 3"
       write(50,'(A)') trim(myfrmt)
     else
       fnm=pfnm(1)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' X'
       write(50,'(A,A11,A,A2,A,A1)') 'plot "',fnm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
       fnm=pfnm(2)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' Y'
       write(50,'(A,A11,A,A2,A,A1)') '     "',fnm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
       fnm=pfnm(3)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx=' Z'
       write(50,'(A,A11,A,A2,A)') '     "',fnm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
     endif
   else
     strng=pfnm(1)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' X'
     write(50,'(A,A23,A,A2,A,A1)') 'plot "',filenm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
     strng=pfnm(2)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' Y'
     write(50,'(A,A23,A,A2,A,A1)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
     strng=pfnm(3)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' Z'
     write(50,'(A,A23,A,A2,A)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
   endif
   write(50,"('unset key')")
   if(iskale.eq.1) then
     write(50,"('unset logscale y')")
     write(50,'(A)') 'set format y "%g"'
   endif
!
! xp,yp,zp profiles
! new start
   labels3="Xp, Yp, Zp (RMS multiples)"
   labels4="N (normalized)"
   xmin2=-5.
   xmax2=5.
   ymin2=0.
   if(iskale.eq.1) then
     if (yminsk.gt.0. .and. yminsk.lt.1.) then
       ymin2=yminsk  
     else
       ymin2=1.e-6
     endif
   endif
   ymax2=1.
! new end
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.5,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels3),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels4),'"'
   if(iskale.eq.1) then
     write(50,"('set logscale y')")
     write(50,'(A)') 'set format y "%.0t.E%+02T"'
   endif
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin2,xmax2
   write(50,"('set yrange [',E10.4,':',f12.6,']')") ymin2,ymax2
   if(iopsy.eq.1) then
     if(s2gr) then
       write(50,"('set key at screen 0.55, 0.17 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.545, 0.18 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     endif
   elseif(iopsy.eq.3) then
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.18 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.535, 0.18 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     endif          
   else
! Windows
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.18 spacing 1.0', &
       &     ' samplen 1 textcolor rgb variable ')")    
     else
       write(50,"('set key at screen 0.545, 0.18 spacing 1.0', &
       &     ' samplen 1 textcolor rgb variable ')")            
     endif        
   endif
   if(isave.eq.0) then
     if(iopsy.le.3) then
       fnm=pfnm(4)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Xp'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines, "
       write(50,'(A,A1)') trim(myfrmt),backslash
       fnm=pfnm(5)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Yp'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 2, "
       write(50,'(A,A1)') trim(myfrmt),backslash
       fnm=pfnm(6)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Zp'
       fwpath=''
       fwpath=trim(fnm)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 3"
       write(50,'(A)') trim(myfrmt)
     else
       fnm=pfnm(4)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Xp'
       write(50,'(A,A11,A,A2,A,A1)') 'plot "',fnm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
       fnm=pfnm(5)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Yp'
       write(50,'(A,A11,A,A2,A,A1)') '     "',fnm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
       fnm=pfnm(6)
       nn=len_trim(fnm)
       fnm(nn-2:nn)='pro'
       indx='Zp'
       write(50,'(A,A11,A,A2,A,A1)') '     "',fnm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
     endif
   else
     strng=pfnm(4)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Xp'
     write(50,'(A,A23,A,A2,A,A1)') 'plot "',filenm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
     strng=pfnm(5)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Yp'
     write(50,'(A,A23,A,A2,A,A1)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
     strng=pfnm(6)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Zp'
     write(50,'(A,A23,A,A2,A)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
   endif
   write(50,"('unset key')")
   if(iskale.eq.1) then
     write(50,"('unset logscale y')")
     write(50,'(A)') 'set format y "%g"'
   endif
!
   write(50,"('unset multiplot')")
   if(.not. s2gr) then
     if(.not. dgui) write(50,'(A)')'pause -1 "hit return to continue"'
   endif  
   close (50)
   END SUBROUTINE wfile21
!> *******************************************************************
!! SUBROUTINE wfile121
!! xz-yz density plots and x,y,z & x',y',z' profiles
!< *******************************************************************
   SUBROUTINE wfile121(isave,ipn)
   USE m4wfiles, ONLY: iopsy,termtype,s2gr,ppath,filenm,pfnm, &
                     xmin,xmax,ymin,ymax,title,labels,&
                     ndx,ndy,zxmax,zymax,bex
   USE mrouti1, ONLY: dgui,imax
   USE mrouti2, ONLY: yminsk,iskale
   USE DynacConstants, ONLY: backslash,cygwin
   IMPLICIT NONE
   character(len=280) :: command
   character(len=256) :: fwpath,myfrmt
   character(len=255) :: strng,fnm,txt,outtxt
   character(len=50), dimension(3) :: cols
   character(len=40) :: labels3,labels4
   character(len=33) :: paf
   character(len=10) :: sc
   character(len=8) :: hm,vm,ho,vo,hr,vr
   character(len=8) :: parcnt
   character(len=3) :: cpn,cfn
   character(len=2) :: indx 
   INTEGER isave,ipn
   REAL(8) xmin2,xmax2,ymin2,ymax2,ytitle
   INTEGER nn,ll
!*******************************************************************
   command=''
   ll=len_trim(ppath)
   fwpath=''
   fwpath=trim(ppath)//'dynac.gnu'
   write(6,"(i8,' particles total')") imax
   write(parcnt,'(I8)') imax
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     command='rm -f '//trim(fwpath)    
   else
! WINDOWS
     if(cygwin) then
       command='rm -f '//trim(fwpath)    
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
!   write(6,*) "DBX in wfile121 cmd=",trim(COMMAND)
   call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
   if(isave.eq.0) then
     OPEN(unit=50,file=trim(fwpath))
   else
     call fn
     filenm(1:2)='s2'
     filenm(18:21)='.gnu'
     paf(1:10)='savedplots'
     if(iopsy.eq.1) then
! LINUX
       paf(11:11)="/"
     elseif(iopsy.eq.3) then
! MAC
       paf(11:11)="/"
     else
! WINDOWS
       paf(11:11)=backslash
     endif
     paf(12:32)=filenm(1:21)
     OPEN(unit=50,file=paf(1:32))
   endif
   write(50,"('set style data dots',/,'set pointsize 0.01')")
   ipn=ipn-1
   cpn='   '
   txt=''
   txt='set terminal '//trim(termtype)
! number the plot window 
   cfn='000'
   cpn=''
   if(ipn+1.lt.10) then
     write(cpn(1:1),'(I1)') ipn+1
     write(cfn(3:3),'(I1)') ipn+1
   elseif(ipn.lt.100) then
     write(cpn(1:2),'(I2)') ipn+1
     write(cfn(2:3),'(I2)') ipn+1
   else
     write(cpn(1:3),'(I3)') ipn+1
     write(cfn(1:3),'(I3)') ipn+1
   endif   
!    write(cpn,'(I3.3)') ipn+1
   outtxt=''
   outtxt="set output '"//trim(ppath)//"dynplot"//cfn//"."//trim(termtype)//"'"
   ytitle=0.99
   if(iopsy.eq.1) then
! LINUX
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     endif
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.980
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
         ytitle=0.985
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.980              
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
         ytitle=0.990              
       endif
     endif
   else
! WINDOWS
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.52'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.985 
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
         ytitle=0.985              
       else  
         txt=trim(txt)//' title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     endif
   endif
   write(50,"('unset key')")
   write(50,'(A,A,A,F5.3)') 'set label "',trim(title),'" at screen 0.13 ,',ytitle
   write(50,"('set multiplot')")
! x-z
   write(50,"('set size 0.495,0.55')")
   if(iopsy.eq.1) then
! LINUX
!     write(50,"('set origin 0.0,0.49')")
     write(50,"('set origin 0.015,0.49')")
   else
     write(50,"('set origin 0.015,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(1)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(2)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(1),xmax(1)
   write(50,"('set yrange [',f12.6,':',f12.6,']')") ymin(1),ymax(1)
   write(50,"('set dgrid3d 20,20')")
   write(50,"('set pm3d map interpolate 0,0')")
   write(50,'(A,A,A)') 'set palette defined ( 0 "white", 1 "pink", ', &
                       '2 "purple", 3  "blue", 4 "green", 5 "yellow",', &
                       '6 "orange", 7 "red", 8 "black" )'   
! splot 'dynac.plt' u (xmul*($1-10.5)/20.):(xpmul*($2-10.5)/20.):(100*$3/fmax)
   hm=''
   vm=''
   ho=''
   vo=''
   hr=''
   vr=''
   sc=''
   write(hm,'(F8.3)') bex(18)-bex(17)
   write(vm,'(F8.3)') bex(20)-bex(19)
   write(ho,'(F8.3)') float(ndx+1)/2.
   write(vo,'(F8.3)') float(ndy+1)/2.
   write(hr,'(F8.3)') float(ndx)
   write(vr,'(F8.3)') float(ndy)
!   write(6,*) "DBX zxmax at 1690 ",zxmax
   write(sc,'(F10.2)') zxmax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$3/'//sc//')'
   if(isave.eq.0) then
     fwpath=''
     fwpath=trim(ppath)//'dynac.plt'
!     write(6,*) "DBX in wfile121 fwp=",trim(fwpath)
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
   else
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   endif
   write(50,"('unset key')")
   write(50,"('unset label')")
! y-z
   write(50,"('set size 0.495,0.55')")
   if(iopsy.eq.1) then
! LINUX
!     write(50,"('set origin 0.495,0.49')")
     write(50,"('set origin 0.5,0.49')")
   else
     write(50,"('set origin 0.5,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(3)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(4)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(2),xmax(2)
   write(50,"('set yrange [',f12.6,':',f12.6,']')") ymin(2),ymax(2)
   hm=''
   vm=''
   sc=''
   write(hm,'(F8.3)') bex(22)-bex(21)
   write(vm,'(F8.3)') bex(24)-bex(23)
!   write(6,*) "DBX zymax at 1726 ",zymax   
   write(sc,'(F10.2)') zymax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$4/'//sc//')'
   if(isave.eq.0) then
     fwpath=''
     fwpath=trim(ppath)//'dynac.plt'
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
  else
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   endif
! x,y,z profiles
! new start
   labels3="X, Y, Z (RMS multiples)"
   labels4="N (normalized)"
   xmin2=-5.
   xmax2=5.
   ymin2=0.
   if(iskale.eq.1) then
     if (yminsk.gt.0. .and. yminsk.lt.1.) then
       ymin2=yminsk
     else
       write(6,*) '***         Error in logscale          ***'
       write(6,*) '** log scale minimum defaults to 1.E-06 **'
       ymin2=1.e-6
     endif
   endif
   ymax2=1.
! new end
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels3),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels4),'"'
   if(iskale.eq.1) then
     write(50,"('set logscale y')")
     write(50,'(A)') 'set format y "%.0t.E%+02T"'
   endif
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin2,xmax2
   write(50,"('set yrange [',E10.4,':',f12.6,']')") ymin2,ymax2
   if(iopsy.eq.1) then
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.45 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.545, 0.45 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     endif
   elseif(iopsy.eq.3) then
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.46 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.535, 0.475 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     endif         
   else
     write(50,"('set key at screen 0.545, 0.47 spacing 1.0', &
     &     ' samplen 1 textcolor rgb variable ')")
   endif
   if(isave.eq.0) then
     fnm=pfnm(1)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx=' X'
     fwpath=trim(fnm)
!     write(6,*) "DBX in wfile121 fwpath=",trim(fwpath)
     myfrmt=''
     myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines, "
     write(50,'(A,A1)') trim(myfrmt),backslash
     fnm=pfnm(2)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx=' Y'
     fwpath=trim(fnm)
     myfrmt=''
     myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 2, "
     write(50,'(A,A1)') trim(myfrmt),backslash
     fnm=pfnm(3)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx=' Z'
     fwpath=''
     fwpath=trim(fnm)
     myfrmt=''
     myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 3"
     write(50,'(A)') trim(myfrmt)
   else
     strng=pfnm(1)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' X'
     write(50,'(A,A23,A,A2,A,A1)') 'plot "',filenm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
     strng=pfnm(2)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' Y'
     write(50,'(A,A23,A,A2,A,A1)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
     strng=pfnm(3)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx=' Z'
     write(50,'(A,A23,A,A2,A)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
   endif
   write(50,"('unset key')")
   if(iskale.eq.1) then
     write(50,"('unset logscale y')")
     write(50,'(A)') 'set format y "%g"'
   endif
!
! xp,yp,zp profiles
! new start
   labels3="Xp, Yp, Zp (RMS multiples)"
   labels4="N (normalized)"
   xmin2=-5.
   xmax2=5.
   ymin2=0.
   if(iskale.eq.1) then
     if (yminsk.gt.0. .and. yminsk.lt.1.) then
       ymin2=yminsk
     else
       ymin2=1.e-6
     endif
   endif
   ymax2=1.
! new end
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.5,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels3),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels4),'"'
   if(iskale.eq.1) then
     write(50,"('set logscale y')")
     write(50,'(A)') 'set format y "%.0t.E%+02T"'
   endif
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin2,xmax2
   write(50,"('set yrange [',E10.4,':',f12.6,']')") ymin2,ymax2
   if(iopsy.eq.1) then
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.19 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.545, 0.19 spacing 0.9', &
       & ' samplen 1 textcolor rgb variable ')")
     endif
   elseif(iopsy.eq.3) then
     if(s2gr) then
       write(50,"('set key at screen 0.545, 0.18 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     else
       write(50,"('set key at screen 0.535, 0.17 spacing 0.9', &
       &     ' samplen 1 textcolor rgb variable ')")
     endif                   
   else
     write(50,"('set key at screen 0.545, 0.17 spacing 1.0', &
     &     ' samplen 1 textcolor rgb variable ')")
   endif
   if(isave.eq.0) then
     fnm=pfnm(4)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx='Xp'
     fwpath=''
     fwpath=trim(fnm)
     myfrmt=''
     myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines, "
     write(50,'(A,A1)') trim(myfrmt),backslash
     fnm=pfnm(5)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx='Yp'
     fwpath=''
     fwpath=trim(fnm)
     myfrmt=''
     myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 2, "
     write(50,'(A,A1)') trim(myfrmt),backslash
     fnm=pfnm(6)
     nn=len_trim(fnm)
     fnm(nn-2:nn)='pro'
     indx='Zp'
     fwpath=''
     fwpath=trim(fnm)
     myfrmt=''
     myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indx//"' with lines ls 3"
     write(50,'(A)') trim(myfrmt)
   else
     strng=pfnm(4)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Xp'
     write(50,'(A,A23,A,A2,A,A1)') 'plot "',filenm,'" using 1:2 title "',indx, &
               '" with lines, ',backslash
     strng=pfnm(5)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Yp'
     write(50,'(A,A23,A,A2,A,A1)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 2, ',backslash
     strng=pfnm(6)
     filenm(18:20)=strng(6:8)
     filenm(21:23)='pro'
     indx='Zp'
     write(50,'(A,A23,A,A2,A)') '     "',filenm,'" using 1:2 title "',indx, &
               '" with lines ls 3'
   endif
   write(50,"('unset key')")
   if(iskale.eq.1) then
     write(50,"('unset logscale y')")
     write(50,'(A)') 'set format y "%g"'
   endif
!
   write(50,"('unset multiplot')")
   if(.not. s2gr) then
     if(.not. dgui) write(50,'(A)')'pause -1 "hit return to continue"'
   endif  
   close (50)
   END SUBROUTINE wfile121
!> *******************************************************************
!! SUBROUTINE wfile20
!! xx'-yy'-xy-zz'
!< *******************************************************************
   SUBROUTINE wfile20(isave,ipn)
   USE m4wfiles, ONLY: iopsy,termtype,s2gr,ppath,filenm,pfnm, &
                     title,labels,xmin,xmax,ymin,ymax
   USE m4cstates
   USE mrouti1
   USE m4files
   USE DynacConstants, ONLY: backslash,iptsz,cygwin
   IMPLICIT NONE
   character(len=256) :: command,lfname
   character(len=256) :: fwpath,myfrmt
   character(len=255) :: txt,outtxt
   character(len=33) :: paf
   character(len=255) :: strng
   character(len=8) :: parcnt
   character(len=8) :: toc
   character(len=7) :: indxx
   character(len=3) :: cpn,cfn
   INTEGER j,isave,ipn,llpath
   REAL(8) ytitle
   command=''
   lfname=''
   fwpath=''
!*******************************************************************
   if (.not. allocated(cst))  allocate(cst(iptsz))
   write(parcnt,'(I8)') imax
   write(6,"(i8,' particles total')") imax
   ytitle=0.995
   llpath=len_trim(ppath)
   fwpath=''
   fwpath=trim(ppath)//'dynac.gnu'
   if(iopsy.eq.1) then
! LINUX
     command='rm -f '//trim(fwpath)    
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     command='rm -f '//trim(fwpath)    
     if(dgui) then
       if(s2gr) then
         ytitle=0.985
       else
         ytitle=0.99
       endif
     else
       if(s2gr) then
         ytitle=0.985
       else
         ytitle=0.992
       endif
     endif
   else
! WINDOWS
     if(dgui) then
       ytitle=0.99
     else
       if(s2gr) then
         ytitle=0.988
       else
         ytitle=0.985
       endif
     endif          
     if(cygwin) then
       command='rm -f '//trim(fwpath)    
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
!   write(6,*) "DBX34 in wfile20 cmd=",trim(COMMAND)
   call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
   IF (isave.eq.0) then
     OPEN(unit=50,file=trim(fwpath))
   ELSE
     call fn
     filenm(1:2)='s1'
     filenm(18:21)='.gnu'
     paf(1:10)='savedplots'
     if(iopsy.eq.1) then
! LINUX
       paf(11:11)="/"
     elseif(iopsy.eq.3) then
! MAC
       paf(11:11)="/"
     else
! WINDOWS
       paf(11:11)=backslash
     endif
     paf(12:32)=filenm(1:21)
     OPEN(unit=50,file=paf(1:32))
   ENDIF
   write(50,"('set style data dots',/,'set pointsize 0.01')")
   if(mcstat.eq.1) then
     write(50,"('unset key')")
   else
     if(iopsy.eq.1) then
       if(igrtyp.eq.11) then
         if(s2gr) then
           write(50,"('set key at screen 0.59, 0.96 spacing 0.9 maxcols 1', &
         & ' samplen 1 horizontal textcolor rgb variable ')")
         elseif(dgui) then
           write(50,"('set key at screen 0.58, 0.95 spacing 0.8', &
         & ' samplen 1 textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.59, 0.95 spacing 0.8', &
         & ' samplen 1 textcolor rgb variable ')")
         endif
       else
         if(s2gr) then
           write(50,"('set key at screen 0.57, 0.96 spacing 0.8 maxcols 1', &
         & ' samplen 1 horizontal textcolor rgb variable ')")
         elseif(dgui)then
           write(50,"('set key at screen 0.555, 0.97 spacing 0.8', &
         & ' samplen 1 textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.565, 0.97 spacing 0.8', &
         & ' samplen 1 textcolor rgb variable ')")
         endif
       endif
     elseif(iopsy.eq.3) then
       if(igrtyp.eq.11) then
         if(s2gr) then
           write(50,"('set key at screen 0.59, 0.95 spacing 0.9 maxcols 1', &
         & ' samplen 1 horizontal textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.58, 0.95 spacing 0.9', &
         & ' samplen 1 textcolor rgb variable ')")
         endif
       else
         if(s2gr) then
           write(50,"('set key at screen 0.575, 0.97 spacing 0.9 maxcols 1', &
         & ' samplen 1 horizontal textcolor rgb variable ')")
         else
           write(50,"('set key at screen 0.555, 0.97 spacing 0.9 maxcols 1', &
         & ' samplen 1 horizontal textcolor rgb variable ')")
         endif             
       endif
     else
       if(igrtyp.eq.11) then
         write(50,"('set key at screen 0.585, 0.95 spacing 0.9', &
         & ' samplen 1 textcolor rgb variable ')")
       else
         if(s2gr) then
           write(50,"('set key at screen 0.565, 0.97 spacing 0.9', &
           & ' samplen 1 textcolor rgb variable ')")   
         else
           write(50,"('set key at screen 0.565, 0.97 spacing 0.8', &
           & ' samplen 1 textcolor rgb variable ')")            
         endif            
       endif
     endif
   endif
   write(50,"('set size 1.0, 1.0')")
   write(50,'(A,A,A,F5.3)') 'set label "',trim(title),'" at screen 0.13 ,',ytitle
   ipn=ipn-1
   cpn=''
   txt=''
   txt='set terminal '//trim(termtype)
! number the plot window 
   cfn='000'
   cpn=''
   if(ipn+1.lt.10) then
     write(cpn(1:1),'(I1)') ipn+1
     write(cfn(3:3),'(I1)') ipn+1
   elseif(ipn.lt.100) then
     write(cpn(1:2),'(I2)') ipn+1
     write(cfn(2:3),'(I2)') ipn+1
   else
     write(cpn(1:3),'(I3)') ipn+1
     write(cfn(1:3),'(I3)') ipn+1
   endif   
!   write(cpn,'(I3.3)') ipn+1
   outtxt=''
   outtxt="set output '"//trim(ppath)//"dynplot"//cfn//"."//trim(termtype)//"'"
   if(iopsy.eq.1) then
! LINUX
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     endif
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
       ytitle=0.995
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
       ytitle=0.985
     endif
   else
! WINDOWS
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.52'
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     endif
   endif
   write(50,"('set multiplot')")
! x-xp
   write(50,"('set size 0.5,0.5')")

   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.,0.49')")
   else
     write(50,"('set origin 0.,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(1)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(2)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(1),xmax(1)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(1),ymax(1)
   IF(igrtyp.eq.1) then
     IF (isave.eq.0) then
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.le.3) then
         if(iopsy.eq.2) then
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         else
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 1:2 title "" with ', &
               'dots lc 7, ',backslash
       else
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 1:2 title "" with ', &
               'dots lc 0, ',backslash
       endif
!       write(6,*) "DBX substr pre=",trim(fwpath)
       j=index(fwpath, '.plt')
       fwpath(j:j+3)='.cnt'
!       write(6,*) "DBX substr pos=",trim(fwpath)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 1:2 title '' with lines"
       write(50,'(A)') trim(myfrmt)
     ELSE
       filenm(18:21)='.plt'
       write(50,'(A,A21,A,A1)') 'plot "',filenm(1:21), &
          '" using 1:2 title "" with dots lc 0, ',backslash
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 1:2 title "" with lines'
     ENDIF
   ELSE
     IF (isave.eq.0) then
       toc=cccst(1)
       indxx=trim(toc)
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
!         write(6,*) "DBX wfile20 af mcs fwpath=",trim(fwpath)
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:2 title '"//indxx//"' with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A5,A,A1)') 'plot "',pfnm(1),'" using 1:2 title "',indxx, &
               '" with dots lc 1, ',backslash
       endif
       do j=2,mcstat
         strng=''
         write(strng,'(I2)') j
         if(j.eq.mcstat .and. igrtyp.eq.11) then
           toc=cccst(j-1)
           indxx=trim(toc)
           if(iopsy.le.3) then
             fwpath=''
             fwpath=trim(pfnm(j))
!             write(6,*) "DBX wfile20 mcs loop fwpath=",j,trim(fwpath)
             myfrmt=''
             myfrmt="     '"//trim(fwpath)//"' using 1:2 title ' >"//indxx//"' with dots lc "//trim(strng)//", "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else           
             write(50,'(A,A11,A,A5,A,I2,A,A1)') '     "',pfnm(j),'" using 1:2 title " >',indxx, &
               '" with dots lc ',j,',',backslash
           endif
         else           
           toc=cccst(j)
           indxx=trim(toc)
           if(iopsy.le.3) then
             fwpath=''
             fwpath=trim(pfnm(j))
             myfrmt=''
             myfrmt="     '"//trim(fwpath)//"' using 1:2 title '"//indxx//"' with dots lc "//trim(strng)//", "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else           
             write(50,'(A,A11,A,A5,A,I2,A,A1)') '     "',pfnm(j),'" using 1:2 title "',indxx, &
               '" with dots lc ',j,',',backslash
           endif
         endif
       enddo
       if(iopsy.le.3) then
         fwpath=trim(ppath)
         fwpath=trim(fwpath)//'dynac.cnt'
!         write(6,*) "DBX wfile20 CNT fwpath=",trim(fwpath)
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 1:2 title '' with lines"
         write(50,'(A)') trim(myfrmt)
       else           
         write(50,'(A)') '     "dynac.cnt" using 1:2 title "" with lines'
       endif            
     ELSE
       strng=pfnm(1)
       toc=cccst(1)
       indxx=trim(toc)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A4,A,A1)') 'plot "',filenm,'" using 1:2 title "',indxx, &
               '" with dots lc 1, ',backslash
       do j=2,mcstat
         strng=pfnm(j)
         filenm(18:23)=strng(6:11)
         if(j.eq.mcstat .and. igrtyp.eq.11) then
           toc=cccst(j-1)
           indxx=trim(toc)
           write(50,'(A,A23,A,A4,A,I2,A,A1)') '     "',filenm,'" using 1:2 title " >',indxx, &
               '" with dots lc ',j,',',backslash
         else
           toc=cccst(j)
           indxx=trim(toc)
           write(50,'(A,A23,A,A4,A,I2,A,A1)') '     "',filenm,'" using 1:2 title "',indxx, &
               '" with dots lc ',j,',',backslash
         endif
       enddo
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 1:2 title "" with lines'
     ENDIF
   ENDIF
   write(50,"('unset key')")
   write(50,"('unset label')")
! y-yp
   write(50,"('set size 0.5,0.5')")
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.5,0.49')")
   else
     write(50,"('set origin 0.5,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(3)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(4)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(2),xmax(2)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(2),ymax(2)
   IF(igrtyp.eq.1) then
     IF (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(ppath)//'dynac.plt'
         if(iopsy.eq.2) then
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         else
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 3:4 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 3:4 with', &
               ' dots lc 7, ',backslash
       else
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 3:4 with', &
               ' dots lc 0, ',backslash
       endif
!       write(6,*) "DBX2 substr pre=",trim(fwpath)
       j=index(fwpath, '.plt')
       fwpath(j:j+3)='.cnt'
!       write(6,*) "DBX2 substr pos=",trim(fwpath)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 3:4 title '' with lines"
       write(50,'(A)') trim(myfrmt)
     ELSE
       filenm(18:21)='.plt'
       write(50,'(A,A21,A,A,A1)') 'plot "',filenm(1:21),'" using 3:4 with', &
               ' dots lc 0, ',backslash
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 3:4 with lines'
     ENDIF
   ELSE
     IF (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 3:4 with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A,A1)') 'plot "',pfnm(1),'" using 3:4 with', &
               ' dots lc 1, ',backslash
       endif
       do j=2,mcstat
         if(iopsy.le.3) then
           strng=''
           write(strng,'(I2)') j
           fwpath=''
           fwpath=trim(pfnm(j))
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 3:4 with dots lc "//trim(strng)//", "
           write(50,'(A,A1)') trim(myfrmt),backslash
         else           
           write(50,'(A,A11,A,I2,A,A1)') '     "',pfnm(j),'" using 3:4 with', &
               ' dots lc ',j,',',backslash
         endif
       enddo
       if(iopsy.le.3) then
         fwpath=''
!         fwpath=trim(ppath)
         fwpath=trim(ppath)//'dynac.cnt'
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 3:4 with lines"
         write(50,'(A)') trim(myfrmt)
       else           
         write(50,'(A)') '     "dynac.cnt" using 3:4 with lines'
       endif            
     ELSE
       strng=pfnm(1)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,A1)') 'plot "',filenm,'" using 3:4 with', &
               ' dots lc 1, ',backslash
       do j=2,mcstat
         strng=pfnm(j)
         filenm(18:23)=strng(6:11)
         write(50,'(A,A23,A,A,I2,A,A1)') '     "',filenm,'" using 3:4 with', &
               ' dots lc ',j,',',backslash
       enddo
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 3:4 with lines'
     ENDIF
   ENDIF
! x-y
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(5)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(6)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(3),xmax(3)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(3),ymax(3)
   IF(igrtyp.eq.1) then
     IF (isave.eq.0) then
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.le.3) then
         if(iopsy.eq.2) then
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:3 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:3 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         else
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 1:3 title '' with dots lc 8, "
             write(50,'(A)') trim(myfrmt)
           else
             myfrmt="plot '"//trim(fwpath)//"' using 1:3 title '' with dots lc 0, "
             write(50,'(A)') trim(myfrmt)
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A)') 'plot "dynac.plt" using 1:3 with dots lc 7'
       else
         write(50,'(A)') 'plot "dynac.plt" using 1:3 with dots lc 0'
       endif
     ELSE
       filenm(18:21)='.plt'
       write(50,'(A,A21,A)') 'plot "',filenm(1:21),'" using 1:3 with dots lc 0'
     ENDIF
   ELSE
     IF (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 1:3 with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A,A1)') 'plot "',pfnm(1),'" using 1:3', &
               ' with dots lc 1, ',backslash
       endif
       do j=2,mcstat-1
         if(iopsy.le.3) then
           strng=''
           write(strng,'(I2)') j
           fwpath=''
           fwpath=trim(pfnm(j))
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 1:3 with dots lc "//trim(strng)//", "
           write(50,'(A,A1)') trim(myfrmt),backslash
         else           
           write(50,'(A,A11,A,A,I2,A,A1)') '     "',pfnm(j),'" using 1:3', &
               ' with dots lc ',j,',',backslash
         endif
       enddo
       if(iopsy.le.3) then
         strng=''
         write(strng,'(I2)') mcstat
         fwpath=''
         fwpath=trim(pfnm(mcstat))
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 1:3 with dots lc "//trim(strng)
         write(50,'(A)') trim(myfrmt)
       else           
         write(50,'(A,A11,A,A,I2)') '     "',pfnm(mcstat),'" using 1:3', &
               ' with dots lc ',mcstat
       endif
     ELSE
       strng=pfnm(1)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,A1)') 'plot "',filenm,'" using 1:3', &
               ' with dots lc 1, ',backslash
       do j=2,mcstat-1
         strng=pfnm(j)
         filenm(18:23)=strng(6:11)
         write(50,'(A,A23,A,A,I2,A,A1)') '     "',filenm,'" using 1:3', &
               ' with dots lc ',j,',',backslash
       enddo
       strng=pfnm(mcstat)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,I2)') '     "',filenm,'" using 1:3', &
               ' with dots lc ',mcstat
     ENDIF
   ENDIF
! dW-dPHI
   write(50,"('set size 0.5,0.5')")
   write(50,"('set origin 0.5,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(7)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(8)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(4),xmax(4)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(4),ymax(4)
   IF(igrtyp.eq.1) then
     IF (isave.eq.0) then
       fwpath=''
       fwpath=trim(ppath)//'dynac.plt'
       if(iopsy.le.3) then
         if(iopsy.eq.2) then
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 5:6 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 5:6 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         else
           myfrmt=''
           if(termtype.eq.'qt' .or. s2gr) then
             myfrmt="plot '"//trim(fwpath)//"' using 5:6 title '' with dots lc 8, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           else
             myfrmt="plot '"//trim(fwpath)//"' using 5:6 title '' with dots lc 0, "
             write(50,'(A,A1)') trim(myfrmt),backslash
           endif
         endif
       elseif(iopsy.eq.1 .and. termtype.eq.'qt') then
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 5:6 with', &
               ' dots lc 7, ',backslash
       else
         write(50,'(A,A,A1)') 'plot "dynac.plt" using 5:6 with', &
               ' dots lc 0, ',backslash
       endif
!       write(6,*) "DBX3 substr pre=",trim(fwpath)
       j=index(fwpath, '.plt')
       fwpath(j:j+3)='.cnt'
!       write(6,*) "DBX3 substr pos=",trim(fwpath)
       myfrmt=''
       myfrmt="     '"//trim(fwpath)//"' using 5:6 with lines"
       write(50,'(A)') trim(myfrmt)
     ELSE
       filenm(18:21)='.plt'
       write(50,'(A,A21,A,A,A1)') 'plot "',filenm(1:21),'" using 5:6 with', &
               ' dots lc 0, ',backslash
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 5:6 with lines'
     ENDIF
   ELSE
     IF (isave.eq.0) then
       if(iopsy.le.3) then
         fwpath=''
         fwpath=trim(pfnm(1))
         myfrmt=''
         myfrmt="plot '"//trim(fwpath)//"' using 5:6 with dots lc 1, "
         write(50,'(A,A1)') trim(myfrmt),backslash
       else           
         write(50,'(A,A11,A,A,A1)') 'plot "',pfnm(1),'" using 5:6 with', &
               ' dots lc 1, ',backslash
       endif
       do j=2,mcstat
         if(iopsy.le.3) then
           strng=''
           write(strng,'(I2)') j
           fwpath=''
           fwpath=trim(pfnm(j))
           myfrmt=''
           myfrmt="     '"//trim(fwpath)//"' using 5:6 with dots lc "//trim(strng)//", "
           write(50,'(A,A1)') trim(myfrmt),backslash
         else           
           write(50,'(A,A11,A,A,I2,A,A1)') '     "',pfnm(j),'" using 5:6 with', &
               ' dots lc ',j,',',backslash
         endif
       enddo
       if(iopsy.le.3) then
         fwpath=trim(ppath)
         fwpath=trim(fwpath)//'dynac.cnt'
         myfrmt=''
         myfrmt="     '"//trim(fwpath)//"' using 5:6 with lines"
         write(50,'(A)') trim(myfrmt)
       else           
         write(50,'(A)') '     "dynac.cnt" using 5:6 with lines'
       endif            
     ELSE
       strng=pfnm(1)
       filenm(18:23)=strng(6:11)
       write(50,'(A,A23,A,A,A1)') 'plot "',filenm,'" using 5:6 with', &
               ' dots lc 1, ',backslash
       do j=2,mcstat
         strng=pfnm(j)
         filenm(18:23)=strng(6:11)
         write(50,'(A,A23,A,A,I2,A,A1)') '     "',filenm,'" using 5:6 with', &
               ' dots lc ',j,',',backslash
       enddo
       filenm(18:21)='.cnt'
       write(50,'(A,A21,A)') '     "',filenm(1:21),'" using 5:6 with lines'
     ENDIF
   ENDIF
   write(50,"('unset multiplot')")
   if(.not. s2gr) then
     if(.not. dgui) write(50,'(A)')'pause -1 "hit return to continue"'
   endif
   close (50)
   END SUBROUTINE wfile20
!> *******************************************************************
!! SUBROUTINE wfile120
!! xx'-yy'-xy-zz' 2D plot
!< *******************************************************************
   SUBROUTINE wfile120(isave,ipn)
   USE m4wfiles
   USE mrouti1, ONLY: dgui,imax
   USE m4files
   USE DynacConstants, ONLY: backslash,cygwin
   IMPLICIT NONE
   character(len=256) :: command,lfname
   character(len=256) :: fwpath,myfrmt
   character(len=255) :: txt,outtxt
   character(len=50), dimension(3) :: cols
   character(len=33) :: paf
   character(len=10) :: sc
   character(len=8) :: hm,vm,ho,vo,hr,vr
   character(len=8) :: parcnt
   character(len=3) :: cpn,cfn 
   INTEGER isave,ipn
   REAL(8) ytitle
!*******************************************************************
   command=''
   lfname=''
   fwpath=''
   fwpath=trim(ppath)//'dynac.gnu'
   write(parcnt,'(I8)') imax
   write(6,"(i8,' particles total')") imax
   ytitle=0.985
   if(iopsy.eq.1) then
! LINUX
     command='rm -f '//trim(fwpath)
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     command='rm -f '//trim(fwpath)
     if(dgui) then
       ytitle=0.985
     elseif(s2gr) then
       ytitle=0.98
     else
       ytitle=0.992
     endif
   else
! WINDOWS
!     i=len_trim(ppath)
     if(cygwin) then
       command='rm -f '//trim(fwpath)
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
!  write(6,*) "DBX in wfile120 CMD1=",trim(command)   
   call EXECUTE_COMMAND_LINE(trim(COMMAND), wait=.true.)
   IF (isave.eq.0) then
     OPEN(unit=50,file=trim(fwpath))          
   ELSE
     call fn
     filenm(1:2)='s1'
     filenm(18:21)='.gnu'
     paf(1:10)='savedplots'
     if(iopsy.eq.1) then
! LINUX
       paf(11:11)="/"
     elseif(iopsy.eq.3) then
! MAC
       paf(11:11)="/"
     else
! WINDOWS
       paf(11:11)=backslash
     endif
     paf(12:32)=filenm(1:21)
     OPEN(unit=50,file=paf(1:32))
   ENDIF
   write(50,"('unset key')")
   write(50,"('set size 1.0, 1.0')")
   write(50,'(A,A,A,F5.3)') 'set label "',trim(title),'" at screen 0.13 ,',ytitle
   ipn=ipn-1
   cpn='   '
   txt=''
   txt='set terminal '//trim(termtype)
! number the plot window 
   cfn='000'
   cpn=''
   if(ipn+1.lt.10) then
     write(cpn(1:1),'(I1)') ipn+1
     write(cfn(3:3),'(I1)') ipn+1
   elseif(ipn.lt.100) then
     write(cpn(1:2),'(I2)') ipn+1
     write(cfn(2:3),'(I2)') ipn+1
   else
     write(cpn(1:3),'(I3)') ipn+1
     write(cfn(1:3),'(I3)') ipn+1
   endif   
!   write(cpn,'(I3.3)') ipn+1
   outtxt=''
   outtxt="set output '"//trim(ppath)//"dynplot"//cfn//"."//trim(termtype)//"'"
   if(iopsy.eq.1) then
! LINUX
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.44,0.51'
     txt='set terminal '//trim(termtype)
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
     endif
     ytitle=0.985
   elseif(iopsy.eq.3) then
! MAC
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.51'
     txt(1:13)='set terminal '//trim(termtype)
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
       ytitle=0.995
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 750,625'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 750,625'
         write(50,'(A)') trim(txt)
       endif
       ytitle=0.985
     endif
   else
! WINDOWS
     write(50,'(A,A8,A)') 'set label "',parcnt,' particles" at screen 0.45,0.52'
     txt(1:13)='set terminal '//trim(termtype)
     if(dgui) then
       if(s2gr) then
! then number the plot window 
         txt=trim(txt)//' '//cpn//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else
! then number the plot window and let it persist
         txt=trim(txt)//' '//cpn//' persist title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     else
       if(s2gr) then
! then number the plot window
         txt=trim(txt)//' size 817,768'
         write(50,'(A)') trim(txt)
         write(50,'(A)') trim(outtxt)
       else  
         txt=trim(txt)//' title "DYNAC" size 817,768'
         write(50,'(A)') trim(txt)
       endif
     endif
   endif
   write(50,"('set multiplot')")
! x-xp
   write(50,"('set size 0.495,0.55')")

   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.015,0.49')")
   else
     write(50,"('set origin 0.,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(1)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(2)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(1),xmax(1)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(1),ymax(1)
   write(50,"('set dgrid3d 20,20')")
   write(50,"('set pm3d map interpolate 0,0')")
   write(50,'(A,A,A)') 'set palette defined ( 0 "white", 1 "pink", ', &
                       '2 "purple", 3  "blue", 4 "green", 5 "yellow",', &
                       '6 "orange", 7 "red", 8 "black" )'   
! splot 'dynac.plt' u (xmul*($1-10.5)/20.):(xpmul*($2-10.5)/20.):(100*$3/fmax)
   hm=''
   vm=''
   ho=''
   vo=''
   hr=''
   vr=''
   sc=''
   write(hm,'(F8.3)') bex(2)-bex(1)
   write(vm,'(F8.3)') bex(4)-bex(3)
   write(ho,'(F8.3)') float(ndx+1)/2.
   write(vo,'(F8.3)') float(ndy+1)/2.
   write(hr,'(F8.3)') float(ndx)
   write(vr,'(F8.3)') float(ndy)
   write(sc,'(F10.2)') xxpmax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$3/'//sc//')'
   IF (isave.eq.0) then
     fwpath=''
     fwpath=trim(ppath)//'dynac.plt'
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
   ELSE
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   ENDIF
   write(50,"('unset key')")
   write(50,"('unset label')")
! y-yp
   write(50,"('set size 0.495,0.55')")
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.5,0.49')")
   else
     write(50,"('set origin 0.5,0.5')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(3)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(4)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(2),xmax(2)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(2),ymax(2)
   hm=''
   vm=''
   sc=''
   write(hm,'(F8.3)') bex(6)-bex(5)
   write(vm,'(F8.3)') bex(8)-bex(7)
   write(sc,'(F10.2)') yypmax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$4/'//sc//')'
   IF (isave.eq.0) then
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
   ELSE
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   ENDIF
! x-y
   write(50,"('set size 0.495,0.55')")
   write(50,"('set origin 0.015,0.')")
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(5)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(6)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(3),xmax(3)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(3),ymax(3)
   hm=''
   vm=''
   sc=''
   write(hm,'(F8.3)') bex(10)-bex(9)
   write(vm,'(F8.3)') bex(12)-bex(11)
   write(sc,'(F10.2)') xymax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$5/'//sc//')'
   IF (isave.eq.0) then
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
   ELSE
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   ENDIF
! dW-dPHI
   write(50,"('set size 0.495,0.55')")
   if(iopsy.eq.1) then
! LINUX
     write(50,"('set origin 0.5,0.')")
   else
     write(50,"('set origin 0.5,0.')")
   endif
   write(50,'(A,A,A)') 'set xlabel "',trim(labels(7)),'"'
   write(50,'(A,A,A)') 'set ylabel "',trim(labels(8)),'"'
   write(50,"('set xrange [',f8.2,':',f8.2,']')") xmin(4),xmax(4)
   write(50,"('set yrange [',f12.5,':',f12.5,']')") ymin(4),ymax(4)
   hm=''
   vm=''
   sc=''
   write(hm,'(F8.3)') bex(14)-bex(13)
   write(vm,'(F8.3)') bex(16)-bex(15)
   write(sc,'(F10.2)') zzpmax
   cols(1)='('//hm//'*($1-'//ho//')/'//hr//')'
   cols(2)='('//vm//'*($2-'//vo//')/'//vr//')'
   cols(3)='(100.*$6/'//sc//')'
   IF (isave.eq.0) then
     myfrmt=''
     myfrmt="splot '"//trim(fwpath)//"' u "//trim(cols(1))//':'//trim(cols(2))//':'//trim(cols(3))
     write(50,'(A)') trim(myfrmt)
   ELSE
     filenm(18:21)='.plt'
     write(50,'(A,A21,A,A,A,A,A,A)') 'splot "',filenm(1:21),'" u ',trim(cols(1)),':', &
               trim(cols(2)),':',trim(cols(3))
   ENDIF
   write(50,"('unset multiplot')")
   if(.not. s2gr) then
     if(.not. dgui) write(50,'(A)') 'pause -1 "hit return to continue"'
   endif  
   close (50)
   END SUBROUTINE wfile120
!> *******************************************************************
!! SUBROUTINE mytime
!! get system time and convert it to an ascii string
!< *******************************************************************
SUBROUTINE mytime(iitime)
   IMPLICIT NONE
   character(len=30) :: iitime
   integer :: dt(8),j,k
   integer weekday,month,year
   character(len=3), parameter :: DAYS(7) = [ 'Sun', 'Mon', 'Thu', 'Wed', 'Thu', 'Fri', 'Sat' ]
   character(len=3), parameter :: MONTHS(12) = &
    [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
!*******************************************************************
   call date_and_time(values=dt)
   year  = dt(1)
   month = dt(2)
   if (month <= 2) then
     month = month + 12
     year  = year - 1
   end if
   j = year / 100
   k = mod(year, 100)
   weekday = mod(dt(3) + ((month + 1) * 26) / 10 + k + k / 4 + j / 4 + 5 * j, 7) -1
   if (weekday < 0) weekday = 6
   write (iitime, '(a,1x,a,1x,i0.2,1x,i0.2,":",i0.2,":",i0.2,1x,i4)')DAYS(weekday+1), &
              MONTHS(dt(2)),dt(3),  dt(5), dt(6), dt(7),dt(1)             
END SUBROUTINE mytime   
!> *******************************************************************
!! SUBROUTINE fn
!!
!< *******************************************************************
   SUBROUTINE fn
   USE m4wfiles, ONLY: filenm
   USE mrouti2, ONLY: mg
   IMPLICIT NONE
   character(len=30) :: iitime
!*******************************************************************
!   integer(8) inttim
!   inttim=time8()
!   iitime=ctime(inttim)
   call mytime(iitime)
   if (mg) then
! using MINGW style gfortran 03/30/10 20:51:06 (10 is 2010)
     if(iitime(1:2).eq.'01')filenm(3:5)='Jan'
     if(iitime(1:2).eq.'02')filenm(3:5)='Feb'
     if(iitime(1:2).eq.'03')filenm(3:5)='Mar'
     if(iitime(1:2).eq.'04')filenm(3:5)='Apr'
     if(iitime(1:2).eq.'05')filenm(3:5)='May'
     if(iitime(1:2).eq.'06')filenm(3:5)='Jun'
     if(iitime(1:2).eq.'07')filenm(3:5)='Jul'
     if(iitime(1:2).eq.'08')filenm(3:5)='Aug'
     if(iitime(1:2).eq.'09')filenm(3:5)='Sep'
     if(iitime(1:2).eq.'10')filenm(3:5)='Oct'
     if(iitime(1:2).eq.'11')filenm(3:5)='Nov'
     if(iitime(1:2).eq.'12')filenm(3:5)='Dec'
     filenm(6:7)=iitime(4:5)
     filenm(8:9)='20'
     filenm(10:11)=iitime(7:8)
     filenm(12:13)=iitime(10:11)
     filenm(14:15)=iitime(13:14)
     filenm(16:17)=iitime(16:17)
   else
! using standard gfortran Tue Mar 30 20:51:06 2010
     filenm(3:5)=iitime(5:7)
     filenm(6:7)=iitime(9:10)
     filenm(8:11)=iitime(21:24)
     filenm(12:13)=iitime(12:13)
     filenm(14:15)=iitime(15:16)
     filenm(16:17)=iitime(18:19)
   endif
! on a MAC 02 Apr is shown as 2 Apr (on windows as 02 Apr)
! fill the blank with the character '0' to avoid error message on file copy
   if(filenm(6:6).eq.' ') filenm(6:6)='0'
   END SUBROUTINE fn
!> *******************************************************************
!! SUBROUTINE mkfrmt(i,fmt)
!! this routine makes a (variable) A format
!! e.g. if the integer i=11, the character format fmt will
!! be fmt=(A11)
!< *******************************************************************
   SUBROUTINE mkfrmt(i,fmt)
   IMPLICIT NONE
   character(len=6) :: fmt
   INTEGER i,j,j1,j2,j3
!*******************************************************************
   fmt(1:1)='('
   fmt(2:2)='A'
   fmt(3:6)=''
   if (i.lt.10) then
     fmt(3:3)=char(i+48)
     fmt(4:4)=')'
   elseif (i.lt.100) then
     j1=i/10
     j2=i-j1*10
     fmt(3:3)=char(j1+48)
     fmt(4:4)=char(j2+48)
     fmt(5:5)=')'
   elseif (i.lt.1000) then
     j1=i/100
     j=i-j1*100
     j2=j/10
     j3=j-j2*10
     fmt(3:3)=char(j1+48)
     fmt(4:4)=char(j2+48)
     fmt(5:5)=char(j3+48)
     fmt(6:6)=')'
   endif
   END SUBROUTINE mkfrmt
!> *******************************************************************
!! SUBROUTINE savefile
!! 
!!
!< *******************************************************************
   SUBROUTINE savefile
   USE DynacConstants, ONLY: iptsz
   USE m4wfiles, ONLY: iopsy,filenm,pfnm
   USE m4cstates
   USE mrouti1
   USE m4files
   USE DynacConstants, ONLY: backslash
   IMPLICIT NONE
   character(len=256) :: command
   character(len=132) :: ras
   character(len=255) :: strng
   character(len=6) :: fmt
   character(len=1) :: fsave
   INTEGER isave,j,k,nplot,ios        
!*******************************************************************
   if (.not. allocated(cst))  allocate(cst(iptsz))
! plot number only used in conjunction with dgui, not with plotit call from terminal
! dummy value here
   nplot=0
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     write(6,'(a)',ADVANCE='NO')'Save plot file (y/n/p(rint)/e(xit)/q(uit)/<cr>=n)? '
   else
! WINDOWS
     write(6,'(a)',ADVANCE='NO')'Save plot file (y/n/e(xit)/q(uit)/<cr>=n)? '
   endif
   read(5,'(A)',ADVANCE='YES') fsave
   fsave=fsave(1:1)
   if (fsave.eq.' ' .or. fsave.eq.'n' .or. fsave.eq.'N')then
     write(6,*) ' No files saved'
   elseif (fsave.eq.'e' .or. fsave.eq.'E' .or. &
           fsave.eq.'q' .or. fsave.eq.'Q') then
     stop
   elseif (fsave.eq.'p' .or. fsave.eq.'P') then
! currently for linux and MAC only
     if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
       OPEN(unit=50,file='dynac.gnu')
       OPEN(unit=51,file='dynacp.gnu')
       write(51,'(a)') 'set output "dynac.ps"'
       write(51,'(a)') 'set term postscript color'
       DO
         read(50,'(a)',iostat=ios) ras 
         if( ios < 0 ) exit ! end of file is reached
         if (ras(1:5).ne.'pause') then
           k=len_trim(ras)
           call mkfrmt(k,fmt)
           write(51,fmt) ras(1:k)
         endif
       ENDDO
       close(50)
       close(51)
       command(1:18)="gnuplot dynacp.gnu"
       call EXECUTE_COMMAND_LINE(COMMAND(1:18),wait=.true.)
       command(1:13)="lpr dynac.ps"
       call EXECUTE_COMMAND_LINE(COMMAND(1:13),wait=.true.)
     endif
   elseif (fsave.eq.'y' .or. fsave.eq.'Y') then
! filename format: sXMmmDDYYYYHHMMSSaa.eee (see user guide)
     isave=1
     IF (igrtyp.eq.1 .or. igrtyp.eq.6 .or. igrtyp.eq.11) THEN
! x-xp', y-xp', x-y, z-zp' plots
       call wfile20(isave,nplot)
       if(igrtyp.eq.1 .or. igrtyp.eq.16) then
         filenm(18:21)='.plt'
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           command(1:24)="cp dynac.plt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
           filenm(18:21)='.cnt'
           command(1:24)="cp dynac.cnt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
         else
! WINDOWS
           command(1:25)="copy dynac.plt savedplots"
           command(26:26)=backslash
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
           filenm(18:21)='.cnt'
           command(1:25)="copy dynac.cnt savedplots"
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
         endif
       else
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:3)="cp "
             command(4:14)=pfnm(j)
             command(15:26)=' savedplots/'
             command(27:49)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
           enddo
           filenm(18:21)='.cnt'
           command(1:24)="cp dynac.cnt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
         else
! WINDOWS
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:5)="copy "
             command(6:16)=pfnm(j)
             command(17:27)=' savedplots'
             command(28:28)=backslash
             command(29:51)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
           enddo
           filenm(18:21)='.cnt'
           command(1:25)="copy dynac.cnt savedplots"
           command(26:26)=backslash
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
         endif
       endif
     ENDIF
     IF (igrtyp.eq.2 .or. igrtyp.eq.7 .or. igrtyp.eq.12) THEN
! z-x, z-y plots
       call wfile21(isave,nplot)
       if(igrtyp.eq.2) then
         filenm(18:21)='.plt'
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           command(1:24)="cp dynac.plt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
         else
! WINDOWS
           command(1:25)="copy dynac.plt savedplots"
           command(26:26)=backslash
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
         endif
       else
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:3)="cp "
             command(4:14)=pfnm(j)
             command(15:26)=' savedplots/'
             command(27:49)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
           enddo
         else
! WINDOWS
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:5)="copy "
             command(6:16)=pfnm(j)
             command(17:27)=' savedplots'
             command(28:28)=backslash
             command(29:51)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
           enddo
         endif
       endif
! profiles
       filenm(20:23)='.pro'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:26)="cp dynac01.pro savedplots/"
         filenm(18:19)='01'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac02.pro savedplots/"
         filenm(18:19)='02'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac03.pro savedplots/"
         filenm(18:19)='03'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac04.pro savedplots/"
         filenm(18:19)='04'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac05.pro savedplots/"
         filenm(18:19)='05'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac06.pro savedplots/"
         filenm(18:19)='06'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
       else
! WINDOWS
! s2Jan14200420535101.pro
         command(1:27)="copy dynac01.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='01'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac02.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='02'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac03.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='03'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac04.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='04'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac05.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='05'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac06.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='06'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.3) THEN
! x,y envelopes as f(z)
       call wfile2(isave,2,nplot)
       filenm(18:21)='.plt'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:24)="cp dynac.plt savedplots/"
         command(25:45)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
       else
! WINDOWS
         command(1:25)="copy dynac.plt savedplots"
         command(26:26)=backslash
         command(27:47)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.4) THEN
! dW/W envelope as f(z)
       call wfile2(isave,3,nplot)
       filenm(18:21)='.plt'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:24)="cp dynac.plt savedplots/"
         command(25:45)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
       else
! WINDOWS
         command(1:25)="copy dynac.plt savedplots"
         command(26:26)=backslash
         command(27:47)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.5) THEN
! dPHI envelope as f(z)
       call wfile2(isave,4,nplot)
       filenm(18:21)='.plt'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:24)="cp dynac.plt savedplots/"
         command(25:45)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
       else
! WINDOWS
         command(1:25)="copy dynac.plt savedplots"
         command(26:26)=backslash
         command(27:47)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.16) THEN
! x-xp', y-xp', x-y, z-zp' density plots
       call wfile120(isave,nplot)
       if(igrtyp.eq.1 .or. igrtyp.eq.16) then
         filenm(18:21)='.plt'
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           command(1:24)="cp dynac.plt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
           filenm(18:21)='.cnt'
           command(1:24)="cp dynac.cnt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
         else
! WINDOWS
           command(1:25)="copy dynac.plt savedplots"
           command(26:26)=backslash
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
           filenm(18:21)='.cnt'
           command(1:25)="copy dynac.cnt savedplots"
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
         endif
       else
         if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:3)="cp "
             command(4:14)=pfnm(j)
             command(15:26)=' savedplots/'
             command(27:49)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
           enddo
           filenm(18:21)='.cnt'
           command(1:24)="cp dynac.cnt savedplots/"
           command(25:45)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
         else
! WINDOWS
           do j=1,mcstat
             strng=pfnm(j)
             filenm(18:23)=strng(6:11)
             command(1:5)="copy "
             command(6:16)=pfnm(j)
             command(17:27)=' savedplots'
             command(28:28)=backslash
             command(29:51)=filenm(1:23)
             call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
           enddo
           filenm(18:21)='.cnt'
           command(1:25)="copy dynac.cnt savedplots"
           command(26:26)=backslash
           command(27:47)=filenm(1:21)
           call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
         endif
       endif
     ENDIF
     IF (igrtyp.eq.18) THEN
! z-x, z-y density plots
       call wfile121(isave,nplot)
       filenm(18:21)='.plt'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:24)="cp dynac.plt savedplots/"
         command(25:45)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:45),wait=.true.)
       else
! WINDOWS
         command(1:25)="copy dynac.plt savedplots"
         command(26:26)=backslash
         command(27:47)=filenm(1:21)
         call EXECUTE_COMMAND_LINE(COMMAND(1:47),wait=.true.)
       endif
! profiles
       filenm(20:23)='.pro'
       if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
         command(1:26)="cp dynac01.pro savedplots/"
         filenm(18:19)='01'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac02.pro savedplots/"
         filenm(18:19)='02'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac03.pro savedplots/"
         filenm(18:19)='03'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac04.pro savedplots/"
         filenm(18:19)='04'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac05.pro savedplots/"
         filenm(18:19)='05'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
         command(1:26)="cp dynac06.pro savedplots/"
         filenm(18:19)='06'
         command(27:49)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:49),wait=.true.)
       else
! WINDOWS
! s2Jan14200420535101.pro
         command(1:27)="copy dynac01.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='01'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac02.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='02'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac03.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='03'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac04.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='04'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac05.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='05'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
         command(1:27)="copy dynac06.pro savedplots"
         command(28:28)=backslash
         filenm(18:19)='06'
         command(29:51)=filenm(1:23)
         call EXECUTE_COMMAND_LINE(COMMAND(1:51),wait=.true.)
       endif            
     ENDIF
     write(6,*) ' Saved ',filenm(1:17),' in savedplots directory'
     isave=0
   ENDIF
   END SUBROUTINE savefile
!> *******************************************************************
!! SUBROUTINE wfile110
!! Writes the histogrammed data which will be plotted by GNU to a file
!< *******************************************************************
   SUBROUTINE wfile110(ndx,ndy)
   USE DynacConstants, ONLY: cygwin
   USE m4wfiles, ONLY: iopsy,ppath
   USE mrouti2, ONLY: xxpar,yypar,xyar,zzpar
   IMPLICIT NONE
   character(len=256) :: fwpath
   character(len=280) :: command
   INTEGER i,j,ndx,ndy
!*******************************************************************
! store histogrammed data
   command=''
   fwpath=''
   fwpath=trim(ppath)//'dynac.plt'
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
!     ll=len_trim(ppath)
     if(cygwin) then
       command='rm -f '//trim(fwpath)
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
!   write(6,*) "DBX in wfile110 cmd=",command
   call EXECUTE_COMMAND_LINE(COMMAND,wait=.true.)
!   write(6,*) "DBX in wfile110 fwpath=",trim(fwpath)
   OPEN(unit=52,file=trim(fwpath))
   DO i=1,ndx
     DO j=1,ndy
       write(52,*) i,j,xxpar(i,j),yypar(i,j),xyar(i,j),zzpar(i,j)
     ENDDO
   ENDDO
   CLOSE(52)
   END SUBROUTINE wfile110
!> *******************************************************************
!! SUBROUTINE wfile111
!! Writes the Z-X and Z-Y histogrammed data to a file
!< *******************************************************************
   SUBROUTINE wfile111(ndx,ndy)
   USE DynacConstants, ONLY: cygwin
   USE m4wfiles, ONLY: iopsy,ppath
   USE mrouti2, ONLY: zxar,zyar
   IMPLICIT NONE
   character(len=256) :: fwpath
   character(len=280) :: command
   INTEGER i,j,ndx,ndy
!*******************************************************************
! store histogrammed data
   command=''
   fwpath=''
   fwpath=trim(ppath)//'dynac.plt'
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
     command='rm -f '//trim(fwpath)
   else
! WINDOWS
     if(cygwin) then
       command='rm -f '//trim(fwpath)
     else
       command='if exist '//trim(fwpath)//' del '//trim(fwpath)
     endif
   endif
!   write(6,*) "DBX in wfile111 cmd=",trim(COMMAND)   
   call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
!   write(6,*) "DBX in wfile111 fwp=",trim(fwpath)   
   OPEN(unit=52,file=trim(fwpath))
   DO i=1,ndx
     DO j=1,ndy
       write(52,*) i,j,zxar(i,j),zyar(i,j)
     ENDDO
   ENDDO
   CLOSE(52)
   END SUBROUTINE wfile111
!*******************************************************************
   SUBROUTINE pipe_it(command,inp)
   IMPLICIT NONE
!   integer EXITSTAT, CMDSTAT
   integer IOSTAT, IO
!   logical WAIT
   character(len=255) :: COMMAND, inp, Instruction       
!   write(6,*)"DBX1 in pipe_it input arg=",trim(command)
   COMMAND=trim(command)//" >MyPipe; echo '\x04' >MyPipe"
!   write(6,*)"DBX2 in pipe_it input arg=",trim(command)
!   WAIT=.true.
!//remove named pipe (if exists)//
   call EXECUTE_COMMAND_LINE("rm -f MyPipe",wait=.true.)
!//Create a named pipe//
   call EXECUTE_COMMAND_LINE("mkfifo MyPipe",wait=.true.)
!//Open a connection to it//
   open(11,file="MyPipe",iostat=iostat)
!   write(6,*)'IOSTAT  =',iostat
!//Execute//
   call EXECUTE_COMMAND_LINE(COMMAND, WAIT=.true.)
!//Execute a normal reading loop//
   inp=''
   do
     read(11,*,iostat=io)inp
!     write(6,*)io,inp(1:LEN_TRIM(inp)),LEN_TRIM(inp)
     IF(IS_IOSTAT_END(IO)) then
       exit
     elseif(IS_IOSTAT_EOR(IO)) then
       exit
     elseif(LEN_TRIM(inp).gt.0) then
       exit
     else
       write(6,*)"DBX io: ",io
     endif  
   end do
!//remove named pipe//
   CALL EXECUTE_COMMAND_LINE(Instruction,wait=.true.)
!   write(6,'(a,a)')"DBX result: ",inp
   return
   END SUBROUTINE pipe_it   
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
!> *******************************************************************
!! PROGRAM dynplt
!! GNUplot based utility for visualizing DYNAC generated plots
!< *******************************************************************
   PROGRAM dynplt
   USE m4wfiles
   USE m4cstates
   USE mrouti1
   USE m4files
   USE m4files2
   USE DynacConstants
   USE mrouti2
!   USE DynacConstants, ONLY: backslash,iptsz
   IMPLICIT NONE
   character(len=256), dimension(10) :: myarg
   character(len=400) :: command
   character(len=256) :: inarg,txt
   character(len=40) :: vtext
   character(len=1) :: sepa
   character(len=1) :: quotes
!   REAL(8)  dx(iptsz),dxp(iptsz)
   REAL(8), allocatable ::  dx(:),dxp(:)   
   REAL(8)  data(10)
   REAL(8)  zstat(20)
   INTEGER larg(4)
   INTEGER i,j,k,ll,llpath,narg,imx,imxp,imy,imyp,imz,imzp,isave,istat        
   INTEGER lcmd,length,lfnam,lpm,nplot,ios
   character(len=256) res
!*******************************************************************
   if (.not. allocated(dx))  allocate(dx(iptsz))
   if (.not. allocated(dxp)) allocate(dxp(iptsz))
   if (.not. allocated(cst)) allocate(cst(iptsz))
   if (.not. allocated(cx))  allocate(cx(iptsz))
   if (.not. allocated(cxp)) allocate(cxp(iptsz))
   if (.not. allocated(cy))  allocate(cy(iptsz))
   if (.not. allocated(cyp)) allocate(cyp(iptsz))
   if (.not. allocated(cz))  allocate(cz(iptsz))
   if (.not. allocated(czp)) allocate(czp(iptsz))
   if (.not. allocated(ctrx1))  allocate(ctrx1(iptsz))
   if (.not. allocated(ctrx2))  allocate(ctrx2(iptsz))
   if (.not. allocated(ctrx3))  allocate(ctrx3(iptsz))
   if (.not. allocated(ctry1))  allocate(ctry1(iptsz))
   if (.not. allocated(ctry2))  allocate(ctry2(iptsz))
   if (.not. allocated(ctry3))  allocate(ctry3(iptsz))
!
! if mg=.true., use MINGW on windows, which has a different result for ctime function than
! standard gfortran
! default is mg=.false.
   mg=.false.
! if plotit is called by dgui, then create all plots in separate windows
   dgui=.false.
! if running on Windows, may be using cygwin. Default: cygwin=.false.   
   cygwin=.false.        
! s2gr will be set to .true. if the terminal type is png, jpeg or gif
   s2gr=.false.        
   ppath=''
   lpath=0
   llpath=0
   command=''
   fname=''
   termtype=''
   sepa=''
   narg=0
   vtext='PLOTIT V4R0 16-Dec-2025'
   DO
     call get_command_argument(narg, inarg, length, istat)
     larg(narg+1)=LEN_TRIM(inarg)
     if(larg(narg+1).eq.0) exit
     narg=narg+1
     myarg(narg)=TRIM(inarg)
   ENDDO
!   write(6,*) 'Lengths',larg(2),larg(3)
   iopsy=0
   do i=2,narg
     txt=myarg(i)
     if(txt(1:1).ne.'-') then
! the input argument is the type of operating system
! iopsy=1 --> LINUX   GNUPLOT version
       if(txt(1:1).eq.'L' .or. txt(1:1).eq.'l') iopsy=1
! iopsy=2 --> WINDOWS GNUPLOT version
       if(txt(1:1).eq.'W' .or. txt(1:1).eq.'w') then
         iopsy=2
         if(txt(2:3).eq.'MG' .or. txt(2:3).eq.'mg') mg=.true.
!        check if using cygwin
         COMMAND="uname -rs"
         CALL pipe_it(command,res)
         if(res(1:6).eq."CYGWIN") cygwin=.true.
       endif
! iopsy=3 --> MAC     GNUPLOT version
       if(txt(1:1).eq.'M' .or. txt(1:1).eq.'m') iopsy=3
     else
       if(txt(1:3).eq.'-tt') then
         termtype=''
         termtype(1:larg(i)-3)=txt(4:larg(i))
       endif
       if(txt(1:2).eq.'-p') then
         ppath(1:larg(i)-2)=txt(3:larg(i))
         lpm=LEN(ppath)
         do k=lpm,1,-1
           if(ppath(k:k).eq.'\' .or. ppath(k:k).eq.'/') then
             lpath=k
             sepa=ppath(k:k)
             exit
           endif
         enddo
         llpath=LEN_TRIM(ppath)
!         write(6,*) 'DBX arg -p=',llpath,ppath
       endif
       if(txt(1:3).eq.'-dg') then
         dgui=.true.
         termtype=''
         if(iopsy.eq.1) termtype='x11'
!         if(iopsy.eq.2) termtype='windows'
         if(iopsy.eq.2) termtype='qt'
         if(iopsy.eq.3) termtype='x11'
       endif
       if(txt(1:2).eq.'-h') then
!print out of help message, starting with PLOTIT version
         write(6,'(A)') vtext
         write(6,*)'Command format:'
         write(6,*)'dynplt [-h] X [-tt] [-p] [-dg]'
         write(6,*)'where X is the operating system, which ', &
                   'needs to be one of the following 3:'
         write(6,'(a)') '   L or l for LINUX'
         write(6,'(a)') '   M or m for MAC'
         write(6,'(a)') '   W or w for WINDOWS'
         write(6,*)'Optional arguments:'
         write(6,*)'-h will list the argument options (this list)'
         write(6,*)'-p can be used to specify the datafile path. ', &
                   'There should be no '
         write(6,*)'   space between -p and the path. This ', &
                   'option is used by the'
         write(6,*)'   DYNAC GUI.'
         write(6,*)'-tt can be used to specify the GNUPLOT ', &
                   'terminal type, which defaults to:'
         write(6,*)'   wxt for LINUX'
         write(6,*)'   wxt for MAC'
         write(6,*)'   wxt for WINDOWS'
         stop
       endif
       if(txt(1:2).eq.'-v') then
!print out of PLOTIT version
         write(6,'(A)') vtext
         stop
       endif            
     endif
   enddo
! iopsy=1 --> LINUX   GNUPLOT version
! iopsy=2 --> WINDOWS GNUPLOT version
! iopsy=3 --> MAC     GNUPLOT version
   write(6,'(A)') vtext
   if(iopsy.eq.1) then
     write(6,'(A)') 'PLOTIT for LINUX'
     if(LEN_TRIM(termtype).eq.0) then
       write(6,*)'GNUPLOT TERMINAL TYPE NOT DEFINED'
       termtype='wxt'
       write(6,*)'USING TERMINAL TYPE ',termtype
     else
       write(6,'(A,A)')'GNUPLOT TERMINAL TYPE ',termtype
     endif
   elseif(iopsy.eq.2) then
     write(6,'(A)') 'PLOTIT for WINDOWS'
     if(LEN_TRIM(termtype).eq.0) then
       write(6,*)'GNUPLOT TERMINAL TYPE NOT DEFINED'
       termtype='wxt'
       write(6,*)'USING TERMINAL TYPE ',termtype
     else
       write(6,'(A,A)')'GNUPLOT TERMINAL TYPE ',termtype
     endif
   elseif(iopsy.eq.3) then
     write(6,'(A)') 'PLOTIT for MAC'
     if(LEN_TRIM(termtype).eq.0) then
       write(6,*)'GNUPLOT TERMINAL TYPE NOT DEFINED'
       termtype='wxt'
       write(6,*)'USING TERMINAL TYPE ',termtype
     else
       write(6,'(A,A)')'GNUPLOT TERMINAL TYPE ',termtype
     endif
   else
! iopsy=0 --> ERROR: system not found
     write(6,'(a)') 'Error in operating system type entry'
     write(6,'(a)') 'Operating system type required'
     write(6,'(a)') '  for LINUX   GNUPLOT use L or l'
     write(6,'(a)') '  for MAC     GNUPLOT use M or m'
     write(6,'(a)') '  for WINDOWS GNUPLOT use W or w'
     write(6,'(a)') 'Type'
     write(6,'(a)') 'plotit -h'
     write(6,'(a)') 'for help.'
     stop
   endif
   s2gr=.false.
   if(trim(termtype).eq.'gif'  .or. trim(termtype).eq.'GIF' .or. &
      trim(termtype).eq.'png'  .or. trim(termtype).eq.'PNG' .or. &
      trim(termtype).eq.'jpeg' .or. trim(termtype).eq.'JPEG')  s2gr=.true.
   if(lpath.ne.0) then
!     write(6,*) 'DBX in MAIN ppath=',ppath   
!     write(6,*) 'DBX PlotpathL=',llpath,ppath(1:llpath)
     if(iopsy.ne.2) then
       if(ppath(llpath:llpath).eq.'"') llpath=llpath-1
       if(ppath(llpath:llpath).eq.'/' .or.  &
          ppath(llpath:llpath).eq.backslash) then
         fname=ppath(1:llpath)
       else
         llpath=llpath+1
         ppath(llpath:llpath)=sepa
         fname=ppath(1:llpath)
       endif
       lpath=llpath
!       write(6,*) 'PlotpathS=',llpath,ppath(1:llpath)
     else
! Windows
!       write(6,*) 'DBX PlotpathW=',llpath,ppath(1:llpath)
       if(cygwin) then
         fname=ppath(1:llpath)
         if(ppath(llpath:llpath).eq.'"') then
           ppath(llpath:llpath)=backslash
           fname=ppath(1:llpath)
!           write(6,*) 'DBX PlotpathW2=',llpath,ppath(1:llpath)
         endif
         lpath=llpath
       else
         if(ppath(llpath:llpath).eq.'"' .and. ppath(llpath-1:llpath-1).eq."\") then
!         ppath(llpath:llpath)=backslash										
           fname=''
           fname=ppath(1:llpath-1)
!           write(6,*) 'DBX W2=',ppath(llpath-1:llpath-1),ppath(llpath:llpath)
!           write(6,*) 'DBX PlotpathW2=',llpath,ppath(1:llpath)
           lpath=llpath-1
         else
           fname=ppath(1:llpath)
         endif
       endif
     endif
   else
     ppath=''
   endif
!   write(6,*) 'DBX main fname=',trim(fname)
   write(6,*)
! igrtyp is type of graph (there is no igrtyp=8,9,10,13,14,15,20,21,23,24,25,26)
! single charge state, no zones:
!        igrtyp=1  for xx'-yy'-xy-zz' plots   (EMITGR)
!        igrtyp=2  for zx-zy plots & profiles (PROFGR)
!        igrtyp=3  for xz-yz envelopes        (ENVEL)
!        igrtyp=4  for dW envelope            (ENVEL)
!        igrtyp=5  for dPHI envelope          (ENVEL)
! multi charge state, no zones:
!        igrtyp=6  for xx'-yy'-xy-zz' plots for multi-charge state beam
!        igrtyp=7  for zx-zy plots & profiles for multi-charge state beam
!
! with zones, single charge state:
!        igrtyp=11 for xx'-yy'-xy-zz' plots with ZONES card   (EMITGR)
!        igrtyp=12 for zx-zy plots & profiles with ZONES card (PROFGR)
!
!        igrtyp=16 for xx'-yy'-xy-zz' density plots           (EMITGRD)
!        igrtyp=18 for zx-zy density plots & profiles         (PROFGRD)
!
!        igrtyp=17 or 19 or 22 or 27 log scale in bunch profiles   (PROFGR) and (PROFGRD)
   ncstat=1
   data(1)=0.
   do i=1,20
     pfnm(i)=''
   enddo
   quotes='"'
   ll=len_trim(fname)
   if(fname(ll:ll).eq.'"') fname=fname(1:ll-1)
   ll=len_trim(fname)
   if(fname(1:1).eq.'"') fname=fname(2:ll)
!   write(6,*) "DBX before enumerate dynaxXX.plt ",trim(fname)   
   pfnm(1)=trim(fname)//'dynac01.plt'
   pfnm(2)=trim(fname)//'dynac02.plt'
   pfnm(3)=trim(fname)//'dynac03.plt'
   pfnm(4)=trim(fname)//'dynac04.plt'
   pfnm(5)=trim(fname)//'dynac05.plt'
   pfnm(6)=trim(fname)//'dynac06.plt'
   pfnm(7)=trim(fname)//'dynac07.plt'
   pfnm(8)=trim(fname)//'dynac08.plt'
   pfnm(9)=trim(fname)//'dynac09.plt'
   pfnm(10)=trim(fname)//'dynac10.plt'
   pfnm(11)=trim(fname)//'dynac11.plt'
   pfnm(12)=trim(fname)//'dynac12.plt'
   pfnm(13)=trim(fname)//'dynac13.plt'
   pfnm(14)=trim(fname)//'dynac14.plt'
   pfnm(15)=trim(fname)//'dynac15.plt'
   pfnm(16)=trim(fname)//'dynac16.plt'
   pfnm(17)=trim(fname)//'dynac17.plt'
   pfnm(18)=trim(fname)//'dynac18.plt'
   pfnm(19)=trim(fname)//'dynac19.plt'
   pfnm(20)=trim(fname)//'dynac20.plt'
   if(iopsy.eq.1 .or. iopsy.eq.3) then
! LINUX or MAC
!          command(1:40)="test ! -e savedplots && mkdir savedplots"
     if(llpath.eq.0)then
       command="test ! -e savedplots && mkdir savedplots"
       call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
     else
       command="test ! -e "//ppath(1:llpath)//"savedplots && mkdir "//ppath(1:llpath)//"savedplots"
       call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
     endif
   else
! WINDOWS
     if(llpath.eq.0)then
       if(cygwin) then
         command='test ! -e savedplots && echo Creating plots directory'
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
         command='test ! -e savedplots && mkdir savedplots' 
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
       else
         command="if not exist savedplots\\*.* echo creating plots directory"
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
         command="if not exist savedplots\\*.* mkdir savedplots"
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
         command="if not exist savedplots\\*.* copy ..\\bin\\tst savedplots"
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
       endif
     else
       if(cygwin) then
         command='test ! -e "'//trim(ppath)//'savedplots" && echo Creating plots directory'
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
         command='test ! -e "'//trim(ppath)//'savedplots" && mkdir "'//trim(ppath)//'savedplots"' 
         call EXECUTE_COMMAND_LINE(trim(COMMAND),wait=.true.)
       else
         command='if not exist "'//trim(ppath)//'savedplots\*.*" '//'echo Creating plots directory'   
         lcmd=len_trim(command)
         call EXECUTE_COMMAND_LINE(COMMAND(1:lcmd),wait=.true.)
         command="if not exist "//ppath(1:llpath)//"savedplots\*.* "//"mkdir "//ppath(1:llpath)//"savedplots" 
         lcmd=len_trim(command)          
         call EXECUTE_COMMAND_LINE(COMMAND(1:lcmd),wait=.true.)
       endif
     endif
   endif
!   write(6,*) "DBX prep for read emit.plot ",trim(fname)
   command=""
   IF (abs(data(1)).le.fprec) THEN
     if(cygwin) then
! Windows Cygwin	 
       fname(lpath+1:lpath+9)='emit.plot'
     else
       if(iopsy.eq.1 .or. iopsy.eq.3) then
         if(fname(1:1).ne.'/') then
           fname=fname(2:lpath)
         else
           fname=fname(1:lpath)
         endif
       else
! Windows
         fname=fname(1:lpath)
       endif
       fname=trim(fname)//'emit.plot'
     endif
     lfnam=len_trim(fname)
!     write(6,*) "DBX before read emit.plot ",trim(fname)
     OPEN(unit=66,file=fname)
     data(1)=1.
     data(2)=0.
   ENDIF
!  READ the emit.plot file
!+++++++++++++++++++++++++    
   DO
     read(66,*,iostat=ios) igrtyp 
!     write(6,*) 'DBX NEW in MAIN ios,igrtyp=',ios,igrtyp   
     if( ios < 0 ) exit ! end of file is reached
     iskale=0
     IF(igrtyp.eq.17 .or. igrtyp.eq.22 .or. igrtyp.eq.27)THEN
!   log scale in bunch profiles
       igrtyp=igrtyp-15
       iskale=1
       read(66,*) yminsk
     ELSEIF(igrtyp.eq.19)THEN
!   also log scale in bunch profiles
       igrtyp=igrtyp-1
       iskale=1
       read(66,*) yminsk
     ENDIF
     IF (igrtyp.eq.1 .or. igrtyp.eq.6 .or. igrtyp.eq.11) THEN
!+++++++++++++++++++++++++    
!   x-x', y-y', x-y, z-z' plots (EMITGR)
!+++++++++++++++++++++++++    
       data(2)=data(2)+1.
       data(5)=igrtyp
       nplot=int(data(2))
       if (igrtyp.eq.6) then
         read(66,*) ncstat
         read(66,*) (cstat(j),j=1,ncstat)
         do j=1,ncstat
           write(command(2:8),'(f7.3)') cstat(j)
           command(1:1)=' '
           cccst(j)=command(1:8)
         enddo
       endif
       if (igrtyp.eq.11) then
         read(66,*) ncstat
         read(66,*) (zstat(j),j=1,ncstat)
         do j=1,ncstat
           cstat(j)=zstat(j)
           write(command(1:4),'(F4.2)') zstat(j)
           cccst(j)=command(1:4)
         enddo
       endif
       READ(66,'(a80)') title(1:80)
!       write(6,*) "DBX title ",title
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       DO i=1,201
         READ(66,*) dx(i),dxp(i)
         ctrx1(i)=dx(i)
         ctry1(i)=dxp(i)
       ENDDO
       READ(66,*) imax
       if (igrtyp.eq.1) then
         DO i=1,imax
           READ(66,*) dx(i),dxp(i)
           cx(i)=dx(i)
           cxp(i)=dxp(i)
         ENDDO
       else
         DO i=1,imax
           READ(66,*) dx(i),dxp(i),cst(i)
           cx(i)=dx(i)
           cxp(i)=dxp(i)
         ENDDO
       endif
       labels(1)='x (cm)'
       labels(2)='xp (mrad)'
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(2)=uxmin
       xmax(2)=uxmax
       ymin(2)=uymin
       ymax(2)=uymax
       DO i=1,201
         READ(66,*) dx(i),dxp(i)
         ctrx2(i)=dx(i)
         ctry2(i)=dxp(i)
       ENDDO
       READ(66,*) imax
       if (igrtyp.eq.1) then
         DO i=1,imax
           READ(66,*) dx(i),dxp(i)
           cy(i)=dx(i)
           cyp(i)=dxp(i)
         ENDDO
       else
         DO i=1,imax
           READ(66,*) dx(i),dxp(i),cst(i)
           cy(i)=dx(i)
           cyp(i)=dxp(i)
         ENDDO
       endif
       labels(3)='y (cm)'
       labels(4)='yp (mrad)'
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(3)=uxmin
       xmax(3)=uxmax
       ymin(3)=uymin
       ymax(3)=uymax
       labels(5)='x (cm)'
       labels(6)='y (cm)'
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(4)=uxmin
       xmax(4)=uxmax
       ymin(4)=uymin
       ymax(4)=uymax
       DO i=1,201
         READ(66,*) dx(i),dxp(i)
         ctrx3(i)=dx(i)
         ctry3(i)=dxp(i)
       ENDDO
       READ(66,*) imax
       if (igrtyp.eq.1) then
         DO i=1,imax
           READ(66,*) dx(i),dxp(i)
           cz(i)=dx(i)
           czp(i)=dxp(i)
         ENDDO
       else
         DO i=1,imax
           READ(66,*) dx(i),dxp(i),cst(i)
           cz(i)=dx(i)
           czp(i)=dxp(i)
         ENDDO
       endif
       labels(7)='z (deg)'
       labels(8)='zp (MeV)'
!       write(6,*) "DBX before wfile10 0"
       call wfile10(0,imax)
!       write(6,*) "DBX before wfile10 1"
       call wfile10(1,imax)
       isave=0
!       write(6,*) "DBX before wfile20"
       call wfile20(isave,nplot)
!       write(6,*) "DBX after  wfile20"
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command), wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command), wait=.true.)
       else
!   WINDOWS
         command=''
         if(cygwin) then
           if(dgui) then
             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
           else  
             command="gnuplot "//trim(ppath)//"dynac.gnu"
           endif  
         else  
           if(dgui) then
             j=len_trim(ppath)
             if(ppath(j:j).eq.'"') then
               command='gnuplot '//ppath(1:j-1)//'dynac.gnu"'
             else  
               command='gnuplot "'//trim(ppath)//'dynac.gnu"'
             endif  
           else  
             command="gnuplot "//trim(ppath)//"dynac.gnu"
           endif  
         endif
!         write(6,*) "DBX plot x,y,xy,z ",dgui,trim(command)
         call EXECUTE_COMMAND_LINE(trim(command), wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.2 .or. igrtyp.eq.7 .or. igrtyp.eq.12) THEN
!+++++++++++++++++++++++++    
!   z-x, z-y distribution plots & profiles (PROFGR)
!+++++++++++++++++++++++++    
       data(5)=igrtyp
       data(2)=data(2)+1.
       nplot=int(data(2))
       if (igrtyp.eq.7) then
         read(66,*) ncstat
         read(66,*) (cstat(j),j=1,ncstat)
         do j=1,ncstat
!           icstat(j)=int(cstat(j))
!           write(command(2:5),'(I2)') icstat(j)
           write(command(2:8),'(F7.3)') cstat(j)
           command(1:1)=' '
           cccst(j)=command(1:8)
         enddo
       endif
       if (igrtyp.eq.12) then
         read(66,*) ncstat
         read(66,*) (zstat(j),j=1,ncstat)
         do j=1,ncstat
           cstat(j)=zstat(j)
           write(command(1:4),'(f4.2)') zstat(j)
           cccst(j)=command(1:4)
         enddo
       endif
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax
       if (igrtyp.eq.2) then
         DO i=1,imax
           READ(66,*) dx(i),dxp(i)
           cx(i)=dx(i)
           cxp(i)=dxp(i)
         ENDDO
       else
         DO i=1,imax
           READ(66,*) dx(i),dxp(i),cst(i)
           cx(i)=dx(i)
           cxp(i)=dxp(i)
         ENDDO
       endif
       labels(1)='z (cm)'
       labels(2)='x (cm)'
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(2)=uxmin
       xmax(2)=uxmax
       ymin(2)=uymin
       ymax(2)=uymax
       READ(66,*) imax
       if (igrtyp.eq.2) then
         DO i=1,imax
           READ(66,*) dx(i),dxp(i)
           cy(i)=dx(i)
           cyp(i)=dxp(i)
         ENDDO
       else
         DO i=1,imax
           READ(66,*) dx(i),dxp(i),cst(i)
           cy(i)=dx(i)
           cyp(i)=dxp(i)
         ENDDO
       endif
       labels(3)='z (cm)'
       labels(4)='y (cm)'
!       write(6,*) "DBX b4 wfile11"
       call wfile11(imax)
       isave=0
!       write(6,*) "DBX b4 wfile21"
       call wfile21(isave,nplot)
!   profiles
!       write(6,*) "DBX b4 type 12 profs: ",trim(ppath)
       OPEN(unit=70,file=trim(ppath)//'dynac01.pro')
       OPEN(unit=71,file=trim(ppath)//'dynac02.pro')
       OPEN(unit=72,file=trim(ppath)//'dynac03.pro')
       OPEN(unit=73,file=trim(ppath)//'dynac04.pro')
       OPEN(unit=74,file=trim(ppath)//'dynac05.pro')
       OPEN(unit=75,file=trim(ppath)//'dynac06.pro')
       rewind(unit=70)
       rewind(unit=71)
       rewind(unit=72)
       rewind(unit=73)
       rewind(unit=74)
       rewind(unit=75)
       READ(66,*) imx
       DO i=1,imx
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(70,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imy
       DO i=1,imy
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(71,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imz
       DO i=1,imz
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(72,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imxp
       DO i=1,imxp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(73,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imyp
       DO i=1,imyp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(74,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imzp
       DO i=1,imzp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(75,*)dx(i),dxp(i)
       ENDDO
       close(70)
       close(71)
       close(72)
       close(73)
       close(74)
       close(75)
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
!         if(cygwin) then
!           if(dgui) then
!             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
!           else  
!             command="gnuplot "//trim(ppath)//"dynac.gnu"
!           endif  
!         else  
           if(dgui) then
             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
           else  
             command='gnuplot '//trim(ppath)//'dynac.gnu'
           endif  
!         endif
!         write(6,*) "DBX90 in main cmd=",trim(command)
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.18) THEN
!+++++++++++++++++++++++++    
!   z-x, z-y density plots & profiles
!+++++++++++++++++++++++++    
       data(5)=igrtyp
       data(2)=data(2)+1.
       nplot=int(data(2))
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(17),bex(18),bex(19),bex(20)
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax,ndx,ndy
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) zxar(i,j)
         ENDDO
       ENDDO
       labels(1)='z (cm)'
       labels(2)='x (cm)'
       READ(66,*) zxmax
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(21),bex(22),bex(23),bex(24)
       xmin(2)=uxmin
       xmax(2)=uxmax
       ymin(2)=uymin
       ymax(2)=uymax
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) zyar(i,j)
         ENDDO
       ENDDO
       READ(66,*) zymax
       labels(3)='z (cm)'
       labels(4)='y (cm)'
       call wfile111(ndx,ndy)
       isave=0
       call wfile121(isave,nplot)
!   profiles
       OPEN(unit=70,file=trim(ppath)//'dynac01.pro')
       OPEN(unit=71,file=trim(ppath)//'dynac02.pro')
       OPEN(unit=72,file=trim(ppath)//'dynac03.pro')
       OPEN(unit=73,file=trim(ppath)//'dynac04.pro')
       OPEN(unit=74,file=trim(ppath)//'dynac05.pro')
       OPEN(unit=75,file=trim(ppath)//'dynac06.pro')
       rewind(unit=70)
       rewind(unit=71)
       rewind(unit=72)
       rewind(unit=73)
       rewind(unit=74)
       rewind(unit=75)
       READ(66,*) imx
       DO i=1,imx
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(70,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imy
       DO i=1,imy
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(71,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imz
       DO i=1,imz
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(72,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imxp
       DO i=1,imxp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(73,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imyp
       DO i=1,imyp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(74,*)dx(i),dxp(i)
       ENDDO
       READ(66,*) imzp
       DO i=1,imzp
          READ(66,*) dx(i),dxp(i)
          if (abs(dxp(i)).le.fprec) dxp(i)=1.e-8
          write(75,*)dx(i),dxp(i)
       ENDDO
       close(70)
       close(71)
       close(72)
       close(73)
       close(74)
       close(75)
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
!         write(6,*) "DBX in main igrtyp18 ppa=",trim(ppath)
         if(cygwin) then
           if(dgui) then
             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
           else  
             command="gnuplot "//trim(ppath)//"dynac.gnu"
           endif  
         else  
           if(dgui) then
             k=len_trim(ppath)
             if(ppath(k:k).eq.'"') then
               command='gnuplot '//ppath(1:k-1)//'dynac.gnu"'
             else  
               command='gnuplot "'//trim(ppath)//'dynac.gnu"'
             endif  
           else  
             command='gnuplot '//trim(ppath)//'dynac.gnu'
           endif  
         endif
!         write(6,*) "DBX in main igrtyp18 cmd=",trim(command)
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.16) THEN
!+++++++++++++++++++++++++++++++++++++++++    
!   x-x', y-y', x-y, z-z' 2D density plots
!+++++++++++++++++++++++++++++++++++++++++    
       data(2)=data(2)+1.
       data(5)=igrtyp
       nplot=int(data(2))
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(1),bex(2),bex(3),bex(4)
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax,ndx,ndy
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) xxpar(i,j)
         ENDDO
       ENDDO
       labels(1)='x (cm)'
       labels(2)='xp (mrad)'
       READ(66,*) xxpmax
!  
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(5),bex(6),bex(7),bex(8)
       xmin(2)=uxmin
       xmax(2)=uxmax
       ymin(2)=uymin
       ymax(2)=uymax
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) yypar(i,j)
         ENDDO
       ENDDO
       labels(3)='y (cm)'
       labels(4)='yp (mrad)'
       READ(66,*) yypmax
!  
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(9),bex(10),bex(11),bex(12)
       xmin(3)=uxmin
       xmax(3)=uxmax
       ymin(3)=uymin
       ymax(3)=uymax
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) xyar(i,j)
         ENDDO
       ENDDO
       labels(5)='x (cm)'
       labels(6)='y (cm)'
       READ(66,*) xymax
!  
       READ(66,*) uxmin,uxmax,uymin,uymax
       READ(66,*) bex(13),bex(14),bex(15),bex(16)
       xmin(4)=uxmin
       xmax(4)=uxmax
       ymin(4)=uymin
       ymax(4)=uymax
       DO i=1,ndx
         DO j=1,ndy
           READ(66,*) zzpar(i,j)
         ENDDO
       ENDDO
       labels(7)='z (deg)'
       labels(8)='zp (MeV)'
       READ(66,*) zzpmax
!   Write the histogrammed data which will be plotted by GNU to a file
!       write(6,*) "DBX b4 wfile110"          
       call wfile110(ndx,ndy)
       isave=0
!   Write the .gnu gnuplot file for the xx'-yy'-xy-zz' 2D plot          
!       write(6,*) "DBX b4 wfile120"          
       call wfile120(isave,nplot)
!       write(6,*) "DBX b4 gnuplot cmd"          
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
!         if(cygwin) then
!           if(dgui) then
!             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
!           else  
!             command="gnuplot "//trim(ppath)//"dynac.gnu"
!           endif  
!         else  
           if(dgui) then
             command='gnuplot "'//trim(ppath)//'dynac.gnu"'
           else  
             command='gnuplot '//trim(ppath)//'dynac.gnu'
           endif  
!         endif
!         write(6,*) "DBX splot x,y,xy,z ",dgui,trim(command)
         call EXECUTE_COMMAND_LINE(trim(command), wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.3) THEN
!+++++++++++++++++++++++++    
!   x,y envelopes as f(z)
!+++++++++++++++++++++++++    
       data(5)=igrtyp
       data(2)=data(2)+1.
       nplot=int(data(2))
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax
       DO i=1,imax
         READ(66,*) dx(i),dxp(i)
         cx(i)=dx(i)
         cxp(i)=dxp(i)
       ENDDO
       READ(66,*) imax
       DO i=1,imax
         READ(66,*) dx(i),dxp(i)
         cy(i)=dx(i)
         cyp(i)=dxp(i)
       ENDDO
       labels(1)='z (m)'
       labels(2)='x,y (cm)'
       call wfile3(imax)
       isave=0
       call wfile2(isave,2,nplot)
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.4) THEN
!+++++++++++++++++++++++++    
!   dW/W envelope as f(z)
!+++++++++++++++++++++++++    
       data(5)=igrtyp
       data(2)=data(2)+1.
       nplot=int(data(2))
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax
       DO i=1,imax
         READ(66,*) dx(i),dxp(i)
         cx(i)=dx(i)
         cxp(i)=dxp(i)
       ENDDO
       labels(1)='z (m)'
       labels(2)='dW/W (per mille)'
       call wfile1(imax)
       isave=0
       call wfile2(isave,3,nplot)
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       endif
     ENDIF
     IF (igrtyp.eq.5) THEN
!+++++++++++++++++++++++++    
!   dPHI envelope as f(z)
!+++++++++++++++++++++++++    
       data(5)=igrtyp
       data(2)=data(2)+1.
       nplot=int(data(2))
       READ(66,'(a80)') title(1:80)
       READ(66,*) uxmin,uxmax,uymin,uymax
       xmin(1)=uxmin
       xmax(1)=uxmax
       ymin(1)=uymin
       ymax(1)=uymax
       READ(66,*) imax
       DO i=1,imax
         READ(66,*) dx(i),dxp(i)
         cx(i)=dx(i)
         cxp(i)=dxp(i)
       ENDDO
       labels(1)='z (m)'
       labels(2)='dPHI (deg)'
       call wfile1(imax)
       isave=0
       call wfile2(isave,4,nplot)
       if(iopsy.eq.1) then
!   LINUX
         command=''
         !command="gnuplot -noraise -geometry 500x515-250+25 "//trim(ppath)//"dynac.gnu"
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       elseif(iopsy.eq.3) then
!   MAC
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       else
!   WINDOWS
         command=''
         if(dgui) then
           command='gnuplot "'//trim(ppath)//'dynac.gnu"'
         else  
           command='gnuplot '//trim(ppath)//'dynac.gnu'
         endif  
         call EXECUTE_COMMAND_LINE(trim(command),wait=.true.)
       endif
     ENDIF
! ask if the file should be saved when plotit is called from the terminal,
! but not if the terminal type is gif, jpeg or png
     if(.not. s2gr) then
       if(.not. dgui) call savefile
     endif  
     write(6,'(A,i3,A)') 'Plot ',int(data(2)),' has been plotted'
     write(6,*)
   ENDDO
   write(6,'(A,I3)')'Total number of plots: ',int(data(2))
   data(4)=1.
   CLOSE(66)
   data(3)=float(imax)
   END PROGRAM dynplt
