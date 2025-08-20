@echo off
REM Activate your virtual environment first
REM Example: call path\to\your\venv\Scripts\activate

call py-env\Scripts\activate.bat

echo ===========================================
echo Installing required Python packages...
echo ===========================================

pip install Pillow
pip install imagehash
pip install numpy
pip install pyinstaller
pip install imagehash

echo ===========================================
echo All packages installed.
echo ===========================================
pause