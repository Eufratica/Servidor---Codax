@echo off
chcp 65001 > nul
title Codax Mesh Hub - Instancia 8001 (Em Breve)
cd /d "%~dp0"
set WEB_PORT=8001
set DISABLED_TABS=ota,serial,webserver,timestream,scifi
echo Iniciando Codax Mesh Hub na porta %WEB_PORT% (Abas Em breve: %DISABLED_TABS%)...
python app.py
pause
