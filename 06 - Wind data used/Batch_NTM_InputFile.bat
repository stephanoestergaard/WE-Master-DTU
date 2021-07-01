@echo off
setlocal EnableDelayedExpansion
set LF=^



set SEED=%1
set U=%2

set source=IEA15MW_IEC_NTM_UX.X_SeedXXXXX.inp
set target=IEA15MW_IEC_NTM_U%U%_Seed%SEED%.inp

echo %source%
echo %target%


set tmp=

for /f "delims=" %%x in (%source%) do (
  set tmp=!tmp!%%x!LF!
)



REM echo tmp=!tmp:SEED_NO=%SEED%!>>file2.txt

set tmp=!tmp:SEED_NO=%SEED%!
set tmp=!tmp:U_VAL=%U%!

echo !tmp!

echo !tmp!>%target%

endlocal


