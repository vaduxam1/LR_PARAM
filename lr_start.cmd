rem v11.6.5 __main__
@echo off
set NLS_LANG=RUSSIAN_RUSSIA.CL8MSWIN1251

rem // проверить наличие установленного python, по windows-ассоциации с файлом: ".py=Python.File"
assoc | findstr /i /r ".py=Python" > NUL

if %errorlevel% == 0 (
    echo python already installed

) ELSE (
    echo installing python-3.4.4
    lr_lib\whl\python-3.4.4.msi /quiet TargetDir=c:\Python34\ AssociateFiles=1
)

echo run lr_start.py ...
lr_start.py