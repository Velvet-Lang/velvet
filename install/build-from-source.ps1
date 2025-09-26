# Velvet Build Script (PowerShell)
# Uruchom jako Administrator na Windows lub z sudo na Linux/macOS

$ErrorActionPreference = "Stop"

Write-Host "[CHECKING ENVIRONMENT]" -ForegroundColor Cyan

function Check-Rust {
    if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) {
        Write-Host "Rust nie jest zainstalowany. Instalacja..." -ForegroundColor Yellow
        if ($IsWindows) {
            Invoke-WebRequest -Uri "https://win.rustup.rs/x86_64" -OutFile "$env:TEMP\rustup-init.exe"
            & "$env:TEMP\rustup-init.exe" -y
            Remove-Item "$env:TEMP\rustup-init.exe"
        } else {
            Invoke-WebRequest -Uri "https://sh.rustup.rs" -OutFile "/tmp/rustup.sh"
            & bash /tmp/rustup.sh -y
            Remove-Item "/tmp/rustup.sh"
        }
        $env:PATH += [System.IO.Path]::PathSeparator + "$HOME/.cargo/bin"
    } else {
        Write-Host "Rust jest zainstalowany: $(rustc --version)" -ForegroundColor Green
    }
}

function Check-Zig {
    if (-not (Get-Command zig -ErrorAction SilentlyContinue)) {
        Write-Host "Zig nie jest zainstalowany!" -ForegroundColor Yellow
        if ($IsWindows) {
            Write-Host "Pobierz Zig ze strony: https://ziglang.org/download/" -ForegroundColor Red
        } else {
            Write-Host "Zainstaluj Zig przez menedżer pakietów (apt/dnf/pacman/brew)" -ForegroundColor Red
        }
        Read-Host "Naciśnij Enter, gdy Zig będzie zainstalowany..."
    } else {
        Write-Host "Zig jest zainstalowany: $(zig version)" -ForegroundColor Green
    }
}

function Check-Python {
    if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Write-Host "Python3 nie jest zainstalowany!" -ForegroundColor Yellow
        if ($IsWindows) {
            Write-Host "Pobierz Python3 ze strony: https://www.python.org/downloads/windows/" -ForegroundColor Red
        } else {
            Write-Host "Zainstaluj Python3 przez menedżer pakietów (apt/dnf/pacman/brew)" -ForegroundColor Red
        }
        Read-Host "Naciśnij Enter, gdy Python3 będzie zainstalowany..."
    } else {
        Write-Host "Python3 jest zainstalowany: $(python3 --version)" -ForegroundColor Green
    }
}

# Wywołanie funkcji
Check-Rust
Check-Zig
Check-Python

Write-Host "[CLONING REPO]" -ForegroundColor Cyan

$TempDir = Join-Path -Path $env:TEMP -ChildPath "velvet_build"
if (Test-Path $TempDir) {
    Write-Host "Katalog $TempDir już istnieje. Usunąć go? [y/N]" -ForegroundColor Yellow
    $answer = Read-Host
    if ($answer -match "^[Yy]$") {
        Remove-Item -Recurse -Force $TempDir
    } else {
        Write-Host "Anulowano." -ForegroundColor Red
        exit 1
    }
}

git clone https://github.com/Velvet-Lang/velvet.git $TempDir
Set-Location $TempDir

Write-Host "[BUILDING]" -ForegroundColor Cyan

# Build Velvet
cargo build --release
zig build

# Opcjonalne przeniesienie binarki (Linux/macOS)
$BinPath = Join-Path -Path $TempDir -ChildPath "target/release/velvet"
if (Test-Path $BinPath -PathType Leaf) {
    if (-not $IsWindows) {
        sudo cp $BinPath /usr/local/bin/velvet
        sudo chmod +x /usr/local/bin/velvet
        Write-Host "Velvet zainstalowany globalnie: /usr/local/bin/velvet" -ForegroundColor Green
    } else {
        Write-Host "Windows: uruchom $BinPath bezpośrednio lub dodaj do PATH" -ForegroundColor Green
    }
} else {
    Write-Host "Nie znaleziono binarki Velvet w $BinPath" -ForegroundColor Red
}

Write-Host "[DONE] Velvet gotowy do użycia!" -ForegroundColor Cyan

