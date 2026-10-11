@echo off
chcp 65001 > nul
title Codax Mesh Hub - Servidor On-Premise
cd /d "%~dp0"
echo Iniciando Codax Mesh Hub...
python start_server.py
pause
