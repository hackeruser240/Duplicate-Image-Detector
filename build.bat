@echo off

rem Delete existing build and dist folders if they exist
echo ===========================================
echo Cleaning previous build artifacts...
rmdir /S /Q "build" 2>nul
echo Deleted build/
rmdir /S /Q "dist" 2>nul
echo Deleted dist/
IF EXIST *.spec (
    DEL /F /Q *.spec
    echo Deleted *spec)
echo Cleaning complete.
echo ===========================================

rem Run PyInstaller command

pyinstaller --clean --onefile --noconsole --name="Image Duplication Detector" --hidden-import=imagehash -p ./src src/gui.py

echo ===========================================
echo Build process finished
echo ===========================================