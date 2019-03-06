@echo off
rem v11.6.5 __main__
set NLS_LANG=RUSSIAN_RUSSIA.CL8MSWIN1251

rem проверка установлен ли python
python /? > NUL
if not %errorlevel% == 0 (
    c:\Python34\python.exe /? > NUL
)

if %errorlevel% == 0 (
    echo python already installed
) ELSE (
    echo installing python-3.4.4
    lr_lib\whl\python-3.4.4.msi /quiet TargetDir=c:\Python34\ AssociateFiles=1

    rem Просмотр и изменение типов файлов, сопоставленных с расширением имен файлов
    ftype Python.File=c:\Python34\python.exe
    rem Просмотр и изменение сопоставлений файлов.
    assoc .py=Python.File
)

echo try run lr_start.py ...
lr_start.py
