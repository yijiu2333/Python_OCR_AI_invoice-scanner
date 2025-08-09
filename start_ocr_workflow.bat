@echo off
cd /d "E:\Python_OCR_AI_invoice-scanner"

title OCR serve workflow - CTRL+C to end
color 0A

:: 配置基础路径
set "ROOT=E:\Python_OCR_AI_invoice-scanner"

:: 创建必要目录
if not exist "%ROOT%\input" mkdir "%ROOT%\input"
if not exist "%ROOT%\archives" mkdir "%ROOT%\archives"
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"

python main.py
pause