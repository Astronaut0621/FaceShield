param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$PythonPath = if ([System.IO.Path]::IsPathRooted($Python)) {
    $Python
} else {
    Join-Path $Root $Python
}

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Python not found: $PythonPath"
}

& $PythonPath -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
& $PythonPath (Join-Path $PSScriptRoot "floating_assistant.py")
