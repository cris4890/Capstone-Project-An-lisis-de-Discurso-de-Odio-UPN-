$ErrorActionPreference = 'Stop'
$pilotRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $pilotRoot
try {
    $snapshotPath = & 'private/doccano/venv/Scripts/python.exe' 'tools/doccano/export_independent.py'
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo exportar Doccano.' }
    & '.venv/Scripts/python.exe' 'doccano_import.py' $snapshotPath
    if ($LASTEXITCODE -ne 0) { throw 'La validación no terminó correctamente.' }
    Write-Output "Informe y evidencia conservados junto a: $snapshotPath"
} finally { Pop-Location }
