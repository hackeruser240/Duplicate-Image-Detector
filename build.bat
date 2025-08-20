@echo off

rem Delete existing build and dist folders if they exist
echo ===========================================
echo Cleaning previous build artifacts...
rmdir /S /Q "build" 2>nul
rmdir /S /Q "dist" 2>nul
IF EXIST *.spec (
    DEL /F /Q *.spec
)
echo Cleaning complete.
echo ===========================================

rem Run PyInstaller command

pyinstaller --clean --onefile --noconsole --name="Image Duplication Detector" --hidden-import=imagehash -p ./src src/gui.py

echo ===========================================
echo Build process finished
echo ===========================================