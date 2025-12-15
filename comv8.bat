gcc -c cgof.cc
gfortran -c -g -std=f2018 -Wall -fno-automatic dynacv8.f08
gfortran -O -o ..\bin\dynacv8.exe dynacv8.o cgof.o -lstdc++ -lcomdlg32