#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${GREEN}[CHECKING ENVIRONMENT]${NC}"

# Sprawdzenie git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git nie jest zainstalowany. Instalacja...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y git
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y git
        elif command -v pacman &> /dev/null; then
            sudo pacman -Syu --noconfirm git
        else
            echo -e "${RED}Nieznany menedżer pakietów. Zainstaluj git ręcznie.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install git
        else
            echo -e "${RED}Homebrew nie znaleziony. Zainstaluj git ręcznie.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Nieobsługiwany system. Zainstaluj git ręcznie.${NC}"
        exit 1
    fi
fi

# Funkcje do sprawdzenia Rust, Zig i Python (jak wcześniej)
check_rust() { ... }    # Pozostaje bez zmian
check_zig() { ... }     # Pozostaje bez zmian
check_python() { ... }  # Pozostaje bez zmian

check_rust
check_zig
check_python

# Katalog tymczasowy z opcją nadpisania
TMP_DIR="${HOME}/velvet_build"
if [ -d "$TMP_DIR" ]; then
    echo -e "${YELLOW}Katalog $TMP_DIR już istnieje. Nadpisać? [y/N]${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        rm -rf "$TMP_DIR"
    else
        echo "Anulowano."
        exit 1
    fi
fi

echo -e "${GREEN}[CLONING REPO]${NC}"
git clone https://github.com/Velvet-Lang/velvet.git "$TMP_DIR"
cd "$TMP_DIR"

echo -e "${GREEN}[BUILDING]${NC}"
cargo build --release
zig build

# Przeniesienie binarki Velvet do /usr/local/bin
BIN_PATH="./target/release/velvet"   # zakładam, że Velvet w cargo target
if [ -f "$BIN_PATH" ]; then
    sudo cp "$BIN_PATH" /usr/local/bin/velvet
    sudo chmod +x /usr/local/bin/velvet
    echo -e "${GREEN}Velvet zainstalowany globalnie: /usr/local/bin/velvet${NC}"
else
    echo -e "${RED}Nie znaleziono binarki Velvet w $BIN_PATH${NC}"
fi

# Czyszczenie
echo -e "${GREEN}[CLEANUP]${NC}"
# rm -rf "$TMP_DIR"  # Odkomentować jeśli chcesz usuwać katalog build

echo -e "${GREEN}[DONE] Velvet gotowy do użycia!${NC}"
