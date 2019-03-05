@echo off
set NLS_LANG=RUSSIAN_RUSSIA.CL8MSWIN1251

assoc | findstr /i /r ".py=" > Null

if %errorlevel% == 0 (
    echo lr_start.py
    lr_start.py

) ELSE (
    echo install python-3.4.4
    lr_lib\whl\python-3.4.4.msi /quiet TargetDir=c:\Python34\ AssociateFiles=1

    echo 2: lr_start.py
    lr_start.py
)