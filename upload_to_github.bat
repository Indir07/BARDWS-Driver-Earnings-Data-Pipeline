@echo off
echo ====================================================
echo Uploading BARDWS Data Pipeline to GitHub
echo ====================================================
echo.

:: Initialize git repository
if not exist .git (
    echo [1/4] Initializing Git repository...
    git init
) else (
    echo [1/4] Git repository already initialized.
)

:: Add all project files
echo [2/4] Adding files to git...
git add .

:: Create initial commit
echo [3/4] Creating initial commit...
git commit -m "Initial commit of BARDWS Driver Earnings Data Pipeline"

:: Rename default branch to main
git branch -M main

:: Check if remote origin already exists
git remote remove origin >nul 2>&1
echo [4/4] Adding remote origin...
git remote add origin https://github.com/Indir07/BARDWS-Driver-Earnings-Data-Pipeline.git

echo.
echo Pushing project to GitHub...
echo (If prompted, please enter your GitHub credentials or authorize in your browser)
echo.
git push -u origin main

echo.
echo ====================================================
echo Upload Complete!
echo ====================================================
pause
