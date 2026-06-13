#!/bin/bash
# ============================================================
#  Yukioh_Ōkami — Termux Installer v2.0
# ============================================================

clear

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
WHITE='\033[1;37m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

spinner() {
    local pid=$1
    local msg=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    while kill -0 $pid 2>/dev/null; do
        printf "\r  ${CYAN}${spin:$i:1}${NC}  ${DIM}$msg${NC}"
        i=$(( (i+1) % 10 ))
        sleep 0.08
    done
    printf "\r"
}

progress_bar() {
    local current=$1
    local total=$2
    local label=$3
    local width=30
    local filled=$(( current * width / total ))
    local empty=$(( width - filled ))
    local pct=$(( current * 100 / total ))
    local bar="${GREEN}"
    for ((i=0; i<filled; i++)); do bar+="█"; done
    bar+="${DIM}"
    for ((i=0; i<empty; i++)); do bar+="░"; done
    bar+="${NC}"
    printf "  [${bar}] ${BOLD}%3d%%${NC}  ${DIM}%s${NC}\n" $pct "$label"
}

print_banner() {
    echo -e "${GREEN}  ╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}  ║                                                              ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}██╗   ██╗ ██████╗ ████████╗${GREEN}                                ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}╚██╗ ██╔╝██╔═══██╗╚══██╔══╝${GREEN}                                ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE} ╚████╔╝ ██║   ██║   ██║${GREEN}                                   ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}  ╚██╔╝  ██║   ██║   ██║${GREEN}                                   ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}   ██║   ╚██████╔╝   ██║${GREEN}                                   ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}   ╚═╝    ╚═════╝    ╚═╝${GREEN}                                   ║${NC}"
    echo -e "${GREEN}  ║                                                              ║${NC}"
    echo -e "${GREEN}  ║      ${CYAN}YUKIOH OKAMI TOOL INSTALLER v2.0${GREEN}                        ║${NC}"
    echo -e "${GREEN}  ║      ${DIM}PUBG / BGMI PAK MODDING TOOL SETUP${GREEN}                      ║${NC}"
    echo -e "${GREEN}  ╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

section() {
    echo
    echo -e "  ${BLUE}┌─────────────────────────────────────┐${NC}"
    echo -e "  ${BLUE}│${NC}  ${BOLD}${WHITE}$1${NC}"
    echo -e "  ${BLUE}└─────────────────────────────────────┘${NC}"
}

log_ok()   { echo -e "  ${GREEN}[✔]${NC}  $1"; }
log_info() { echo -e "  ${CYAN}[➤]${NC}  $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC}  $1"; }
log_err()  { echo -e "  ${RED}[✘]${NC}  $1"; }
divider()  { echo -e "  ${DIM}──────────────────────────────────────${NC}"; }

print_final_box() {
    echo
    echo -e "${GREEN}  ╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${YELLOW}✔  YUKIOH OKAMI TOOL INSTALLED!${GREEN}        ║${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ╠══════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}HOW TO RUN:${GREEN}                            ║${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${CYAN}❯  Yukioh_Okami_Tool${GREEN}                   ║${NC}"
    echo -e "${GREEN}  ║   ${CYAN}❯  python Yukioh_Okami.py${GREEN}              ║${NC}"
    echo -e "${GREEN}  ╠══════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}INSTALLED AT:${GREEN}                          ║${NC}"
    echo -e "${GREEN}  ║   ${DIM}~/Yukioh_Okami_Tool/${NC}${GREEN}                   ║${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}GLOBAL CMD:${GREEN}                            ║${NC}"
    echo -e "${GREEN}  ║   ${DIM}\$PREFIX/bin/Yukioh_Okami_Tool${NC}${GREEN}          ║${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ╠══════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ║   ${RED}⚠  Do NOT run via curl | bash${GREEN}          ║${NC}"
    echo -e "${GREEN}  ║   ${DIM}Interactive login required${NC}${GREEN}             ║${NC}"
    echo -e "${GREEN}  ║                                          ║${NC}"
    echo -e "${GREEN}  ╚══════════════════════════════════════════╝${NC}"
    echo
}

# ═══════════════════════════════════════════

print_banner
sleep 0.5

section "SYSTEM UPDATE"

log_info "Updating Termux packages..."

pkg update -y && pkg upgrade -y &>/dev/null &
spinner $! "Updating packages..."

log_ok "System packages updated"

# ─── STEP 1: PYTHON CHECK ───────────────────────────────────
section "STEP 1/6 — PYTHON CHECK"

if ! command -v python &>/dev/null; then
    log_info "Python not found. Installing..."
    pkg install python python-pip -y &>/dev/null
fi

PY_VER=$(python --version 2>&1 | awk '{print $2}')
log_ok "Python ${BOLD}$PY_VER${NC} found"
progress_bar 1 6 "Python verified"
sleep 0.3

# ─── STEP 2: PIP SETUP ──────────────────────────────────────
section "STEP 2/6 — PIP SETUP"

if ! command -v pip &>/dev/null; then
    log_info "Installing pip..."
    python -m ensurepip --upgrade &>/dev/null &
    spinner $! "Installing pip..."
fi

PIP_VER=$(pip --version 2>&1 | awk '{print $2}')
log_info "Upgrading pip..."
pip install --upgrade pip &>/dev/null &
spinner $! "Upgrading pip..."
log_ok "pip ${BOLD}$PIP_VER${NC} ready"
progress_bar 2 6 "pip ready"
sleep 0.3

# ─── STEP 3: BUILD TOOLS ────────────────────────────────────
section "STEP 3/6 — BUILD TOOLS"

if ! command -v git &>/dev/null; then
    log_info "Installing git + build deps..."
    (pkg install git clang libffi openssl -y 2>/dev/null || \
     apt install git -y 2>/dev/null) &
    spinner $! "Installing build tools..."
else
    log_info "Installing build deps (clang, libffi, openssl)..."
    pkg install clang libffi openssl -y &>/dev/null &
    spinner $! "Installing build deps..."
fi

GIT_VER=$(git --version 2>&1 | awk '{print $3}')
log_ok "git ${BOLD}$GIT_VER${NC} ready"
progress_bar 3 6 "Build tools ready"
sleep 0.3

# ─── STEP 4: PYTHON MODULES ─────────────────────────────────
section "STEP 4/6 — PYTHON MODULES"

MODULES=(
    gmalg
    pycryptodome
    zstandard
    rich
    requests
    colorama
    pyfiglet
    zstd
)

TOTAL=${#MODULES[@]}

for mod in "${MODULES[@]}"; do
    printf "  ${CYAN}[➤]${NC}  Installing ${BOLD}%-16s${NC} " "$mod..."
    pip install "$mod" &>/dev/null &
    PID=$!
    sp='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    i=0
    while kill -0 $PID 2>/dev/null; do
        printf "\b${CYAN}${sp:$i:1}${NC}"
        i=$(( (i+1) % 10 ))
        sleep 0.07
    done
    wait $PID && printf "\b${GREEN}✔${NC}\n" || {
        printf "\b${RED}✘${NC}\n"
        log_err "Failed: $mod"
        exit 1
    }
done

divider
log_ok "All ${BOLD}$TOTAL${NC} modules installed"
progress_bar 4 6 "Modules ready"
sleep 0.3

# ─── STEP 5: CLONE REPO ─────────────────────────────────────
section "STEP 5/6 — CLONE REPO"

if [ -d "$HOME/Yukioh_Okami_Tool" ]; then
    log_warn "Old Yukioh_Okami_Tool found"
    log_info "Deleting old folder..."
    rm -rf "$HOME/Yukioh_Okami_Tool" &
    spinner $! "Removing old tool..."
    wait $!
    log_ok "Old tool deleted"
fi

log_info "Cloning Yukioh_Okami_Tool..."

git clone https://github.com/Himesh-Shah93/Yukioh_Okami_Tool "$HOME/Yukioh_Okami_Tool" 2>&1 | \
while IFS= read -r line; do
    echo -e "  ${DIM}$line${NC}"
done

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_err "Git clone failed! Check internet or GitHub URL."
    exit 1
fi

log_ok "Tool ready at ${CYAN}~/Yukioh_Okami_Tool${NC}"
cd "$HOME/Yukioh_Okami_Tool" || exit 1
chmod +x *
log_ok "Executable permissions set"
progress_bar 5 6 "Repo cloned"
sleep 0.3

# ─── STEP 6: GLOBAL COMMAND ─────────────────────────────────
section "STEP 6/6 — GLOBAL COMMAND"

CMD_PATH="${PREFIX:-/usr/local}/bin/Yukioh_Okami_Tool"

cat > "$CMD_PATH" << 'CMDEOF'
#!/bin/bash

cd "$HOME/Yukioh_Okami_Tool" || exit 1

if [ -f "Yukioh_Okami.py" ]; then
    python Yukioh_Okami.py
elif [ -f "Yukioh_Okami_Tool" ]; then
    ./Yukioh_Okami_Tool
else
    echo "Tool entry file not found!"
    exit 1
fi
CMDEOF

chmod +x "$CMD_PATH"
log_ok "Global command created: ${CYAN}Yukioh_Okami_Tool${NC}"
progress_bar 6 6 "Installation complete"
sleep 0.3

# ─── DONE ───────────────────────────────────────────────────
print_final_box
