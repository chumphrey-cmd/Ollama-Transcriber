<#
.SYNOPSIS
    Automated setup script for the Ollama Transcriber project.
.DESCRIPTION
    This script requires Administrator privileges. It intelligently checks for
    and installs required dependencies (Chocolatey, FFmpeg, Git, Python 3.10) only if 
    they are missing, creates a virtual environment, and installs Python packages.
#>

# --- ASCII ART BANNER ---
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
Write-Host "[1/8] Enabling Windows Long Paths..." -ForegroundColor Green
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
Write-Host "Long paths enabled successfully."

# Step 3: Check and Install Chocolatey
Write-Host "`n[2/8] Checking for Chocolatey Package Manager..." -ForegroundColor Green
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
Write-Host "`n[3/8] Checking for FFmpeg..." -ForegroundColor Green
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg not found. Installing globally via Chocolatey..." -ForegroundColor Yellow
    choco install ffmpeg -y
    # Refresh Environment Variables so venv can see it
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "FFmpeg is already installed. Skipping."
}

# NEW Step 5: Check and Install Git
Write-Host "`n[4/8] Checking for Git..." -ForegroundColor Green
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git not found. Installing globally via Chocolatey..." -ForegroundColor Yellow
    choco install git -y
    # Refresh Environment Variables so pip can use it
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Git is already installed. Skipping."
}

# Step 6: Check and Install Python 3.10
Write-Host "`n[5/8] Checking for Python 3.10..." -ForegroundColor Green
if (!(Get-Command python3.10 -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3.10 not found. Installing via Chocolatey..." -ForegroundColor Yellow
    choco install python310 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    $pythonVer = python3.10 --version 2>&1
    Write-Host "Python 3.10 is already installed: $pythonVer. Skipping."
}

# Step 7: Create and Activate Virtual Environment
Write-Host "`n[6/8] Setting up Python Virtual Environment..." -ForegroundColor Green
if (!(Test-Path -Path "venv")) {
    Write-Host "Creating new virtual environment using python3.10..." -ForegroundColor Yellow
    python3.10 -m venv venv
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}
# Activate the venv
. .\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated for installation."

# Step 8: Install Requirements
Write-Host "`n[7/8] Checking Python dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet

# Check if PyTorch is installed AND has CUDA available
Write-Host "Verifying PyTorch CUDA installation..." -ForegroundColor Yellow
$torchCudaAvailable = $false
try {
    # This inline python command prints "True" if CUDA is good, or throws an error/prints "False" if not
    $result = python -c "import torch; print(torch.cuda.is_available())" 2>$null
    if ($result -match "True") {
        $torchCudaAvailable = $true
    }
} catch {
    # Catch any errors if torch isn't installed at all
}

if ($torchCudaAvailable) {
    Write-Host "PyTorch with CUDA is already installed and working. Skipping large download." -ForegroundColor Green
} else {
    Write-Host "PyTorch with CUDA not found. Installing now (This is a large download and may take a few minutes)..." -ForegroundColor Yellow
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-warn-script-location
}

Write-Host "`nInstalling remaining Python dependencies from requirements.txt..." -ForegroundColor Green
python -m pip install -r requirements.txt --no-warn-script-location

# Step 9: Final Verification
Write-Host "`n[8/8] Verifying PyTorch and CUDA installation..." -ForegroundColor Green
python pytorch_verify.py

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host " Setup Complete! Your environment is ready. " -ForegroundColor Green
Write-Host " To run the app in a new terminal, type: " -ForegroundColor White
Write-Host " 1. . .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host " 2. python main.py" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan