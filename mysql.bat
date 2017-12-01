@echo off
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
For /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
 
SET backupdir=C:\MySQLBackups\backupfiles
 
C:\Program Files\MySQL\MySQL Server 5.6\bin\mysqldump.exe -u root -p bakayar00 --events --routines --triggers parcelhubpos > %backupdir%\parcelhubpos_%mydate%_%mytime%_.sql

