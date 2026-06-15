param(
    [switch]$NoPath
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppHome = if ($env:AIPROJ_HOME) { $env:AIPROJ_HOME } else { Join-Path $HOME ".aiproj" }
$BinDir = if ($env:AIPROJ_BIN_DIR) { $env:AIPROJ_BIN_DIR } else { Join-Path $AppHome "bin-shim" }

if ([string]::IsNullOrWhiteSpace($AppHome) -or (Resolve-Path -LiteralPath (Split-Path -Parent $AppHome) -ErrorAction SilentlyContinue) -eq $null) {
    throw "Unsafe or invalid AIPROJ_HOME: $AppHome"
}
if (([IO.Path]::GetFullPath($AppHome)).TrimEnd('\') -eq ([IO.Path]::GetPathRoot($AppHome)).TrimEnd('\')) {
    throw "Refusing to install into filesystem root: $AppHome"
}

New-Item -ItemType Directory -Force -Path $AppHome | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

if (([IO.Path]::GetFullPath($ScriptDir)).TrimEnd('\') -ne ([IO.Path]::GetFullPath($AppHome)).TrimEnd('\')) {
    Copy-Item -Path (Join-Path $ScriptDir "*") -Destination $AppHome -Recurse -Force
} else {
    Write-Host "Source and target are the same directory; skipping package copy."
}

$CmdPath = Join-Path $BinDir "aiproj.cmd"
$PyPath = Join-Path $AppHome "bin\aiproj.py"
Set-Content -LiteralPath $CmdPath -Encoding ASCII -Value "@echo off`r`npython `"$PyPath`" %*`r`n"

python $PyPath install-global --kit-root $AppHome --force

if (-not $NoPath) {
    $FullBinDir = [IO.Path]::GetFullPath($BinDir).TrimEnd('\')
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $PathItems = @()
    if (-not [string]::IsNullOrWhiteSpace($UserPath)) {
        $PathItems = $UserPath -split ';' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    }
    $AlreadyInPath = $false
    foreach ($Item in $PathItems) {
        $ExpandedItem = [Environment]::ExpandEnvironmentVariables($Item)
        try {
            $NormalizedItem = [IO.Path]::GetFullPath($ExpandedItem).TrimEnd('\')
        } catch {
            $NormalizedItem = $ExpandedItem.TrimEnd('\')
        }
        if ($NormalizedItem -ieq $FullBinDir) {
            $AlreadyInPath = $true
            break
        }
    }
    if (-not $AlreadyInPath) {
        $NewPathItems = @($PathItems) + $FullBinDir
        [Environment]::SetEnvironmentVariable("Path", ($NewPathItems -join ';'), "User")
        $env:Path = $env:Path + ";" + $FullBinDir
        Write-Host "Added $FullBinDir to the user PATH. New terminals will see aiproj automatically."
    } else {
        Write-Host "$FullBinDir is already in the user PATH."
    }
}

Write-Host "Installed aiproj to $AppHome"
Write-Host "Command wrapper: $CmdPath"
Write-Host "Run: aiproj --help"
