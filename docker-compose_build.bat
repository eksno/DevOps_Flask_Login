@ECHO OFF


Rem Get name of folder program is running in
set MYDIR=%~dp0
set MYDIR1=%MYDIR:~0,-1%

for %%f in (%MYDIR1%) do set myfolder=%%~nxf


echo.
echo Running %myfolder% using docker_compose:

echo - Running using docker_compose...
docker-compose -f "docker-compose.yml" up --build


PAUSE