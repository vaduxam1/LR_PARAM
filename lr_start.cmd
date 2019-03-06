@echo off
rem v11.6.5 автоустановка python-3.4.4, если python не установлен
set NLS_LANG=RUSSIAN_RUSSIA.CL8MSWIN1251

rem определить установлен ли python
rem необходимо прописать путь к python.exe, в переменную окружения windows: Path=c:\Python\;
python /? > NUL
rem либо будет использоватся стандартный путь к python
if not %errorlevel% == 0 (
    echo set python.exe path: Windows "Environment Variables" / "Path"
    c:\Python34\python.exe /? > NUL
)

if %errorlevel% == 0 (
    rem assoc | findstr /i /r ".py=Python.File" > NUL
    echo python already installed
) ELSE (
    rem если python был установлен ранее, но не прописан в переменные окружения,
    rem то не факт что он установится, прежде необходимо или удалить, или прописать.
    echo installing python-3.4.4
    lr_lib\whl\python-3.4.4.msi /quiet TargetDir=c:\Python34\ AssociateFiles=1
    rem set PATH=c:\Python34\;%PATH%
    rem Просмотр и изменение типов файлов, сопоставленных с расширением имен файлов
    ftype Python.File=c:\Python34\python.exe
    rem Просмотр и изменение сопоставлений файлов.
    assoc .py=Python.File
)

rem попробовать запустить в любом случае
rem при необходимости выбрать "c:\Python34\python.exe" в windows диалоге "открыть файл как"
echo try run lr_start.py ...
lr_start.py
