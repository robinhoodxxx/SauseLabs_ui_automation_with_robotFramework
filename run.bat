@echo off
setlocal
REM Generate datetime string
for /f "tokens=1-3 delims=/- " %%a in ("%date%") do (
    set yyyy=%%c
    set mm=%%a
    set dd=%%b
)
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set hh=%%a
    set min=%%b
    set ss=%%c
)
if "%hh:~0,1%"==" " set hh=0%hh:~1,1%
set "reportdir=Reports"
set "outdir=%reportdir%\%yyyy%%mm%%dd%_%hh%%min%%ss%"
python -m robot -A robot.options --outputdir %outdir% --variable SCREENSHOT_DIR:%outdir%\screenshots %*
REM Copy the log and report files into the output directory
copy "%outdir%\output.xml" "%reportdir%\"
copy "%outdir%\log.html" "%reportdir%\"
copy "%outdir%\report.html" "%reportdir%\"
if exist "%reportdir%\screenshots\" (
    echo Screenshots directory exists.
) else (
    echo Screenshots directory does not exist. Creating it.
    mkdir "%reportdir%\screenshots\"
    )
copy "%outdir%\screenshots\*" "%reportdir%\screenshots\"
REM Create a zip file of the output directory using PowerShell
powershell -Command "Compress-Archive -Path '%outdir%\*' -DestinationPath '%reportdir%\report.zip' -Force"
endlocal
