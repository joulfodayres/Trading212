@echo off
REM T212 Limit Order Tester - Quick launch script
REM Usage: Double-click this file to launch the GUI

cd /d "%~dp0"
python test_limit_order_gui.py

if errorlevel 1 (
    echo.
    echo Error: Could not run the test program.
    echo Make sure you have Python 3 installed and requests package:
    echo.
    echo pip install requests
    echo.
    pause
)
