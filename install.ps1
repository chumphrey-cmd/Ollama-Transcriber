<#
.SYNOPSIS
    Automated setup script for the Ollama Transcriber project.
.DESCRIPTION
    This script requires Administrator privileges. It checks for
    and installs required dependencies (Chocolatey, FFmpeg, Python 3.10) only if 
    they are missing, creates a virtual environment, and installs Python packages.
#>

Clear-Host
Write-Host "  ____  _ _                        " -ForegroundColor Cyan
Write-Host " / __ \| | |                       " -ForegroundColor Cyan
Write-Host "| |  | | | | __ _ _ __ ___   __ _  " -ForegroundColor Cyan
Write-Host "| |  | | | |/ _\ | '_ \ _ \ / _\ | " -ForegroundColor Cyan
Write-Host "| |__| | | | (_| | | | | | | (_| | " -ForegroundColor Cyan
Write-Host " \____/|_|_|\__,_|_| |_| |_|\__,_| " -ForegroundColor Cyan
Write-Host " _______                   _ _               " -ForegroundColor Yellow
Write-Host "|__   __|                 (_) |              " -ForegroundColor Yellow
Write-Host "   | | _ __ __ _ _ __  ___ _| |__   ___ _ __ " -ForegroundColor Yellow
Write-Host "   | || '__/ _\ | '_ \/ __| | '_ \ / _ \ '__|" -ForegroundColor Yellow
Write-Host "   | || | | (_| | | | \__ \ | |_) |  __/ |   " -ForegroundColor Yellow
Write-Host "   |_||_|  \__,_|_| |_|___/_|_.__/ \___|_|   " -ForegroundColor Yellow
Write-Host "`n   >> Privacy-First Audio Transcription & Summarization <<   `n" -ForegroundColor Green

# Step 1: Administrator Check
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (!$isAdmin) {
    Write-Host "ERROR: This script requires Administrator privileges." -ForegroundColor Red
    Write-Host "Please right-click PowerShell, select 'Run as Administrator', and try again." -ForegroundColor Yellow
    Exit
}

# Step 2: Enable Windows Long Paths
Write-Host "[1/7] Enabling Windows Long Paths..." -ForegroundColor Green
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
Write-Host "Long paths enabled successfully."

# Step 3: Check and Install Chocolatey
Write-Host "`n[2/7] Checking for Chocolatey Package Manager..." -ForegroundColor Green
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey not found. Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    # Refresh Environment Variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Chocolatey is already installed. Skipping."
}

# Step 4: Check and Install FFmpeg
Write-Host "`n[3/7] Checking for FFmpeg..." -ForegroundColor Green
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg not found. Installing globally via Chocolatey..." -ForegroundColor Yellow
    choco install ffmpeg -y
    # Refresh Environment Variables so venv can see it
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "FFmpeg is already installed. Skipping."
}

# Step 5: Check and Install Python 3.10
Write-Host "`n[4/7] Checking for Python 3.10..." -ForegroundColor Green
if (!(Get-Command python3.10 -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3.10 not found. Installing via Chocolatey..." -ForegroundColor Yellow
    choco install python310 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    $pythonVer = python3.10 --version 2>&1
    Write-Host "Python 3.10 is already installed: $pythonVer. Skipping."
}

# Step 6: Create and Activate Virtual Environment
Write-Host "`n[5/7] Setting up Python Virtual Environment..." -ForegroundColor Green
if (!(Test-Path -Path "venv")) {
    Write-Host "Creating new virtual environment using python3.10..." -ForegroundColor Yellow
    # Explicitly use 3.10 to create the environment
    python3.10 -m venv venv
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}
# Activate the venv. 
# NOTE: Once activated on Windows, the isolated executable is named 'python.exe'
. .\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated for installation."

# Step 7: Install Requirements
Write-Host "`n[6/7] Installing/Updating Python dependencies (This will take a few minutes)..." -ForegroundColor Green
# We use 'python' here because the venv is activated, targeting the isolated 3.10 executable
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --no-warn-script-location

# Step 8: Final Verification
Write-Host "`n[7/7] Verifying PyTorch and CUDA installation..." -ForegroundColor Green
python pytorch_verify.py

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host " Setup Complete! Your environment is ready. " -ForegroundColor Green
Write-Host " To run the app in a new terminal, type: " -ForegroundColor White
Write-Host " 1. . .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host " 2. python3.10 main.py" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan