#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
Write-Output "Activating venv and starting server..."
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}
python .\run.py
