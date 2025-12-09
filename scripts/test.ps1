#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}
pytest -v tests/
