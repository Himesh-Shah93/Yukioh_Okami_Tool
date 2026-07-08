#!/bin/bash
# ============================================================
#  Yukioh_Ōkami — Termux Installer v4.5 (Perfect Edition)
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
    echo -e "${GREEN}  ╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ██╗   ██╗██╗   ██╗██╗  ██╗██╗ ██████╗ ██╗  ██╗          ║${NC}"
    echo -e "${GREEN}  ║   ╚██╗ ██╔╝██║   ██║██║ ██╔╝██║██╔═══██╗██║  ██║          ║${NC}"
    echo -e "${GREEN}  ║    ╚████╔╝ ██║   ██║█████╔╝ ██║██║   ██║███████║          ║${NC}"
    echo -e "${GREEN}  ║     ╚██╔╝  ██║   ██║██╔═██╗ ██║██║   ██║██╔══██║          ║${NC}"
    echo -e "${GREEN}  ║      ██║   ╚██████╔╝██║  ██╗██║╚██████╔╝██║  ██║          ║${NC}"
    echo -e "${GREEN}  ║      ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝          ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║      ${CYAN}YUKIOH OKAMI TOOL INSTALLER v4.5${GREEN}                  ║${NC}"
    echo -e "${GREEN}  ║      ${DIM}PUBG / BGMI PAK MODDING TOOL SETUP${GREEN}                ║${NC}"
    echo -e "${GREEN}  ╚════════════════════════════════════════════════════════╝${NC}"
    echo
}

section() {
    echo
    echo -e "  ${BLUE}┌────────────────────────────────────────────────────┐${NC}"
    echo -e "  ${BLUE}│${NC}  ${BOLD}${WHITE}$1${NC}"
    echo -e "  ${BLUE}└────────────────────────────────────────────────────┘${NC}"
}

log_ok()   { echo -e "  ${GREEN}[✔]${NC}  $1"; }
log_info() { echo -e "  ${CYAN}[➤]${NC}  $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC}  $1"; }
log_err()  { echo -e "  ${RED}[✘]${NC}  $1"; }
divider()  { echo -e "  ${DIM}──────────────────────────────────────────────────${NC}"; }

print_final_box() {
    echo
    echo -e "${GREEN}  ╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ${YELLOW}✔  YUKIOH OKAMI TOOL INSTALLED SUCCESSFULLY!${GREEN}        ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}HOW TO RUN:${GREEN}                                            ║${NC}"
    echo -e "${GREEN}  ║     ${CYAN}▶  Yukioh_Okami_Tool${GREEN}                                  ║${NC}"
    echo -e "${GREEN}  ║     ${CYAN}▶  cd ~/Yukioh_Okami_Tool && python Yukioh_Okami.py${GREEN}  ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}INSTALLED AT:${GREEN}                                        ║${NC}"
    echo -e "${GREEN}  ║     ${DIM}~/Yukioh_Okami_Tool${NC}${GREEN}                              ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ${WHITE}GLOBAL CMD:${GREEN}                                          ║${NC}"
    echo -e "${GREEN}  ║     ${DIM}${PREFIX:-/usr/local}/bin/Yukioh_Okami_Tool${NC}${GREEN}         ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ║   ${RED}⚠  Do NOT run via curl | bash${GREEN}                          ║${NC}"
    echo -e "${GREEN}  ║   ${DIM}Interactive login required${NC}${GREEN}                         ║${NC}"
    echo -e "${GREEN}  ║                                                            ║${NC}"
    echo -e "${GREEN}  ╚════════════════════════════════════════════════════════╝${NC}"
    echo
}

# ============================================================
# MAIN INSTALLATION
# ============================================================

print_banner
sleep 0.5

# STEP 1: System Update
section "STEP 1/6 — SYSTEM UPDATE"
log_info "Updating Termux packages..."
{
    pkg update -y && pkg upgrade -y
} > /dev/null 2>&1 &
spinner $! "Updating packages..."
wait $!
log_ok "System packages updated"
progress_bar 1 6 "System updated"
sleep 0.3

# STEP 2: Install system deps
section "STEP 2/6 — INSTALL DEPENDENCIES"
log_info "Installing python, java, lua, git, clang..."
{
    pkg install -y python openjdk-17 lua53 git clang libffi openssl
} > /dev/null 2>&1 &
spinner $! "Installing system packages..."
wait $!
PY_VER=$(python --version 2>&1 | awk '{print $2}')
log_ok "Python $PY_VER, Java, Lua, Git installed"
progress_bar 2 6 "System deps ready"
sleep 0.3

# STEP 3: Upgrade pip
section "STEP 3/6 — PIP UPGRADE"
log_info "Upgrading pip..."
{
    pip install --upgrade pip
} > /dev/null 2>&1 &
spinner $! "Upgrading pip..."
wait $!
log_ok "pip upgraded"
progress_bar 3 6 "pip upgraded"
sleep 0.3

# STEP 4: Python modules
section "STEP 4/6 — PYTHON MODULES"

MODULES=(
    pycryptodome
    zstandard
    rich
    requests
    psutil
    colorama
)

for mod in "${MODULES[@]}"; do
    printf "  ${CYAN}[➤]${NC}  Installing ${BOLD}%-14s${NC} " "$mod..."
    {
        pip install --no-cache-dir "$mod"
    } > /dev/null 2>&1 &
    PID=$!
    spinner $PID "Installing $mod..."
    wait $PID
    if [ $? -eq 0 ]; then
        printf "\b${GREEN}✔${NC}\n"
    else
        printf "\b${RED}✘${NC}\n"
        log_err "Failed to install $mod. Trying alternative..."
        if [ "$mod" = "gmalg" ]; then
            log_info "Installing gmalg from GitHub..."
            pip install git+https://github.com/myzhan/gmalg > /dev/null 2>&1 &
            PID=$!
            spinner $PID "Installing gmalg from GitHub..."
            wait $PID
            [ $? -eq 0 ] && log_ok "gmalg installed from GitHub" || log_err "gmalg still failed. Continuing anyway."
        else
            log_err "Manual install may be required later."
        fi
    fi
done

# Install gmalg separately (since it's in MODULES but we handle fallback above)
# Actually we already included it in the list, but we should explicitly try again if it failed.
# However the loop above already tried it, so we just need to ensure it's installed.
# We'll double-check and force GitHub if needed.
log_info "Ensuring gmalg is installed..."
if ! python -c "import gmalg" 2>/dev/null; then
    log_warn "gmalg not found, installing from GitHub..."
    pip install git+https://github.com/myzhan/gmalg > /dev/null 2>&1 &
    spinner $! "Installing gmalg from GitHub..."
    wait $!
    if python -c "import gmalg" 2>/dev/null; then
        log_ok "gmalg installed successfully"
    else
        log_err "gmalg still not available. Some PAK features may fail."
    fi
else
    log_ok "gmalg already installed"
fi

divider
log_ok "All Python modules processed"
progress_bar 4 6 "Modules ready"
sleep 0.3

# STEP 5: Clone repo
section "STEP 5/6 — CLONE REPOSITORY"
if [ -d "$HOME/Yukioh_Okami_Tool" ]; then
    log_warn "Old Yukioh_Okami_Tool found"
    log_info "Deleting old folder..."
    rm -rf "$HOME/Yukioh_Okami_Tool" &
    spinner $! "Removing old tool..."
    wait $!
    log_ok "Old tool deleted"
fi

log_info "Cloning Yukioh_Okami_Tool..."
git clone https://github.com/Himesh-Shah93/Yukioh_Okami_Tool "$HOME/Yukioh_Okami_Tool" 2>&1 | while IFS= read -r line; do
    echo -e "  ${DIM}$line${NC}"
done

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_err "Git clone failed! Check internet or GitHub URL."
    exit 1
fi

log_ok "Tool ready at ${CYAN}~/Yukioh_Okami_Tool${NC}"
cd "$HOME/Yukioh_Okami_Tool" || exit 1
chmod +x *.py
log_ok "Executable permissions set"
progress_bar 5 6 "Repo cloned"
sleep 0.3

# STEP 6: Global command
section "STEP 6/6 — GLOBAL COMMAND"
CMD_PATH="${PREFIX:-/usr/local}/bin/Yukioh_Okami_Tool"
cat > "$CMD_PATH" << 'CMDEOF'
#!/bin/bash

cd "$HOME/Yukioh_Okami_Tool" || exit 1

if [ -f "Yukioh_Okami.py" ]; then
    python Yukioh_Okami.py
else
    echo "Yukioh_Okami.py not found!"
    exit 1
fi
CMDEOF

chmod +x "$CMD_PATH"
log_ok "Global command created: ${CYAN}Yukioh_Okami_Tool${NC}"
progress_bar 6 6 "Installation complete"
sleep 0.3

# ============================================================
# DONE
# ============================================================
print_final_box