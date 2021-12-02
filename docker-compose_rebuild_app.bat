@ECHO OFF


Rem Get name of folder program is running in
set MYDIR=%~dp0
set MYDIR1=%MYDIR:~0,-1%

for %%f in (%MYDIR1%) do set myfolder=%%~nxf


echo.
echo Restarting %myfolder%_app using docker_compose:

echo - Stopping service...
docker-compose stop app
echo - Creating service...
docker-compose create app
echo - Starting service...
docker-compose start app


PAUSE