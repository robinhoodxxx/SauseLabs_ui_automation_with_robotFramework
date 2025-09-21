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
set "outdir=reports\%yyyy%-%mm%-%dd%_%hh%-%min%-%ss%"
python -m robot -A robot.options --outputdir %outdir% --variable SCREENSHOT_DIR:%outdir%\screenshots %*
endlocal
