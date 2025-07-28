@echo off
echo ========================================
echo    SISTEMA DE CONTROL DE STOCK
echo ========================================
echo.
echo Abriendo el sistema...
echo.

cd /d "%~dp0Proyecto gestor de stock"
python Control_stock.py

echo.
echo Sistema cerrado.
pause 