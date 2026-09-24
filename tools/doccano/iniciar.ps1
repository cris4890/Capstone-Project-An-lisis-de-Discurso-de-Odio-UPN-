$ErrorActionPreference = 'Stop'
$pilotRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pilotPython = Join-Path $pilotRoot 'private/doccano/venv/Scripts/python.exe'
$pilotScript = Join-Path $PSScriptRoot 'local.py'
if (Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue) {
    Write-Output 'El puerto 8001 ya esta ocupado. Comprueba http://127.0.0.1:8001 antes de iniciar otra instancia.'
    exit
}
Start-Process -FilePath $pilotPython -ArgumentList @(('"' + $pilotScript + '"'), 'webserver', '--port', '8001') -WorkingDirectory $pilotRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $pilotRoot 'private/doccano/server.log') -RedirectStandardError (Join-Path $pilotRoot 'private/doccano/server-error.log')
Write-Output 'Servidor iniciandose en http://127.0.0.1:8001. Los proyectos del piloto ya estan cargados.'
